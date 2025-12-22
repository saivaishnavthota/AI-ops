from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.v1.deps import CurrentUser, CurrentOrganization, DBSession, AdminUser
from app.services.organization_service import OrganizationService
from app.services.user_service import UserService
from app.schemas.organization import OrganizationResponse, OrganizationUpdate, OrganizationStatsResponse
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UserListResponse
from app.schemas.base import MessageResponse
from app.core.exceptions import NotFoundError, ConflictError, ValidationError

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("", response_model=OrganizationResponse)
async def get_current_organization(
    current_org: CurrentOrganization,
):
    """Get current organization details."""
    return OrganizationResponse.model_validate(current_org)


@router.put("", response_model=OrganizationResponse)
async def update_organization(
    data: OrganizationUpdate,
    current_user: AdminUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Update organization settings (admin only)."""
    try:
        service = OrganizationService(db)
        organization = await service.update(current_org.id, data)
        return OrganizationResponse.model_validate(organization)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/stats", response_model=OrganizationStatsResponse)
async def get_organization_stats(
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Get organization statistics."""
    service = OrganizationService(db)
    return await service.get_stats(current_org.id)


# User Management
@router.get("/users", response_model=UserListResponse)
async def list_users(
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """List organization users."""
    service = UserService(db)
    users, total = await service.list_users(
        organization_id=current_org.id,
        page=page,
        page_size=page_size,
        search=search,
        role=role,
        is_active=is_active,
    )

    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    current_user: AdminUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Create a new user (admin only)."""
    try:
        service = UserService(db)
        user = await service.create_user(current_org.id, data)
        return UserResponse.model_validate(user)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Get user details."""
    service = UserService(db)
    user = await service.get_by_id(user_id)

    if not user or user.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_user: AdminUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Update a user (admin only)."""
    try:
        service = UserService(db)
        user = await service.update_user(user_id, data, current_user)
        return UserResponse.model_validate(user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    current_user: AdminUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Delete a user (admin only)."""
    try:
        service = UserService(db)
        await service.delete_user(user_id, current_user)
        return MessageResponse(message="User deleted successfully")
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
