from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User
from app.models.team import TeamMember
from app.core.security import get_password_hash, generate_password
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """User management service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def list_users(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[User], int]:
        """List users for an organization with pagination."""
        query = select(User).where(User.organization_id == organization_id)

        # Apply filters
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (User.email.ilike(search_filter))
                | (User.first_name.ilike(search_filter))
                | (User.last_name.ilike(search_filter))
            )

        if role:
            query = query.where(User.role == role)

        if is_active is not None:
            query = query.where(User.is_active == is_active)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.order_by(User.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        users = result.scalars().all()

        return list(users), total

    async def create_user(
        self, organization_id: UUID, data: UserCreate
    ) -> User:
        """Create a new user."""
        # Check if email already exists
        existing = await self.get_by_email(data.email)
        if existing:
            raise ConflictError("Email already registered")

        # Generate password if not provided
        password = data.password or generate_password()

        user = User(
            organization_id=organization_id,
            email=data.email.lower(),
            password_hash=get_password_hash(password),
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role,
            phone=data.phone,
            job_title=data.job_title,
            is_active=True,
            is_verified=False,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_user(
        self, user_id: UUID, data: UserUpdate, current_user: User
    ) -> User:
        """Update a user."""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)

        # Check organization
        if user.organization_id != current_user.organization_id:
            raise NotFoundError("User", user_id)

        # Prevent non-admins from changing roles
        if data.role and not current_user.is_admin:
            raise ValidationError("Only admins can change user roles")

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def delete_user(self, user_id: UUID, current_user: User) -> bool:
        """Delete a user (soft delete by deactivating)."""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)

        if user.organization_id != current_user.organization_id:
            raise NotFoundError("User", user_id)

        # Prevent deleting yourself
        if user.id == current_user.id:
            raise ValidationError("Cannot delete your own account")

        # Soft delete
        user.is_active = False
        await self.db.commit()

        return True

    async def get_user_teams(self, user_id: UUID) -> List[TeamMember]:
        """Get all team memberships for a user."""
        result = await self.db.execute(
            select(TeamMember).where(TeamMember.user_id == user_id)
        )
        return list(result.scalars().all())
