from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID, uuid4
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.alert import Alert, AlertSource, AlertCorrelation, AlertStatus
from app.models.incident import Incident, IncidentStatus
from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.alert import AlertCreate, AlertUpdate, AlertStatistics, AlertSourceCreate


class AlertService:
    """Alert management service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, alert_id: UUID, organization_id: UUID) -> Optional[Alert]:
        """Get alert by ID."""
        result = await self.db.execute(
            select(Alert).where(
                Alert.id == alert_id,
                Alert.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_alerts(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 50,
        status: Optional[List[str]] = None,
        severity: Optional[List[str]] = None,
        source: Optional[str] = None,
        host: Optional[str] = None,
        service: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Alert], int]:
        """List alerts with filters and pagination."""
        query = select(Alert).where(Alert.organization_id == organization_id)

        # Apply filters
        if status:
            query = query.where(Alert.status.in_(status))

        if severity:
            query = query.where(Alert.severity.in_(severity))

        if source:
            query = query.where(Alert.source == source)

        if host:
            query = query.where(Alert.host.ilike(f"%{host}%"))

        if service:
            query = query.where(Alert.service.ilike(f"%{service}%"))

        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (Alert.title.ilike(search_filter))
                | (Alert.message.ilike(search_filter))
                | (Alert.host.ilike(search_filter))
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(Alert, sort_by, Alert.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        alerts = result.scalars().all()

        return list(alerts), total

    async def ingest_alert(
        self, organization_id: UUID, data: AlertCreate
    ) -> Alert:
        """Ingest a new alert (from webhook or API)."""
        # Generate fingerprint for deduplication
        fingerprint = self._generate_fingerprint(data)

        # Check for existing alert with same fingerprint (deduplication)
        existing_alert = await self._find_by_fingerprint(organization_id, fingerprint)

        if existing_alert and existing_alert.status == AlertStatus.FIRING.value:
            # Update existing alert (increment count)
            existing_alert.occurrence_count += 1
            existing_alert.last_occurrence_at = datetime.now(timezone.utc)
            existing_alert.message = data.message  # Update message
            await self.db.commit()
            await self.db.refresh(existing_alert)
            return existing_alert

        # Create new alert
        now = datetime.now(timezone.utc)
        alert = Alert(
            organization_id=organization_id,
            alert_id_external=data.alert_id_external,
            source=data.source,
            source_type=data.source_type,
            title=data.title,
            message=data.message,
            severity=data.severity,
            status=AlertStatus.FIRING.value,
            host=data.host,
            service=data.service,
            metric_name=data.metric_name,
            metric_value=data.metric_value,
            threshold_value=data.threshold_value,
            tags=data.tags or {},
            raw_payload=data.raw_payload,
            fingerprint=fingerprint,
            occurrence_count=1,
            first_occurrence_at=now,
            last_occurrence_at=now,
        )

        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)

        return alert

    async def acknowledge_alert(
        self, alert_id: UUID, organization_id: UUID, user_id: UUID
    ) -> Alert:
        """Acknowledge an alert."""
        alert = await self.get_by_id(alert_id, organization_id)
        if not alert:
            raise NotFoundError("Alert", alert_id)

        if alert.status != AlertStatus.FIRING.value:
            raise ValidationError("Alert is not in firing status")

        alert.status = AlertStatus.ACKNOWLEDGED.value
        alert.acknowledged_at = datetime.now(timezone.utc)
        alert.acknowledged_by_id = user_id

        await self.db.commit()
        await self.db.refresh(alert)

        return alert

    async def resolve_alert(
        self, alert_id: UUID, organization_id: UUID
    ) -> Alert:
        """Resolve an alert."""
        alert = await self.get_by_id(alert_id, organization_id)
        if not alert:
            raise NotFoundError("Alert", alert_id)

        if alert.status == AlertStatus.RESOLVED.value:
            raise ValidationError("Alert is already resolved")

        alert.status = AlertStatus.RESOLVED.value
        alert.resolved_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(alert)

        return alert

    async def suppress_alert(
        self,
        alert_id: UUID,
        organization_id: UUID,
        reason: str,
        duration_hours: Optional[int] = None,
    ) -> Alert:
        """Suppress an alert."""
        alert = await self.get_by_id(alert_id, organization_id)
        if not alert:
            raise NotFoundError("Alert", alert_id)

        alert.status = AlertStatus.SUPPRESSED.value
        alert.is_suppressed = True
        alert.suppression_reason = reason

        if duration_hours:
            from datetime import timedelta
            alert.suppressed_until = datetime.now(timezone.utc) + timedelta(hours=duration_hours)

        await self.db.commit()
        await self.db.refresh(alert)

        return alert

    async def create_incident_from_alert(
        self,
        alert_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: str = "p3",
        severity: str = "medium",
        assigned_team_id: Optional[UUID] = None,
    ) -> Incident:
        """Create an incident from an alert."""
        alert = await self.get_by_id(alert_id, organization_id)
        if not alert:
            raise NotFoundError("Alert", alert_id)

        # Import here to avoid circular dependency
        from app.services.incident_service import IncidentService
        from app.schemas.incident import IncidentCreate

        incident_service = IncidentService(self.db)

        incident_data = IncidentCreate(
            title=title or alert.title or f"Alert: {alert.source}",
            description=description or alert.message,
            priority=priority,
            severity=severity,
            assigned_team_id=assigned_team_id,
            affected_services=[alert.service] if alert.service else [],
            tags=[alert.source],
        )

        incident = await incident_service.create_incident(
            organization_id, incident_data, user_id
        )

        # Link alert to incident
        alert.incident_id = incident.id
        await self.db.commit()

        return incident

    async def get_statistics(self, organization_id: UUID) -> AlertStatistics:
        """Get alert statistics."""
        # Total count
        total_result = await self.db.execute(
            select(func.count()).where(Alert.organization_id == organization_id)
        )
        total = total_result.scalar() or 0

        # Count by status
        status_counts = {}
        for status in AlertStatus:
            result = await self.db.execute(
                select(func.count()).where(
                    Alert.organization_id == organization_id,
                    Alert.status == status.value,
                )
            )
            status_counts[status.value] = result.scalar() or 0

        # Count by severity
        severity_result = await self.db.execute(
            select(Alert.severity, func.count())
            .where(Alert.organization_id == organization_id)
            .group_by(Alert.severity)
        )
        by_severity = dict(severity_result.all())

        # Count by source
        source_result = await self.db.execute(
            select(Alert.source, func.count())
            .where(Alert.organization_id == organization_id)
            .group_by(Alert.source)
        )
        by_source = dict(source_result.all())

        # Count by service
        service_result = await self.db.execute(
            select(Alert.service, func.count())
            .where(
                Alert.organization_id == organization_id,
                Alert.service.isnot(None),
            )
            .group_by(Alert.service)
        )
        by_service = dict(service_result.all())

        return AlertStatistics(
            total=total,
            firing=status_counts.get("firing", 0),
            acknowledged=status_counts.get("acknowledged", 0),
            resolved=status_counts.get("resolved", 0),
            suppressed=status_counts.get("suppressed", 0),
            by_severity=by_severity,
            by_source=by_source,
            by_service=by_service,
        )

    # Alert Source Management
    async def create_source(
        self, organization_id: UUID, data: AlertSourceCreate
    ) -> AlertSource:
        """Create an alert source configuration."""
        from app.core.security import generate_api_key

        source = AlertSource(
            organization_id=organization_id,
            name=data.name,
            source_type=data.source_type,
            config=data.config or {},
            api_key=generate_api_key(),
            is_active=True,
        )

        self.db.add(source)
        await self.db.commit()
        await self.db.refresh(source)

        return source

    async def list_sources(self, organization_id: UUID) -> List[AlertSource]:
        """List all alert sources for an organization."""
        result = await self.db.execute(
            select(AlertSource)
            .where(AlertSource.organization_id == organization_id)
            .order_by(AlertSource.created_at.desc())
        )
        return list(result.scalars().all())

    def _generate_fingerprint(self, data: AlertCreate) -> str:
        """Generate a fingerprint for alert deduplication."""
        # Create fingerprint from key fields
        fingerprint_data = f"{data.source}:{data.host}:{data.service}:{data.title}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()

    async def _find_by_fingerprint(
        self, organization_id: UUID, fingerprint: str
    ) -> Optional[Alert]:
        """Find an alert by fingerprint."""
        result = await self.db.execute(
            select(Alert).where(
                Alert.organization_id == organization_id,
                Alert.fingerprint == fingerprint,
                Alert.status.in_([AlertStatus.FIRING.value, AlertStatus.ACKNOWLEDGED.value]),
            )
        )
        return result.scalar_one_or_none()
