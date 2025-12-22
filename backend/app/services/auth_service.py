from datetime import datetime, timezone
from typing import Optional, Tuple
from uuid import UUID
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.organization import Organization
from app.core.security import verify_password, get_password_hash, generate_token
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
    create_password_reset_token,
    verify_password_reset_token,
)
from app.core.exceptions import AuthenticationError, ValidationError, NotFoundError, ConflictError
from app.schemas.auth import RegisterRequest, LoginRequest
from app.config.settings import settings


class AuthService:
    """Authentication service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest) -> Tuple[User, Organization]:
        """Register a new organization and admin user."""
        # Check if email already exists
        existing_user = await self.db.execute(
            select(User).where(User.email == data.email.lower())
        )
        if existing_user.scalar_one_or_none():
            raise ConflictError("Email already registered")

        # Create organization
        slug = self._generate_slug(data.organization_name)

        # Ensure slug is unique
        existing_org = await self.db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        if existing_org.scalar_one_or_none():
            slug = f"{slug}-{generate_token(4)}"

        organization = Organization(
            name=data.organization_name,
            slug=slug,
            subscription_tier="free",
            settings={},
            features={},
        )
        self.db.add(organization)
        await self.db.flush()

        # Create admin user
        user = User(
            organization_id=organization.id,
            email=data.email.lower(),
            password_hash=get_password_hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            role="admin",
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        await self.db.refresh(organization)

        return user, organization

    async def login(self, data: LoginRequest) -> Tuple[User, str, str]:
        """Authenticate user and return tokens."""
        # Find user by email
        result = await self.db.execute(
            select(User).where(User.email == data.email.lower())
        )
        user = result.scalar_one_or_none()

        if not user:
            raise AuthenticationError("Invalid email or password")

        if not user.password_hash:
            raise AuthenticationError("Please use SSO to login")

        if not verify_password(data.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is disabled")

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await self.db.commit()

        # Generate tokens
        access_token = create_access_token(
            subject=user.id,
            organization_id=user.organization_id,
            role=user.role,
        )
        refresh_token = create_refresh_token(
            subject=user.id,
            organization_id=user.organization_id,
        )

        return user, access_token, refresh_token

    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh access token using refresh token."""
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise AuthenticationError("Invalid or expired refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")

        # Get user
        result = await self.db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise AuthenticationError("User not found or disabled")

        # Generate new access token
        access_token = create_access_token(
            subject=user.id,
            organization_id=user.organization_id,
            role=user.role,
        )

        return access_token, refresh_token

    async def request_password_reset(self, email: str) -> Optional[str]:
        """Request password reset and return token (for email)."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        user = result.scalar_one_or_none()

        if not user:
            # Don't reveal if email exists
            return None

        if not user.is_active:
            return None

        # Generate reset token
        token = create_password_reset_token(email.lower())
        return token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token."""
        email = verify_password_reset_token(token)
        if not email:
            raise ValidationError("Invalid or expired reset token")

        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundError("User")

        user.password_hash = get_password_hash(new_password)
        user.password_changed_at = datetime.now(timezone.utc)
        await self.db.commit()

        return True

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> bool:
        """Change user password."""
        if not user.password_hash:
            raise ValidationError("Cannot change password for SSO users")

        if not verify_password(current_password, user.password_hash):
            raise ValidationError("Current password is incorrect")

        user.password_hash = get_password_hash(new_password)
        user.password_changed_at = datetime.now(timezone.utc)
        await self.db.commit()

        return True

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug from name."""
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug[:100]
