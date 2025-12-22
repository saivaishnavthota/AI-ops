"""Audit log API endpoints."""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.config.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.audit_log import (
    AuditLogResponse,
    AuditLogListResponse,
    AuditLogStatsResponse,
)
from app.config.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List audit logs for the organization."""
    # Only admins and operators can view audit logs
    if current_user.role not in ["admin", "operator"]:
        raise HTTPException(status_code=403, detail="Not authorized to view audit logs")

    # Build query
    query = select(AuditLog).where(
        AuditLog.organization_id == current_user.organization_id
    ).options(joinedload(AuditLog.user))

    if action:
        query = query.where(AuditLog.action == action)

    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)

    if resource_id:
        query = query.where(AuditLog.resource_id == resource_id)

    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    if status:
        query = query.where(AuditLog.status == status)

    if start_date:
        query = query.where(AuditLog.created_at >= start_date)

    if end_date:
        query = query.where(AuditLog.created_at <= end_date)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Get paginated results
    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.unique().scalars().all()

    # Build response with user info
    items = []
    for log in logs:
        log_dict = {
            "id": str(log.id),
            "organization_id": str(log.organization_id),
            "user_id": str(log.user_id) if log.user_id else None,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "resource_name": getattr(log, 'resource_name', None),
            "description": log.description,
            "changes": log.changes,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "request_id": getattr(log, 'request_id', None),
            "status": getattr(log, 'status', 'success'),
            "error_message": getattr(log, 'error_message', None),
            "created_at": log.created_at,
            "user_email": log.user.email if log.user else None,
            "user_name": f"{log.user.first_name} {log.user.last_name}" if log.user else None,
        }
        items.append(AuditLogResponse(**log_dict))

    return AuditLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=AuditLogStatsResponse)
async def get_audit_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get audit log statistics."""
    if current_user.role not in ["admin", "operator"]:
        raise HTTPException(status_code=403, detail="Not authorized to view audit logs")

    org_filter = AuditLog.organization_id == current_user.organization_id
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    # Total actions
    total_query = select(func.count()).where(org_filter)
    total_actions = (await db.execute(total_query)).scalar() or 0

    # Actions today
    today_query = select(func.count()).where(
        org_filter,
        AuditLog.created_at >= today_start,
    )
    actions_today = (await db.execute(today_query)).scalar() or 0

    # Actions this week
    week_query = select(func.count()).where(
        org_filter,
        AuditLog.created_at >= week_start,
    )
    actions_this_week = (await db.execute(week_query)).scalar() or 0

    # Count by action
    action_query = select(AuditLog.action, func.count()).where(org_filter).group_by(AuditLog.action)
    action_result = await db.execute(action_query)
    by_action = {str(a[0]): a[1] for a in action_result.fetchall()}

    # Count by resource type
    resource_query = select(AuditLog.resource_type, func.count()).where(org_filter).group_by(AuditLog.resource_type)
    resource_result = await db.execute(resource_query)
    by_resource_type = {r[0]: r[1] for r in resource_result.fetchall()}

    # Top users by activity
    user_query = (
        select(AuditLog.user_id, func.count().label("count"))
        .where(org_filter, AuditLog.user_id.isnot(None))
        .group_by(AuditLog.user_id)
        .order_by(func.count().desc())
        .limit(10)
    )
    user_result = await db.execute(user_query)
    by_user = [{"user_id": str(u[0]), "count": u[1]} for u in user_result.fetchall()]

    # Recent activity
    recent_query = (
        select(AuditLog)
        .where(org_filter)
        .options(joinedload(AuditLog.user))
        .order_by(AuditLog.created_at.desc())
        .limit(10)
    )
    recent_result = await db.execute(recent_query)
    recent_logs = recent_result.unique().scalars().all()

    recent_activity = []
    for log in recent_logs:
        log_dict = {
            "id": str(log.id),
            "organization_id": str(log.organization_id),
            "user_id": str(log.user_id) if log.user_id else None,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "resource_name": getattr(log, 'resource_name', None),
            "description": log.description,
            "changes": log.changes,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "request_id": getattr(log, 'request_id', None),
            "status": getattr(log, 'status', 'success'),
            "error_message": getattr(log, 'error_message', None),
            "created_at": log.created_at,
            "user_email": log.user.email if log.user else None,
            "user_name": f"{log.user.first_name} {log.user.last_name}" if log.user else None,
        }
        recent_activity.append(AuditLogResponse(**log_dict))

    return AuditLogStatsResponse(
        total_actions=total_actions,
        actions_today=actions_today,
        actions_this_week=actions_this_week,
        by_action=by_action,
        by_resource_type=by_resource_type,
        by_user=by_user,
        recent_activity=recent_activity,
    )


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific audit log entry."""
    if current_user.role not in ["admin", "operator"]:
        raise HTTPException(status_code=403, detail="Not authorized to view audit logs")

    query = select(AuditLog).where(
        AuditLog.id == log_id,
        AuditLog.organization_id == current_user.organization_id,
    ).options(joinedload(AuditLog.user))

    result = await db.execute(query)
    log = result.unique().scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")

    log_dict = {
        "id": str(log.id),
        "organization_id": str(log.organization_id),
        "user_id": str(log.user_id) if log.user_id else None,
        "action": log.action,
        "resource_type": log.resource_type,
        "resource_id": log.resource_id,
        "resource_name": getattr(log, 'resource_name', None),
        "description": log.description,
        "changes": log.changes,
        "ip_address": log.ip_address,
        "user_agent": log.user_agent,
        "request_id": getattr(log, 'request_id', None),
        "status": getattr(log, 'status', 'success'),
        "error_message": getattr(log, 'error_message', None),
        "created_at": log.created_at,
        "user_email": log.user.email if log.user else None,
        "user_name": f"{log.user.first_name} {log.user.last_name}" if log.user else None,
    }

    return AuditLogResponse(**log_dict)


@router.get("/resource/{resource_type}/{resource_id}", response_model=AuditLogListResponse)
async def get_resource_audit_trail(
    resource_type: str,
    resource_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get audit trail for a specific resource."""
    if current_user.role not in ["admin", "operator"]:
        raise HTTPException(status_code=403, detail="Not authorized to view audit logs")

    query = select(AuditLog).where(
        AuditLog.organization_id == current_user.organization_id,
        AuditLog.resource_type == resource_type,
        AuditLog.resource_id == resource_id,
    ).options(joinedload(AuditLog.user))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Get paginated results
    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.unique().scalars().all()

    items = []
    for log in logs:
        log_dict = {
            "id": str(log.id),
            "organization_id": str(log.organization_id),
            "user_id": str(log.user_id) if log.user_id else None,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "resource_name": getattr(log, 'resource_name', None),
            "description": log.description,
            "changes": log.changes,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "request_id": getattr(log, 'request_id', None),
            "status": getattr(log, 'status', 'success'),
            "error_message": getattr(log, 'error_message', None),
            "created_at": log.created_at,
            "user_email": log.user.email if log.user else None,
            "user_name": f"{log.user.first_name} {log.user.last_name}" if log.user else None,
        }
        items.append(AuditLogResponse(**log_dict))

    return AuditLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
