"""Notification API endpoints."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.config.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkReadRequest,
    NotificationStatsResponse,
)
from app.websocket.handlers import broadcast_notification
from app.config.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List notifications for the current user."""
    # Build query
    query = select(Notification).where(
        Notification.user_id == current_user.id,
        Notification.organization_id == current_user.organization_id,
    )

    if unread_only:
        query = query.where(Notification.is_read == False)

    if type:
        query = query.where(Notification.type == type)

    if priority:
        query = query.where(Notification.priority == priority)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Get unread count
    unread_query = select(func.count()).where(
        Notification.user_id == current_user.id,
        Notification.organization_id == current_user.organization_id,
        Notification.is_read == False,
    )
    unread_count = (await db.execute(unread_query)).scalar() or 0

    # Get paginated results
    query = query.order_by(Notification.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    notifications = result.scalars().all()

    return NotificationListResponse(
        items=[
            NotificationResponse(
                id=str(n.id),
                organization_id=str(n.organization_id),
                user_id=str(n.user_id),
                title=n.title,
                message=n.message,
                type=n.type,
                priority=n.priority,
                is_read=n.is_read,
                read_at=n.read_at,
                action_url=n.action_url,
                action_label=n.action_label,
                related_entity_type=n.related_entity_type,
                related_entity_id=n.related_entity_id,
                expires_at=n.expires_at,
                created_at=n.created_at,
                updated_at=n.updated_at,
            )
            for n in notifications
        ],
        total=total,
        page=page,
        page_size=page_size,
        unread_count=unread_count,
    )


@router.get("/stats", response_model=NotificationStatsResponse)
async def get_notification_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get notification statistics for the current user."""
    base_filter = and_(
        Notification.user_id == current_user.id,
        Notification.organization_id == current_user.organization_id,
    )

    # Total count
    total_query = select(func.count()).where(base_filter)
    total = (await db.execute(total_query)).scalar() or 0

    # Unread count
    unread_query = select(func.count()).where(base_filter, Notification.is_read == False)
    unread = (await db.execute(unread_query)).scalar() or 0

    # Count by type
    type_query = select(Notification.type, func.count()).where(base_filter).group_by(Notification.type)
    type_result = await db.execute(type_query)
    by_type = {str(t[0]): t[1] for t in type_result.fetchall()}

    # Count by priority
    priority_query = select(Notification.priority, func.count()).where(base_filter).group_by(Notification.priority)
    priority_result = await db.execute(priority_query)
    by_priority = {str(p[0]): p[1] for p in priority_result.fetchall()}

    return NotificationStatsResponse(
        total=total,
        unread=unread,
        by_type=by_type,
        by_priority=by_priority,
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific notification."""
    query = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    )
    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return NotificationResponse(
        id=str(notification.id),
        organization_id=str(notification.organization_id),
        user_id=str(notification.user_id),
        title=notification.title,
        message=notification.message,
        type=notification.type,
        priority=notification.priority,
        is_read=notification.is_read,
        read_at=notification.read_at,
        action_url=notification.action_url,
        action_label=notification.action_label,
        related_entity_type=notification.related_entity_type,
        related_entity_id=notification.related_entity_id,
        expires_at=notification.expires_at,
        created_at=notification.created_at,
        updated_at=notification.updated_at,
    )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as read."""
    query = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    )
    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    notification.read_at = datetime.utcnow()
    await db.commit()
    await db.refresh(notification)

    return NotificationResponse.model_validate(notification)


@router.post("/mark-read", status_code=status.HTTP_200_OK)
async def mark_multiple_read(
    request: NotificationMarkReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark multiple notifications as read."""
    query = select(Notification).where(
        Notification.id.in_(request.notification_ids),
        Notification.user_id == current_user.id,
    )
    result = await db.execute(query)
    notifications = result.scalars().all()

    now = datetime.utcnow()
    for notification in notifications:
        notification.is_read = True
        notification.read_at = now

    await db.commit()

    return {"marked_read": len(notifications)}


@router.post("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read."""
    query = select(Notification).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    )
    result = await db.execute(query)
    notifications = result.scalars().all()

    now = datetime.utcnow()
    for notification in notifications:
        notification.is_read = True
        notification.read_at = now

    await db.commit()

    return {"marked_read": len(notifications)}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a notification."""
    query = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    )
    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    await db.delete(notification)
    await db.commit()


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a notification (admin only)."""
    if current_user.role not in ["admin", "operator"]:
        raise HTTPException(status_code=403, detail="Not authorized to create notifications")

    notification = Notification(
        organization_id=current_user.organization_id,
        **notification_data.model_dump(),
    )

    db.add(notification)
    await db.commit()
    await db.refresh(notification)

    # Broadcast via WebSocket
    try:
        await broadcast_notification(
            notification_data.user_id,
            {
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "priority": notification.priority,
            }
        )
    except Exception as e:
        logger.warning(f"Failed to broadcast notification: {e}")

    return NotificationResponse.model_validate(notification)
