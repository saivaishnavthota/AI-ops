from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, func, select
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.api.v1.deps import CurrentUser, DBSession
from app.models.security import SecurityEvent
from app.schemas.security import (
    SecurityEventCreate,
    SecurityEventUpdate,
    SecurityEventResponse,
    SecurityEventListResponse,
    SecurityEventStatsResponse,
)

router = APIRouter(prefix="/security-events", tags=["Security"])


@router.get("", response_model=SecurityEventListResponse)
async def list_security_events(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    severity: Optional[str] = None,
    status: Optional[str] = None,
):
    """List all security events for the organization."""
    query = select(SecurityEvent).where(
        SecurityEvent.organization_id == current_user.organization_id
    )
    
    if severity:
        query = query.where(SecurityEvent.severity == severity)
    if status:
        query = query.where(SecurityEvent.status == status)
    
    # Get total count
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()
    
    # Get events
    result = await db.execute(
        query.order_by(desc(SecurityEvent.created_at)).offset(skip).limit(limit)
    )
    events = result.scalars().all()
    
    return {
        "items": events,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/stats", response_model=SecurityEventStatsResponse)
async def get_security_stats(
    db: DBSession,
    current_user: CurrentUser,
):
    """Get security event statistics."""
    base_query = select(SecurityEvent).where(
        SecurityEvent.organization_id == current_user.organization_id
    )
    
    # Total events
    total_result = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total_events = total_result.scalar()
    
    # Critical count
    critical_result = await db.execute(
        select(func.count()).select_from(
            select(SecurityEvent).where(
                SecurityEvent.organization_id == current_user.organization_id,
                SecurityEvent.severity == "critical",
                SecurityEvent.status != "resolved"
            ).subquery()
        )
    )
    critical_count = critical_result.scalar()
    
    # High count
    high_result = await db.execute(
        select(func.count()).select_from(
            select(SecurityEvent).where(
                SecurityEvent.organization_id == current_user.organization_id,
                SecurityEvent.severity == "high",
                SecurityEvent.status != "resolved"
            ).subquery()
        )
    )
    high_count = high_result.scalar()
    
    # Open count
    open_result = await db.execute(
        select(func.count()).select_from(
            select(SecurityEvent).where(
                SecurityEvent.organization_id == current_user.organization_id,
                SecurityEvent.status.in_(["open", "investigating"])
            ).subquery()
        )
    )
    open_count = open_result.scalar()
    
    # Group by severity
    by_severity = {}
    severity_result = await db.execute(
        select(SecurityEvent.severity, func.count(SecurityEvent.id))
        .where(SecurityEvent.organization_id == current_user.organization_id)
        .group_by(SecurityEvent.severity)
    )
    for severity, count in severity_result.all():
        by_severity[severity] = count
    
    # Group by status
    by_status = {}
    status_result = await db.execute(
        select(SecurityEvent.status, func.count(SecurityEvent.id))
        .where(SecurityEvent.organization_id == current_user.organization_id)
        .group_by(SecurityEvent.status)
    )
    for event_status, count in status_result.all():
        by_status[event_status] = count
    
    # Group by type
    by_type = {}
    type_result = await db.execute(
        select(SecurityEvent.type, func.count(SecurityEvent.id))
        .where(SecurityEvent.organization_id == current_user.organization_id)
        .group_by(SecurityEvent.type)
    )
    for event_type, count in type_result.all():
        by_type[event_type] = count
    
    return {
        "total_events": total_events,
        "critical_count": critical_count,
        "high_count": high_count,
        "open_count": open_count,
        "by_severity": by_severity,
        "by_status": by_status,
        "by_type": by_type,
    }


@router.post("", response_model=SecurityEventResponse, status_code=status.HTTP_201_CREATED)
async def create_security_event(
    event_in: SecurityEventCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Create a new security event."""
    event = SecurityEvent(
        organization_id=current_user.organization_id,
        status="open",
        **event_in.dict(),
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.get("/{event_id}", response_model=SecurityEventResponse)
async def get_security_event(
    event_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Get a specific security event."""
    result = await db.execute(
        select(SecurityEvent).where(
            SecurityEvent.id == event_id,
            SecurityEvent.organization_id == current_user.organization_id,
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security event not found",
        )
    
    return event


@router.put("/{event_id}", response_model=SecurityEventResponse)
async def update_security_event(
    event_id: UUID,
    event_in: SecurityEventUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Update a security event."""
    result = await db.execute(
        select(SecurityEvent).where(
            SecurityEvent.id == event_id,
            SecurityEvent.organization_id == current_user.organization_id,
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security event not found",
        )
    
    update_data = event_in.dict(exclude_unset=True)
    
    # If resolving, set resolved_at and resolved_by
    if update_data.get("status") == "resolved" and event.status != "resolved":
        update_data["resolved_at"] = datetime.now(timezone.utc)
        update_data["resolved_by_id"] = current_user.id
    
    for field, value in update_data.items():
        setattr(event, field, value)
    
    await db.commit()
    await db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_security_event(
    event_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Delete a security event."""
    result = await db.execute(
        select(SecurityEvent).where(
            SecurityEvent.id == event_id,
            SecurityEvent.organization_id == current_user.organization_id,
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security event not found",
        )
    
    await db.delete(event)
    await db.commit()
