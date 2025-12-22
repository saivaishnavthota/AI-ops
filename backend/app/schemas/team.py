from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .base import BaseSchema, PaginatedResponse


class TeamBase(BaseModel):
    """Base team schema."""

    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    team_type: Optional[str] = Field(None, max_length=50)


class TeamCreate(TeamBase):
    """Team creation schema."""

    name: str = Field(..., min_length=1, max_length=255)
    team_type: str = Field(default="operations")
    member_ids: Optional[List[UUID]] = None


class TeamUpdate(TeamBase):
    """Team update schema."""

    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class TeamMemberBase(BaseModel):
    """Base team member schema."""

    role: Optional[str] = Field(None, max_length=50)
    is_on_call: Optional[bool] = None
    notifications_enabled: Optional[bool] = None


class TeamMemberCreate(TeamMemberBase):
    """Team member creation schema."""

    user_id: UUID
    role: str = Field(default="member")


class TeamMemberUpdate(TeamMemberBase):
    """Team member update schema."""

    pass


class TeamMemberResponse(BaseSchema):
    """Team member response schema."""

    id: UUID
    team_id: UUID
    user_id: UUID
    role: str
    is_on_call: bool
    notifications_enabled: bool
    created_at: datetime

    # Included user details
    user_email: Optional[str] = None
    user_name: Optional[str] = None


class TeamResponse(BaseSchema):
    """Team response schema."""

    id: UUID
    organization_id: UUID
    name: str
    description: Optional[str]
    team_type: str
    settings: Dict[str, Any]
    is_active: bool
    member_count: int = 0
    created_at: datetime
    updated_at: datetime


class TeamDetailResponse(TeamResponse):
    """Team detail response with members."""

    members: List[TeamMemberResponse] = []


class TeamListResponse(PaginatedResponse[TeamResponse]):
    """Paginated team list response."""

    pass
