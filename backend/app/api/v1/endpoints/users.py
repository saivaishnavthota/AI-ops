"""Users management API endpoints (Admin only)."""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List
from uuid import UUID

from app.api.v1.deps import CurrentUser, DBSession
from app.models.user import User, UserRole
from app.schemas.user import (
    UserResponse,
    UserCreate,
    UserUpdate,
    UserListResponse,
    UserInviteRequest,
)
from app.schemas.base import MessageResponse, PaginatedResponse
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundError, AuthorizationError, ConflictError
from app.core.audit_logger import log_create, log_update, log_delete, log_activate, log_deactivate

router = APIRouter(prefix="/users", tags=["Users"])


def require_admin(current_user: User) -> User:
    """Check if current user is admin or super_admin."""
    if current_user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """List all users in the organization (Admin only)."""
    require_admin(current_user)

    # Base query - users in same organization
    query = select(User).where(User.organization_id == current_user.organization_id)

    # Apply filters
    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            User.first_name.ilike(f"%{search}%"),
            User.last_name.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    if role:
        query = query.where(User.role == role)

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    users = result.scalars().all()

    return PaginatedResponse(
        items=[UserResponse(
            id=u.id,
            organization_id=u.organization_id,
            email=u.email,
            first_name=u.first_name,
            last_name=u.last_name,
            full_name=u.full_name,
            role=u.role,
            phone=u.phone,
            job_title=u.job_title,
            avatar_url=u.avatar_url,
            is_active=u.is_active,
            is_verified=u.is_verified,
            mfa_enabled=u.mfa_enabled,
            last_login=u.last_login,
            created_at=u.created_at,
            updated_at=u.updated_at,
        ) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Get a specific user by ID (Admin only)."""
    require_admin(current_user)

    query = select(User).where(
        User.id == user_id,
        User.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        job_title=user.job_title,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_verified=user.is_verified,
        mfa_enabled=user.mfa_enabled,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    current_user: CurrentUser,
    db: DBSession,
    request: Request,
):
    """Create a new user in the organization (Admin only)."""
    require_admin(current_user)

    # Check if email already exists
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Validate role
    valid_roles = [r.value for r in UserRole]
    if data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )

    # Only super_admin can create super_admin users
    if data.role == UserRole.SUPER_ADMIN.value and current_user.role != UserRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can create super admin users"
        )

    # Create user
    user = User(
        organization_id=current_user.organization_id,
        email=data.email,
        password_hash=get_password_hash(data.password) if data.password else None,
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role,
        phone=data.phone,
        job_title=data.job_title,
        is_active=True,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Audit log
    await log_create(
        db=db,
        user=current_user,
        resource_type="user",
        resource_id=str(user.id),
        resource_name=user.full_name,
        request=request,
    )

    return UserResponse(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        job_title=user.job_title,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_verified=user.is_verified,
        mfa_enabled=user.mfa_enabled,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_user: CurrentUser,
    db: DBSession,
    request: Request,
):
    """Update a user (Admin only)."""
    require_admin(current_user)

    query = select(User).where(
        User.id == user_id,
        User.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent non-super-admin from modifying super_admin users
    if user.role == UserRole.SUPER_ADMIN.value and current_user.role != UserRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify super admin user"
        )

    # Update fields
    if data.email is not None:
        # Check if email is already taken
        existing = await db.execute(
            select(User).where(User.email == data.email, User.id != user_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        user.email = data.email

    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.phone is not None:
        user.phone = data.phone
    if data.job_title is not None:
        user.job_title = data.job_title
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.preferences is not None:
        user.preferences = data.preferences

    # Handle role change
    if data.role is not None:
        valid_roles = [r.value for r in UserRole]
        if data.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )

        # Only super_admin can assign super_admin role
        if data.role == UserRole.SUPER_ADMIN.value and current_user.role != UserRole.SUPER_ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can assign super admin role"
            )

        user.role = data.role

    await db.commit()
    await db.refresh(user)
    
    # Audit log
    await log_update(
        db=db,
        user=current_user,
        resource_type="user",
        resource_id=str(user.id),
        resource_name=user.full_name,
        request=request,
    )

    return UserResponse(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        job_title=user.job_title,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_verified=user.is_verified,
        mfa_enabled=user.mfa_enabled,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
    request: Request,
):
    """Delete a user (Admin only)."""
    require_admin(current_user)

    # Cannot delete yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    query = select(User).where(
        User.id == user_id,
        User.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent non-super-admin from deleting super_admin users
    if user.role == UserRole.SUPER_ADMIN.value and current_user.role != UserRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete super admin user"
        )
    
    user_name = user.full_name
    await db.delete(user)
    await db.commit()
    
    # Audit log
    await log_delete(
        db=db,
        user=current_user,
        resource_type="user",
        resource_id=str(user_id),
        resource_name=user_name,
        request=request,
    )

    return MessageResponse(message="User deleted successfully")


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
    request: Request,
):
    """Activate a user account (Admin only)."""
    require_admin(current_user)

    query = select(User).where(
        User.id == user_id,
        User.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    await db.commit()
    await db.refresh(user)
    
    # Audit log
    await log_activate(
        db=db,
        user=current_user,
        resource_type="user",
        resource_id=str(user.id),
        resource_name=user.full_name,
        request=request,
    )

    return UserResponse(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        job_title=user.job_title,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_verified=user.is_verified,
        mfa_enabled=user.mfa_enabled,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
    request: Request,
):
    """Deactivate a user account (Admin only)."""
    require_admin(current_user)

    # Cannot deactivate yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    query = select(User).where(
        User.id == user_id,
        User.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    await db.commit()
    await db.refresh(user)
    
    # Audit log
    await log_deactivate(
        db=db,
        user=current_user,
        resource_type="user",
        resource_id=str(user.id),
        resource_name=user.full_name,
        request=request,
    )

    return UserResponse(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        job_title=user.job_title,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_verified=user.is_verified,
        mfa_enabled=user.mfa_enabled,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/{user_id}/change-role", response_model=UserResponse)
async def change_user_role(
    user_id: UUID,
    role: str,
    current_user: CurrentUser,
    db: DBSession,
):
    """Change a user's role (Admin only)."""
    require_admin(current_user)

    # Validate role
    valid_roles = [r.value for r in UserRole]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )

    query = select(User).where(
        User.id == user_id,
        User.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent non-super-admin from modifying super_admin role
    if user.role == UserRole.SUPER_ADMIN.value and current_user.role != UserRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify super admin user"
        )

    # Only super_admin can assign super_admin role
    if role == UserRole.SUPER_ADMIN.value and current_user.role != UserRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can assign super admin role"
        )

    user.role = role
    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        job_title=user.job_title,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_verified=user.is_verified,
        mfa_enabled=user.mfa_enabled,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
