from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.api.v1 import deps
from app.models import SecurityEvent, User
from app.schemas.security import (
    SecurityEventCreate,
    SecurityEventUpdate,
    SecurityEventResponse,
    SecurityEventListResponse,
    SecurityEventStatsResponse,
)

router = APIRouter(prefix="/security-events", tags=["Security"])


@router.get("", response_model=SecurityEventListResponse)
def list_security_events(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    severity: Optional[str] = None,
    status: Optional[str] = None,
):
    """List all security events for the organization."""
    query = db.query(SecurityEvent).filter(
        SecurityEvent.organization_id == current_user.organization_id
    )
    
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    if status:
        query = query.filter(SecurityEvent.status == status)
    
    total = query.count()
    events = query.order_by(desc(SecurityEvent.created_at)).offset(skip).limit(limit).all()
    
    return {
        "items": events,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/stats", response_model=SecurityEventStatsResponse)
def get_security_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get security event statistics."""
    base_query = db.query(SecurityEvent).filter(
        SecurityEvent.organization_id == current_user.organization_id
    )
    
    total_events = base_query.count()
    critical_count = base_query.filter(SecurityEvent.severity == "critical", SecurityEvent.status != "resolved").count()
    high_count = base_query.filter(SecurityEvent.severity == "high", SecurityEvent.status != "resolved").count()
    open_count = base_query.filter(SecurityEvent.status.in_(["open", "investigating"])).count()
    
    # Group by severity
    by_severity = {}
    severity_counts = db.query(
        SecurityEvent.severity,
        func.count(SecurityEvent.id)
    ).filter(
        SecurityEvent.organization_id == current_user.organization_id
    ).group_by(SecurityEvent.severity).all()
    
    for severity, count in severity_counts:
        by_severity[severity] = count
    
    # Group by status
    by_status = {}
    status_counts = db.query(
        SecurityEvent.status,
        func.count(SecurityEvent.id)
    ).filter(
        SecurityEvent.organization_id == current_user.organization_id
    ).group_by(SecurityEvent.status).all()
    
    for event_status, count in status_counts:
        by_status[event_status] = count
    
    # Group by type
    by_type = {}
    type_counts = db.query(
        SecurityEvent.type,
        func.count(SecurityEvent.id)
    ).filter(
        SecurityEvent.organization_id == current_user.organization_id
    ).group_by(SecurityEvent.type).all()
    
    for event_type, count in type_counts:
        by_type[event_type] = count
    
    return {
        "total_events": total_events,
        "critical_count": critical_count,
        "high_count": high_count,
        "open_count": open_count,
        "by_severity": by_severity,
        "by_status": by_status,
        "by_type": by_type,
    }


@router.post("", response_model=SecurityEventResponse, status_code=status.HTTP_201_CREATED)
def create_security_event(
    event_in: SecurityEventCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Create a new security event."""
    event = SecurityEvent(
        organization_id=current_user.organization_id,
        status="open",
        **event_in.dict(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/{event_id}", response_model=SecurityEventResponse)
def get_security_event(
    event_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get a specific security event."""
    event = db.query(SecurityEvent).filter(
        SecurityEvent.id == event_id,
        SecurityEvent.organization_id == current_user.organization_id,
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security event not found",
        )
    
    return event


@router.put("/{event_id}", response_model=SecurityEventResponse)
def update_security_event(
    event_id: UUID,
    event_in: SecurityEventUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Update a security event."""
    event = db.query(SecurityEvent).filter(
        SecurityEvent.id == event_id,
        SecurityEvent.organization_id == current_user.organization_id,
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security event not found",
        )
    
    update_data = event_in.dict(exclude_unset=True)
    
    # If resolving, set resolved_at and resolved_by
    if update_data.get("status") == "resolved" and event.status != "resolved":
        update_data["resolved_at"] = datetime.utcnow()
        update_data["resolved_by_id"] = current_user.id
    
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_security_event(
    event_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Delete a security event."""
    event = db.query(SecurityEvent).filter(
        SecurityEvent.id == event_id,
        SecurityEvent.organization_id == current_user.organization_id,
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security event not found",
        )
    
    db.delete(event)
    db.commit()
