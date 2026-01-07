"""Notification service for creating and managing notifications."""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.notification import Notification, NotificationType, NotificationPriority
from app.models.user import User
from app.models.ticket import Ticket
from app.models.incident import Incident
from app.models.alert import Alert
from app.websocket.handlers import broadcast_notification
from app.config.logging import get_logger

logger = get_logger(__name__)


class NotificationService:
    """Service for creating and managing notifications."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        user_id: UUID,
        organization_id: UUID,
        title: str,
        message: str,
        type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=user_id,
            organization_id=organization_id,
            title=title,
            message=message,
            type=type.value,
            priority=priority.value,
            action_url=action_url,
            action_label=action_label,
            related_entity_type=related_entity_type,
            related_entity_id=str(related_entity_id) if related_entity_id else None,
            expires_at=expires_at,
        )

        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)

        # Broadcast via WebSocket
        try:
            await broadcast_notification(
                str(user_id),
                {
                    "id": str(notification.id),
                    "title": notification.title,
                    "message": notification.message,
                    "type": notification.type,
                    "priority": notification.priority,
                    "action_url": notification.action_url,
                    "action_label": notification.action_label,
                }
            )
        except Exception as e:
            logger.warning(f"Failed to broadcast notification: {e}")

        return notification

    async def notify_ticket_assignment(
        self,
        ticket: Ticket,
        assignee: User,
        assigned_by: User,
    ) -> Notification:
        """Create notification for ticket assignment."""
        return await self.create_notification(
            user_id=assignee.id,
            organization_id=assignee.organization_id,
            title="New Ticket Assigned",
            message=f"Ticket #{ticket.ticket_number}: {ticket.subject} has been assigned to you by {assigned_by.full_name}",
            type=NotificationType.INFO,
            priority=NotificationPriority.MEDIUM,
            action_url=f"/tickets/{ticket.id}",
            action_label="View Ticket",
            related_entity_type="ticket",
            related_entity_id=ticket.id,
        )

    async def notify_incident_assignment(
        self,
        incident: Incident,
        assignee: User,
        assigned_by: User,
    ) -> Notification:
        """Create notification for incident assignment."""
        return await self.create_notification(
            user_id=assignee.id,
            organization_id=assignee.organization_id,
            title="New Incident Assigned",
            message=f"Incident #{incident.incident_number}: {incident.title} has been assigned to you by {assigned_by.full_name}",
            type=NotificationType.ALERT,
            priority=NotificationPriority.HIGH,
            action_url=f"/incidents/{incident.id}",
            action_label="View Incident",
            related_entity_type="incident",
            related_entity_id=incident.id,
        )

    async def notify_alert_escalation(
        self,
        alert: Alert,
        user: User,
    ) -> Notification:
        """Create notification for alert escalation."""
        return await self.create_notification(
            user_id=user.id,
            organization_id=user.organization_id,
            title="Alert Escalated",
            message=f"Alert: {alert.title} has been escalated and requires immediate attention",
            type=NotificationType.WARNING,
            priority=NotificationPriority.HIGH,
            action_url=f"/alerts/{alert.id}",
            action_label="View Alert",
            related_entity_type="alert",
            related_entity_id=alert.id,
        )

    async def notify_team_members(
        self,
        team_member_ids: List[UUID],
        organization_id: UUID,
        title: str,
        message: str,
        type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
    ) -> List[Notification]:
        """Create notifications for multiple team members."""
        notifications = []
        
        for user_id in team_member_ids:
            notification = await self.create_notification(
                user_id=user_id,
                organization_id=organization_id,
                title=title,
                message=message,
                type=type,
                priority=priority,
                action_url=action_url,
                action_label=action_label,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
            )
            notifications.append(notification)
        
        return notifications

    async def notify_system_maintenance(
        self,
        organization_id: UUID,
        title: str,
        message: str,
        scheduled_time: Optional[datetime] = None,
    ) -> List[Notification]:
        """Create system maintenance notifications for all users in organization."""
        # Get all active users in the organization
        result = await self.db.execute(
            select(User).where(
                User.organization_id == organization_id,
                User.is_active == True
            )
        )
        users = result.scalars().all()

        notifications = []
        for user in users:
            notification = await self.create_notification(
                user_id=user.id,
                organization_id=organization_id,
                title=title,
                message=message,
                type=NotificationType.SYSTEM,
                priority=NotificationPriority.MEDIUM,
                expires_at=scheduled_time,
            )
            notifications.append(notification)

        return notifications

    async def mark_notifications_read(
        self,
        notification_ids: List[UUID],
        user_id: UUID,
    ) -> int:
        """Mark multiple notifications as read."""
        result = await self.db.execute(
            select(Notification).where(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        )
        notifications = result.scalars().all()

        count = 0
        now = datetime.now(timezone.utc)
        for notification in notifications:
            notification.is_read = True
            notification.read_at = now
            count += 1

        await self.db.commit()
        return count