from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .base import BaseSchema, PaginatedResponse


class UserBase(BaseModel):
    """Base user schema."""

    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    job_title: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """User creation schema."""

    email: EmailStr
    password: Optional[str] = Field(None, min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="viewer")


class UserUpdate(UserBase):
    """User update schema."""

    role: Optional[str] = None
    is_active: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(BaseSchema):
    """User response schema."""

    id: UUID
    organization_id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: str
    role: str
    phone: Optional[str]
    job_title: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class UserProfileResponse(UserResponse):
    """User profile response with preferences."""

    preferences: Dict[str, Any]
    permissions: List[str]


class UserListResponse(PaginatedResponse[UserResponse]):
    """Paginated user list response."""

    pass


class UserInviteRequest(BaseModel):
    """User invitation request."""

    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="viewer")
    team_ids: Optional[List[UUID]] = None
