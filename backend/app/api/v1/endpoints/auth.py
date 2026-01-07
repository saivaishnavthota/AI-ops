from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.settings import settings
from app.api.v1.deps import CurrentUser, DBSession
from app.services.auth_service import AuthService
from app.models.audit import AuditLog
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TokenRefreshRequest,
    TokenRefreshResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePasswordRequest,
)
from app.schemas.user import UserResponse, UserProfileResponse
from app.schemas.base import MessageResponse
from app.core.exceptions import AuthenticationError, ValidationError, ConflictError

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: DBSession):
    """Register a new organization and admin user."""
    try:
        auth_service = AuthService(db)
        user, organization = await auth_service.register(data)

        # Auto-login after registration
        _, access_token, refresh_token = await auth_service.login(
            LoginRequest(email=data.email, password=data.password)
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, request: Request, db: DBSession):
    """Login and get access tokens."""
    auth_service = AuthService(db)
    
    # Get request info for audit log
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    try:
        user, access_token, refresh_token = await auth_service.login(data)
        
        # Create successful login audit log
        audit_log = AuditLog(
            organization_id=user.organization_id,
            user_id=user.id,
            action="login",
            resource_type="auth",
            resource_id=str(user.id),
            resource_name=user.full_name,
            description=f"User {user.full_name} logged in successfully",
            ip_address=ip_address,
            user_agent=user_agent,
            status="success",
        )
        db.add(audit_log)
        await db.commit()

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    except AuthenticationError as e:
        # Create failed login audit log
        # Try to find user by email to get organization_id
        from sqlalchemy import select
        from app.models.user import User
        
        result = await db.execute(
            select(User).where(User.email == data.email.lower())
        )
        user = result.scalar_one_or_none()
        
        if user:
            audit_log = AuditLog(
                organization_id=user.organization_id,
                user_id=None,  # Don't link to user for failed attempts
                action="login_failed",
                resource_type="auth",
                resource_id=data.email,
                resource_name=data.email,
                description=f"Failed login attempt for {data.email}",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e),
            )
            db.add(audit_log)
            await db.commit()
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: CurrentUser, request: Request, db: DBSession):
    """Logout - invalidate tokens (client should discard tokens)."""
    # Get request info for audit log
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Create logout audit log
    audit_log = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="logout",
        resource_type="auth",
        resource_id=str(current_user.id),
        resource_name=current_user.full_name,
        description=f"User {current_user.full_name} logged out",
        ip_address=ip_address,
        user_agent=user_agent,
        status="success",
    )
    db.add(audit_log)
    await db.commit()
    
    # In a production system, you would add the token to a blacklist
    return MessageResponse(message="Successfully logged out")


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(data: TokenRefreshRequest, db: DBSession):
    """Refresh access token using refresh token."""
    try:
        auth_service = AuthService(db)
        access_token, _ = await auth_service.refresh_token(data.refresh_token)

        return TokenRefreshResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: PasswordResetRequest, db: DBSession):
    """Request password reset email."""
    auth_service = AuthService(db)
    token = await auth_service.request_password_reset(data.email)

    # In production, send email with reset link containing token
    # For now, just return success (don't reveal if email exists)
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: PasswordResetConfirm, db: DBSession):
    """Reset password using reset token."""
    try:
        auth_service = AuthService(db)
        await auth_service.reset_password(data.token, data.new_password)
        return MessageResponse(message="Password has been reset successfully")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(current_user: CurrentUser):
    """Get current user profile."""
    from app.core.permissions import get_permissions_for_role

    return UserProfileResponse(
        id=current_user.id,
        organization_id=current_user.organization_id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        full_name=current_user.full_name,
        role=current_user.role,
        phone=current_user.phone,
        job_title=current_user.job_title,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        mfa_enabled=current_user.mfa_enabled,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        preferences=current_user.preferences or current_user.default_preferences,
        permissions=get_permissions_for_role(current_user.role),
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    current_user: CurrentUser,
    db: DBSession,
    first_name: str = None,
    last_name: str = None,
    phone: str = None,
    job_title: str = None,
):
    """Update current user profile."""
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name
    if phone:
        current_user.phone = phone
    if job_title:
        current_user.job_title = job_title

    await db.commit()
    await db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        organization_id=current_user.organization_id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        full_name=current_user.full_name,
        role=current_user.role,
        phone=current_user.phone,
        job_title=current_user.job_title,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        mfa_enabled=current_user.mfa_enabled,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """Change current user's password."""
    try:
        auth_service = AuthService(db)
        await auth_service.change_password(
            current_user, data.current_password, data.new_password
        )
        return MessageResponse(message="Password changed successfully")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
