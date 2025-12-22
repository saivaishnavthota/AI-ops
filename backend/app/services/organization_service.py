from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.organization import Organization
from app.models.user import User
from app.models.team import Team
from app.models.incident import Incident
from app.models.alert import Alert
from app.core.exceptions import NotFoundError
from app.schemas.organization import OrganizationUpdate, OrganizationStatsResponse


class OrganizationService:
    """Organization management service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, organization_id: UUID) -> Optional[Organization]:
        """Get organization by ID."""
        result = await self.db.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        result = await self.db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        return result.scalar_one_or_none()

    async def update(
        self, organization_id: UUID, data: OrganizationUpdate
    ) -> Organization:
        """Update organization."""
        org = await self.get_by_id(organization_id)
        if not org:
            raise NotFoundError("Organization", organization_id)

        update_data = data.model_dump(exclude_unset=True)

        # Handle nested settings update (merge instead of replace)
        if "settings" in update_data and org.settings:
            update_data["settings"] = {**org.settings, **update_data["settings"]}

        if "features" in update_data and org.features:
            update_data["features"] = {**org.features, **update_data["features"]}

        for field, value in update_data.items():
            setattr(org, field, value)

        await self.db.commit()
        await self.db.refresh(org)

        return org

    async def get_stats(self, organization_id: UUID) -> OrganizationStatsResponse:
        """Get organization statistics."""
        # Count users
        users_count = await self.db.execute(
            select(func.count()).where(User.organization_id == organization_id)
        )
        total_users = users_count.scalar() or 0

        # Count teams
        teams_count = await self.db.execute(
            select(func.count()).where(Team.organization_id == organization_id)
        )
        total_teams = teams_count.scalar() or 0

        # Count incidents
        incidents_count = await self.db.execute(
            select(func.count()).where(Incident.organization_id == organization_id)
        )
        total_incidents = incidents_count.scalar() or 0

        # Count open incidents
        open_incidents_count = await self.db.execute(
            select(func.count()).where(
                Incident.organization_id == organization_id,
                Incident.status.in_(["open", "acknowledged", "in_progress"]),
            )
        )
        open_incidents = open_incidents_count.scalar() or 0

        # Count alerts
        alerts_count = await self.db.execute(
            select(func.count()).where(Alert.organization_id == organization_id)
        )
        total_alerts = alerts_count.scalar() or 0

        # Count active alerts
        active_alerts_count = await self.db.execute(
            select(func.count()).where(
                Alert.organization_id == organization_id,
                Alert.status == "firing",
            )
        )
        active_alerts = active_alerts_count.scalar() or 0

        return OrganizationStatsResponse(
            total_users=total_users,
            total_teams=total_teams,
            total_incidents=total_incidents,
            total_alerts=total_alerts,
            open_incidents=open_incidents,
            active_alerts=active_alerts,
        )
