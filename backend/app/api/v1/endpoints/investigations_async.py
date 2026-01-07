from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, func, select
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.api.v1.deps import CurrentUser, DBSession
from app.models.investigation import Investigation
from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationUpdate,
    InvestigationResponse,
    InvestigationListResponse,
)

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("", response_model=InvestigationListResponse)
async def list_investigations(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
):
    """List all investigations for the organization."""
    query = select(Investigation).where(
        Investigation.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.where(Investigation.status == status)
    if priority:
        query = query.where(Investigation.priority == priority)
    
    # Get total count
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()
    
    # Get investigations
    result = await db.execute(
        query.order_by(desc(Investigation.created_at)).offset(skip).limit(limit)
    )
    investigations = result.scalars().all()
    
    return {
        "items": investigations,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    investigation_in: InvestigationCreate,
    db: DBSession,
    current_user: CurrentUser,
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
                "date": datetime.now(timezone.utc).isoformat(),
                "action": "Investigation created",
                "user": current_user.full_name,
            }
        ],
        **investigation_in.dict(),
    )
    db.add(investigation)
    await db.commit()
    await db.refresh(investigation)
    return investigation


@router.get("/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation(
    investigation_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Get a specific investigation."""
    result = await db.execute(
        select(Investigation).where(
            Investigation.id == investigation_id,
            Investigation.organization_id == current_user.organization_id,
        )
    )
    investigation = result.scalar_one_or_none()
    
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )
    
    return investigation


@router.put("/{investigation_id}", response_model=InvestigationResponse)
async def update_investigation(
    investigation_id: UUID,
    investigation_in: InvestigationUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Update an investigation."""
    result = await db.execute(
        select(Investigation).where(
            Investigation.id == investigation_id,
            Investigation.organization_id == current_user.organization_id,
        )
    )
    investigation = result.scalar_one_or_none()
    
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )
    
    update_data = investigation_in.dict(exclude_unset=True)
    
    # Add timeline entry for status changes
    if "status" in update_data and update_data["status"] != investigation.status:
        if not investigation.timeline:
            investigation.timeline = []
        investigation.timeline.append({
            "date": datetime.now(timezone.utc).isoformat(),
            "action": f"Status changed to {update_data['status']}",
            "user": current_user.full_name,
        })
    
    # If closing, set closed_at
    if update_data.get("status") == "closed" and investigation.status != "closed":
        update_data["closed_at"] = datetime.now(timezone.utc)
    
    for field, value in update_data.items():
        setattr(investigation, field, value)
    
    await db.commit()
    await db.refresh(investigation)
    return investigation


@router.delete("/{investigation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investigation(
    investigation_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Delete an investigation."""
    result = await db.execute(
        select(Investigation).where(
            Investigation.id == investigation_id,
            Investigation.organization_id == current_user.organization_id,
        )
    )
    investigation = result.scalar_one_or_none()
    
    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )
    
    await db.delete(investigation)
    await db.commit()
