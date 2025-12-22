from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
import random
import string

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.incident import Incident, IncidentComment, IncidentTimeline, IncidentStatus
from app.models.user import User
from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentStatistics


class IncidentService:
    """Incident management service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self, incident_id: UUID, organization_id: UUID
    ) -> Optional[Incident]:
        """Get incident by ID."""
        result = await self.db.execute(
            select(Incident).where(
                Incident.id == incident_id,
                Incident.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_number(
        self, incident_number: str, organization_id: UUID
    ) -> Optional[Incident]:
        """Get incident by incident number."""
        result = await self.db.execute(
            select(Incident).where(
                Incident.incident_number == incident_number,
                Incident.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_incidents(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: Optional[List[str]] = None,
        priority: Optional[List[str]] = None,
        severity: Optional[List[str]] = None,
        assigned_team_id: Optional[UUID] = None,
        assigned_user_id: Optional[UUID] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Incident], int]:
        """List incidents with filters and pagination."""
        query = select(Incident).where(Incident.organization_id == organization_id)

        # Apply filters
        if status:
            query = query.where(Incident.status.in_(status))

        if priority:
            query = query.where(Incident.priority.in_(priority))

        if severity:
            query = query.where(Incident.severity.in_(severity))

        if assigned_team_id:
            query = query.where(Incident.assigned_team_id == assigned_team_id)

        if assigned_user_id:
            query = query.where(Incident.assigned_user_id == assigned_user_id)

        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (Incident.title.ilike(search_filter))
                | (Incident.incident_number.ilike(search_filter))
                | (Incident.description.ilike(search_filter))
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(Incident, sort_by, Incident.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        incidents = result.scalars().all()

        return list(incidents), total

    async def create_incident(
        self, organization_id: UUID, data: IncidentCreate, reported_by_id: UUID
    ) -> Incident:
        """Create a new incident."""
        # Generate incident number
        incident_number = await self._generate_incident_number(organization_id)

        incident = Incident(
            organization_id=organization_id,
            incident_number=incident_number,
            title=data.title,
            description=data.description,
            status=IncidentStatus.OPEN.value,
            priority=data.priority or "p3",
            severity=data.severity or "medium",
            impact=data.impact,
            urgency=data.urgency,
            category=data.category,
            subcategory=data.subcategory,
            assigned_team_id=data.assigned_team_id,
            assigned_user_id=data.assigned_user_id,
            reported_by_id=reported_by_id,
            affected_services=data.affected_services or [],
            tags=data.tags or [],
            metadata=data.metadata or {},
        )

        self.db.add(incident)
        await self.db.flush()

        # Create timeline entry
        await self._add_timeline_event(
            incident.id, reported_by_id, "created", "Incident created"
        )

        await self.db.commit()
        await self.db.refresh(incident)

        return incident

    async def update_incident(
        self, incident_id: UUID, organization_id: UUID, data: IncidentUpdate, user_id: UUID
    ) -> Incident:
        """Update an incident."""
        incident = await self.get_by_id(incident_id, organization_id)
        if not incident:
            raise NotFoundError("Incident", incident_id)

        # Track changes for timeline
        changes = {}
        update_data = data.model_dump(exclude_unset=True)

        for field, new_value in update_data.items():
            old_value = getattr(incident, field)
            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}
                setattr(incident, field, new_value)

        if changes:
            await self._add_timeline_event(
                incident.id, user_id, "updated", "Incident updated", changes
            )

        await self.db.commit()
        await self.db.refresh(incident)

        return incident

    async def acknowledge_incident(
        self, incident_id: UUID, organization_id: UUID, user_id: UUID
    ) -> Incident:
        """Acknowledge an incident."""
        incident = await self.get_by_id(incident_id, organization_id)
        if not incident:
            raise NotFoundError("Incident", incident_id)

        if incident.status not in [IncidentStatus.OPEN.value]:
            raise ValidationError("Incident cannot be acknowledged in current status")

        incident.status = IncidentStatus.ACKNOWLEDGED.value
        incident.acknowledged_at = datetime.now(timezone.utc)

        await self._add_timeline_event(
            incident.id, user_id, "acknowledged", "Incident acknowledged"
        )

        await self.db.commit()
        await self.db.refresh(incident)

        return incident

    async def resolve_incident(
        self,
        incident_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        resolution_notes: str,
        root_cause: Optional[str] = None,
    ) -> Incident:
        """Resolve an incident."""
        incident = await self.get_by_id(incident_id, organization_id)
        if not incident:
            raise NotFoundError("Incident", incident_id)

        if incident.status in [IncidentStatus.RESOLVED.value, IncidentStatus.CLOSED.value]:
            raise ValidationError("Incident is already resolved or closed")

        incident.status = IncidentStatus.RESOLVED.value
        incident.resolved_at = datetime.now(timezone.utc)
        incident.resolution_notes = resolution_notes
        if root_cause:
            incident.root_cause = root_cause

        await self._add_timeline_event(
            incident.id, user_id, "resolved", f"Incident resolved: {resolution_notes}"
        )

        await self.db.commit()
        await self.db.refresh(incident)

        return incident

    async def close_incident(
        self, incident_id: UUID, organization_id: UUID, user_id: UUID
    ) -> Incident:
        """Close an incident."""
        incident = await self.get_by_id(incident_id, organization_id)
        if not incident:
            raise NotFoundError("Incident", incident_id)

        if incident.status != IncidentStatus.RESOLVED.value:
            raise ValidationError("Only resolved incidents can be closed")

        incident.status = IncidentStatus.CLOSED.value
        incident.closed_at = datetime.now(timezone.utc)

        await self._add_timeline_event(
            incident.id, user_id, "closed", "Incident closed"
        )

        await self.db.commit()
        await self.db.refresh(incident)

        return incident

    async def assign_incident(
        self,
        incident_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        assigned_team_id: Optional[UUID] = None,
        assigned_user_id: Optional[UUID] = None,
    ) -> Incident:
        """Assign incident to team/user."""
        incident = await self.get_by_id(incident_id, organization_id)
        if not incident:
            raise NotFoundError("Incident", incident_id)

        changes = {}

        if assigned_team_id is not None:
            changes["assigned_team_id"] = {
                "old": str(incident.assigned_team_id) if incident.assigned_team_id else None,
                "new": str(assigned_team_id) if assigned_team_id else None,
            }
            incident.assigned_team_id = assigned_team_id

        if assigned_user_id is not None:
            changes["assigned_user_id"] = {
                "old": str(incident.assigned_user_id) if incident.assigned_user_id else None,
                "new": str(assigned_user_id) if assigned_user_id else None,
            }
            incident.assigned_user_id = assigned_user_id

        if changes:
            await self._add_timeline_event(
                incident.id, user_id, "assigned", "Incident assignment updated", changes
            )

        await self.db.commit()
        await self.db.refresh(incident)

        return incident

    async def add_comment(
        self,
        incident_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        content: str,
        is_internal: bool = False,
        attachments: Optional[List[Dict[str, str]]] = None,
    ) -> IncidentComment:
        """Add a comment to an incident."""
        incident = await self.get_by_id(incident_id, organization_id)
        if not incident:
            raise NotFoundError("Incident", incident_id)

        comment = IncidentComment(
            incident_id=incident_id,
            user_id=user_id,
            content=content,
            is_internal=is_internal,
            attachments=attachments or [],
        )

        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)

        return comment

    async def get_comments(
        self, incident_id: UUID, organization_id: UUID
    ) -> List[IncidentComment]:
        """Get all comments for an incident."""
        # Verify incident exists
        incident = await self.get_by_id(incident_id, organization_id)
        if not incident:
            raise NotFoundError("Incident", incident_id)

        result = await self.db.execute(
            select(IncidentComment)
            .where(IncidentComment.incident_id == incident_id)
            .order_by(IncidentComment.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_timeline(
        self, incident_id: UUID, organization_id: UUID
    ) -> List[IncidentTimeline]:
        """Get timeline for an incident."""
        incident = await self.get_by_id(incident_id, organization_id)
        if not incident:
            raise NotFoundError("Incident", incident_id)

        result = await self.db.execute(
            select(IncidentTimeline)
            .where(IncidentTimeline.incident_id == incident_id)
            .order_by(IncidentTimeline.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_statistics(self, organization_id: UUID) -> IncidentStatistics:
        """Get incident statistics for an organization."""
        base_query = select(Incident).where(Incident.organization_id == organization_id)

        # Total count
        total_result = await self.db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = total_result.scalar() or 0

        # Count by status
        status_counts = {}
        for status in IncidentStatus:
            result = await self.db.execute(
                select(func.count()).where(
                    Incident.organization_id == organization_id,
                    Incident.status == status.value,
                )
            )
            status_counts[status.value] = result.scalar() or 0

        # Count by priority
        priority_result = await self.db.execute(
            select(Incident.priority, func.count())
            .where(Incident.organization_id == organization_id)
            .group_by(Incident.priority)
        )
        by_priority = dict(priority_result.all())

        # Count by severity
        severity_result = await self.db.execute(
            select(Incident.severity, func.count())
            .where(Incident.organization_id == organization_id)
            .group_by(Incident.severity)
        )
        by_severity = dict(severity_result.all())

        # Count by category
        category_result = await self.db.execute(
            select(Incident.category, func.count())
            .where(
                Incident.organization_id == organization_id,
                Incident.category.isnot(None),
            )
            .group_by(Incident.category)
        )
        by_category = dict(category_result.all())

        return IncidentStatistics(
            total=total,
            open=status_counts.get("open", 0),
            acknowledged=status_counts.get("acknowledged", 0),
            in_progress=status_counts.get("in_progress", 0),
            resolved=status_counts.get("resolved", 0),
            closed=status_counts.get("closed", 0),
            by_priority=by_priority,
            by_severity=by_severity,
            by_category=by_category,
            avg_resolution_time_hours=None,  # TODO: Calculate
            mttr_hours=None,  # TODO: Calculate
        )

    async def _generate_incident_number(self, organization_id: UUID) -> str:
        """Generate a unique incident number."""
        # Get count of incidents for this org
        result = await self.db.execute(
            select(func.count()).where(Incident.organization_id == organization_id)
        )
        count = (result.scalar() or 0) + 1

        # Format: INC-XXXXXX
        return f"INC-{count:06d}"

    async def _add_timeline_event(
        self,
        incident_id: UUID,
        user_id: Optional[UUID],
        event_type: str,
        description: str,
        changes: Optional[Dict[str, Any]] = None,
        is_automated: bool = False,
    ) -> IncidentTimeline:
        """Add a timeline event to an incident."""
        event = IncidentTimeline(
            incident_id=incident_id,
            user_id=user_id,
            event_type=event_type,
            description=description,
            changes=changes,
            is_automated=is_automated,
        )
        self.db.add(event)
        return event
