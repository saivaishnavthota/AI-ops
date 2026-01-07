from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, func, select, update, delete
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.api.v1.deps import CurrentUser, DBSession
from app.models import Playbook, PlaybookExecution, User
from app.schemas.playbook import (
    PlaybookCreate,
    PlaybookUpdate,
    PlaybookResponse,
    PlaybookListResponse,
    PlaybookExecuteRequest,
    PlaybookExecutionResponse,
    PlaybookExecutionListResponse,
)
from app.core.audit_logger import log_create, log_update, log_delete, log_execute

router = APIRouter(prefix="/playbooks", tags=["Playbooks"])


@router.get("", response_model=PlaybookListResponse)
async def list_playbooks(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
):
    """List all playbooks for the organization."""
    query = select(Playbook).where(
        Playbook.organization_id == current_user.organization_id
    )
    
    if status == "active":
        query = query.where(Playbook.is_active == True)
    elif status == "inactive":
        query = query.where(Playbook.is_active == False)
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Playbook.id)).where(
            Playbook.organization_id == current_user.organization_id
        )
    )
    total = count_result.scalar()
    
    # Get playbooks with pagination
    result = await db.execute(
        query.order_by(desc(Playbook.created_at)).offset(skip).limit(limit)
    )
    playbooks = result.scalars().all()
    
    # Calculate pagination fields
    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit  # Ceiling division
    
    return {
        "items": playbooks,
        "total": total,
        "page": page,
        "page_size": limit,
        "pages": pages,
    }


@router.post("", response_model=PlaybookResponse, status_code=status.HTTP_201_CREATED)
async def create_playbook(
    playbook_in: PlaybookCreate,
    db: DBSession,
    current_user: CurrentUser,
    request: Request,
):
    """Create a new playbook."""
    playbook = Playbook(
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
        **playbook_in.dict(),
    )
    db.add(playbook)
    await db.commit()
    await db.refresh(playbook)
    
    # Audit log
    await log_create(
        db=db,
        user=current_user,
        resource_type="playbook",
        resource_id=str(playbook.id),
        resource_name=playbook.name,
        request=request,
    )
    
    return playbook


@router.get("/{playbook_id}", response_model=PlaybookResponse)
async def get_playbook(
    playbook_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Get a specific playbook."""
    result = await db.execute(
        select(Playbook).where(
            Playbook.id == playbook_id,
            Playbook.organization_id == current_user.organization_id,
        )
    )
    playbook = result.scalar_one_or_none()
    
    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playbook not found",
        )
    
    return playbook


@router.put("/{playbook_id}", response_model=PlaybookResponse)
async def update_playbook(
    playbook_id: UUID,
    playbook_in: PlaybookUpdate,
    db: DBSession,
    current_user: CurrentUser,
    request: Request,
):
    """Update a playbook."""
    result = await db.execute(
        select(Playbook).where(
            Playbook.id == playbook_id,
            Playbook.organization_id == current_user.organization_id,
        )
    )
    playbook = result.scalar_one_or_none()
    
    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playbook not found",
        )
    
    update_data = playbook_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(playbook, field, value)
    
    await db.commit()
    await db.refresh(playbook)
    
    # Audit log
    await log_update(
        db=db,
        user=current_user,
        resource_type="playbook",
        resource_id=str(playbook.id),
        resource_name=playbook.name,
        request=request,
    )
    
    return playbook


@router.delete("/{playbook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playbook(
    playbook_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    request: Request,
):
    """Delete a playbook."""
    result = await db.execute(
        select(Playbook).where(
            Playbook.id == playbook_id,
            Playbook.organization_id == current_user.organization_id,
        )
    )
    playbook = result.scalar_one_or_none()
    
    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playbook not found",
        )
    
    playbook_name = playbook.name
    await db.execute(delete(Playbook).where(Playbook.id == playbook_id))
    await db.commit()
    
    # Audit log
    await log_delete(
        db=db,
        user=current_user,
        resource_type="playbook",
        resource_id=str(playbook_id),
        resource_name=playbook_name,
        request=request,
    )


@router.post("/{playbook_id}/execute", response_model=PlaybookExecutionResponse)
async def execute_playbook(
    playbook_id: UUID,
    execute_request: PlaybookExecuteRequest,
    db: DBSession,
    current_user: CurrentUser,
    request: Request,
):
    """Execute a playbook manually."""
    result = await db.execute(
        select(Playbook).where(
            Playbook.id == playbook_id,
            Playbook.organization_id == current_user.organization_id,
        )
    )
    playbook = result.scalar_one_or_none()
    
    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playbook not found",
        )
    
    if not playbook.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot execute inactive playbook",
        )
    
    # Create execution record
    execution = PlaybookExecution(
        playbook_id=playbook.id,
        organization_id=current_user.organization_id,
        incident_id=execute_request.incident_id,
        alert_id=execute_request.alert_id,
        triggered_by="manual",
        triggered_by_user_id=current_user.id,
        approval_required=playbook.requires_approval,
        status="pending" if playbook.requires_approval else "running",
        started_at=datetime.now(timezone.utc) if not playbook.requires_approval else None,
    )
    
    db.add(execution)
    
    # Update playbook stats
    playbook.execution_count += 1
    
    await db.commit()
    await db.refresh(execution)
    
    # Audit log
    await log_execute(
        db=db,
        user=current_user,
        resource_type="playbook",
        resource_id=str(playbook.id),
        resource_name=playbook.name,
        request=request,
    )
    
    # Add playbook name for response
    execution_dict = {
        **execution.__dict__,
        "playbook_name": playbook.name,
        "triggered_by_user_name": current_user.full_name,
    }
    
    return execution_dict


@router.get("/{playbook_id}/executions", response_model=PlaybookExecutionListResponse)
async def list_playbook_executions(
    playbook_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List execution history for a playbook."""
    result = await db.execute(
        select(Playbook).where(
            Playbook.id == playbook_id,
            Playbook.organization_id == current_user.organization_id,
        )
    )
    playbook = result.scalar_one_or_none()
    
    if not playbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playbook not found",
        )
    
    # Get total count
    count_result = await db.execute(
        select(func.count(PlaybookExecution.id)).where(
            PlaybookExecution.playbook_id == playbook_id
        )
    )
    total = count_result.scalar()
    
    # Get executions
    executions_result = await db.execute(
        select(PlaybookExecution).where(
            PlaybookExecution.playbook_id == playbook_id
        ).order_by(desc(PlaybookExecution.created_at)).offset(skip).limit(limit)
    )
    executions = executions_result.scalars().all()
    
    # Enrich with related data
    items = []
    for execution in executions:
        execution_dict = {
            **execution.__dict__,
            "playbook_name": playbook.name,
        }
        
        if execution.triggered_by_user_id:
            user_result = await db.execute(
                select(User).where(User.id == execution.triggered_by_user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                execution_dict["triggered_by_user_name"] = user.full_name
        
        items.append(execution_dict)
    
    # Calculate pagination fields
    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit  # Ceiling division
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": limit,
        "pages": pages,
    }
