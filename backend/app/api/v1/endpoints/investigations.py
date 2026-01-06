from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.api.v1 import deps
from app.models import Investigation, User
from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationUpdate,
    InvestigationResponse,
    InvestigationListResponse,
)

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("", response_model=InvestigationListResponse)
def list_investigations(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
):
    """List all investigations for the organization."""
    query = db.query(Investigation).filter(
        Investigation.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(Investigation.status == status)
    if priority:
        query = query.filter(Investigation.priority == priority)
    
    total = query.count()
    investigations = query.order_by(desc(Investigation.created_at)).offset(skip).limit(limit).all()
    
    return {
        "items": investigations,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
def create_investigation(
    investigation_in: InvestigationCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Create a new investigation."""
    investigation = Investigation(
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
        status="pending",
        progress=0,
        events_linked=0,
        findings=[],
        timeline=[
            {
                "date": datetime.utcnow().isoformat(),
                "action": "Investigation created",
                "user": current_user.full_name,
            }
        ],
        **investigation_in.dict(),
    )
    db.add(investigation)
    db.commit()
    db.refresh(investigation)
    return investigation


@router.get("/{investigation_id}", response_model=InvestigationResponse)
def get_investigation(
    investigation_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get a specific investigation."""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.organization_id == current_user.organization_id,
    ).first()
    
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )
    
    return investigation


@router.put("/{investigation_id}", response_model=InvestigationResponse)
def update_investigation(
    investigation_id: UUID,
    investigation_in: InvestigationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Update an investigation."""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.organization_id == current_user.organization_id,
    ).first()
    
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )
    
    update_data = investigation_in.dict(exclude_unset=True)
    
    # Add timeline entry for status changes
    if "status" in update_data and update_data["status"] != investigation.status:
        timeline = investigation.timeline or []
        timeline.append({
            "date": datetime.utcnow().isoformat(),
            "action": f"Status changed to {update_data['status']}",
            "user": current_user.full_name,
        })
        update_data["timeline"] = timeline
    
    for field, value in update_data.items():
        setattr(investigation, field, value)
    
    db.commit()
    db.refresh(investigation)
    return investigation


@router.delete("/{investigation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investigation(
    investigation_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Delete an investigation."""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id,
        Investigation.organization_id == current_user.organization_id,
    ).first()
    
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )
    
    db.delete(investigation)
    db.commit()
