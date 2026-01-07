"""Audit logging utility for tracking user actions."""
from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.user import User


async def log_action(
    db: AsyncSession,
    user: User,
    action: str,
    resource_type: str,
    resource_id: str,
    resource_name: Optional[str] = None,
    description: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
    status: str = "success",
    error_message: Optional[str] = None,
) -> AuditLog:
    """
    Create an audit log entry.
    
    Args:
        db: Database session
        user: User performing the action
        action: Action being performed (create, update, delete, etc.)
        resource_type: Type of resource (incident, alert, user, etc.)
        resource_id: ID of the resource
        resource_name: Name of the resource (optional)
        description: Human-readable description
        changes: Dictionary of changes {field: {old: x, new: y}}
        request: FastAPI request object (for IP and user agent)
        status: Status of the action (success, failed)
        error_message: Error message if action failed
    
    Returns:
        Created AuditLog instance
    """
    # Get request info if available
    ip_address = "unknown"
    user_agent = "unknown"
    
    if request:
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
    
    # Create audit log entry
    audit_log = AuditLog(
        organization_id=user.organization_id,
        user_id=user.id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        description=description or f"{action.capitalize()} {resource_type}",
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        error_message=error_message,
    )
    
    db.add(audit_log)
    await db.commit()
    
    return audit_log


async def log_create(
    db: AsyncSession,
    user: User,
    resource_type: str,
    resource_id: str,
    resource_name: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource creation action."""
    return await log_action(
        db=db,
        user=user,
        action="create",
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        description=f"Created {resource_type}: {resource_name}",
        request=request,
    )


async def log_update(
    db: AsyncSession,
    user: User,
    resource_type: str,
    resource_id: str,
    resource_name: str,
    changes: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource update action."""
    return await log_action(
        db=db,
        user=user,
        action="update",
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        description=f"Updated {resource_type}: {resource_name}",
        changes=changes,
        request=request,
    )


async def log_delete(
    db: AsyncSession,
    user: User,
    resource_type: str,
    resource_id: str,
    resource_name: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource deletion action."""
    return await log_action(
        db=db,
        user=user,
        action="delete",
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        description=f"Deleted {resource_type}: {resource_name}",
        request=request,
    )


async def log_assign(
    db: AsyncSession,
    user: User,
    resource_type: str,
    resource_id: str,
    resource_name: str,
    assigned_to: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource assignment action."""
    return await log_action(
        db=db,
        user=user,
        action="assign",
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        description=f"Assigned {resource_type} '{resource_name}' to {assigned_to}",
        request=request,
    )


async def log_resolve(
    db: AsyncSession,
    user: User,
    resource_type: str,
    resource_id: str,
    resource_name: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource resolution action."""
    return await log_action(
        db=db,
        user=user,
        action="resolve",
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        description=f"Resolved {resource_type}: {resource_name}",
        request=request,
    )


async def log_execute(
    db: AsyncSession,
    user: User,
    resource_type: str,
    resource_id: str,
    resource_name: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource execution action (e.g., playbook)."""
    return await log_action(
        db=db,
        user=user,
        action="execute",
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        description=f"Executed {resource_type}: {resource_name}",
        request=request,
    )


async def log_acknowledge(
    db: AsyncSession,
    user: User,
    resource_type: str,
    resource_id: str,
    resource_name: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource acknowledgment action."""
    return await log_action(
        db=db,
        user=user,
        action="acknowledge",
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        description=f"Acknowledged {resource_type}: {resource_name}",
        request=request,
    )


async def log_close(
    db: AsyncSession,
    user: User,
    resource_type: str,
    resource_id: str,
    resource_name: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource close action."""
    return await log_action(
        db=db,
        user=user,
        action="close",
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        description=f"Closed {resource_type}: {resource_name}",
        request=request,
    )


async def log_activate(
    db: AsyncSession,
    user: User,
    resource_type: str,
    resource_id: str,
    resource_name: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource activation action."""
    return await log_action(
        db=db,
        user=user,
        action="activate",
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        description=f"Activated {resource_type}: {resource_name}",
        request=request,
    )


async def log_deactivate(
    db: AsyncSession,
    user: User,
    resource_type: str,
    resource_id: str,
    resource_name: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log a resource deactivation action."""
    return await log_action(
        db=db,
        user=user,
        action="deactivate",
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        description=f"Deactivated {resource_type}: {resource_name}",
        request=request,
    )
