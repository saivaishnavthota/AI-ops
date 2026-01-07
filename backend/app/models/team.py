from sqlalchemy import Column, String, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class Team(BaseModel):
    """Team model for organizing users."""

    __tablename__ = "teams"

    # Organization reference
    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Team type: operations, security, devops, network, support, etc.
    team_type = Column(String(50), default="operations")

    # Escalation policy reference (for future implementation)
    escalation_policy_id = Column(GUID(), nullable=True)

    # Settings
    settings = Column(JSON, default=dict)

    # Status
    is_active = Column(Boolean, default=True)

    # Relationships
    organization = relationship("Organization", back_populates="teams")
    members = relationship("TeamMember", back_populates="team", lazy="dynamic")
    assigned_incidents = relationship("Incident", back_populates="assigned_team", lazy="dynamic")

    def __repr__(self) -> str:
        try:
            return f"<Team {self.name}>"
        except:
            return f"<Team id={self.id}>"


class TeamMember(BaseModel):
    """Team membership model."""

    __tablename__ = "team_members"

    team_id = Column(
        GUID(),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Role within team: lead, member, on_call
    role = Column(String(50), default="member")

    # On-call status
    is_on_call = Column(Boolean, default=False)

    # Notifications for this team
    notifications_enabled = Column(Boolean, default=True)

    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")

    def __repr__(self) -> str:
        return f"<TeamMember team={self.team_id} user={self.user_id}>"
