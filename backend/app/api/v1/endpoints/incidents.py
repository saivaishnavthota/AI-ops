from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.v1.deps import CurrentUser, CurrentOrganization, DBSession
from app.services.incident_service import IncidentService
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentDetailResponse,
    IncidentListResponse,
    IncidentAssignRequest,
    IncidentResolveRequest,
    IncidentCommentCreate,
    IncidentCommentResponse,
    IncidentTimelineResponse,
    IncidentStatistics,
)
from app.schemas.base import MessageResponse
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[List[str]] = Query(None),
    priority: Optional[List[str]] = Query(None),
    severity: Optional[List[str]] = Query(None),
    assigned_team_id: Optional[UUID] = None,
    assigned_user_id: Optional[UUID] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    """List incidents with filters and pagination."""
    service = IncidentService(db)
    incidents, total = await service.list_incidents(
        organization_id=current_org.id,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        severity=severity,
        assigned_team_id=assigned_team_id,
        assigned_user_id=assigned_user_id,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return IncidentListResponse(
        items=[IncidentResponse.model_validate(i) for i in incidents],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    data: IncidentCreate,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Create a new incident."""
    service = IncidentService(db)
    incident = await service.create_incident(
        organization_id=current_org.id,
        data=data,
        reported_by_id=current_user.id,
    )
    return IncidentResponse.model_validate(incident)


@router.get("/statistics", response_model=IncidentStatistics)
async def get_incident_statistics(
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Get incident statistics for the organization."""
    service = IncidentService(db)
    return await service.get_statistics(current_org.id)


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
async def get_incident(
    incident_id: UUID,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Get incident details."""
    service = IncidentService(db)
    incident = await service.get_by_id(incident_id, current_org.id)

    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    # Get comments and timeline
    comments = await service.get_comments(incident_id, current_org.id)
    timeline = await service.get_timeline(incident_id, current_org.id)

    response = IncidentDetailResponse.model_validate(incident)
    response.comments = [IncidentCommentResponse.model_validate(c) for c in comments]
    response.timeline = [IncidentTimelineResponse.model_validate(t) for t in timeline]

    return response


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    data: IncidentUpdate,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Update an incident."""
    try:
        service = IncidentService(db)
        incident = await service.update_incident(
            incident_id=incident_id,
            organization_id=current_org.id,
            data=data,
            user_id=current_user.id,
        )
        return IncidentResponse.model_validate(incident)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{incident_id}/acknowledge", response_model=IncidentResponse)
async def acknowledge_incident(
    incident_id: UUID,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Acknowledge an incident."""
    try:
        service = IncidentService(db)
        incident = await service.acknowledge_incident(
            incident_id=incident_id,
            organization_id=current_org.id,
            user_id=current_user.id,
        )
        return IncidentResponse.model_validate(incident)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: UUID,
    data: IncidentResolveRequest,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Resolve an incident."""
    try:
        service = IncidentService(db)
        incident = await service.resolve_incident(
            incident_id=incident_id,
            organization_id=current_org.id,
            user_id=current_user.id,
            resolution_notes=data.resolution_notes,
            root_cause=data.root_cause,
        )
        return IncidentResponse.model_validate(incident)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{incident_id}/close", response_model=IncidentResponse)
async def close_incident(
    incident_id: UUID,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Close an incident."""
    try:
        service = IncidentService(db)
        incident = await service.close_incident(
            incident_id=incident_id,
            organization_id=current_org.id,
            user_id=current_user.id,
        )
        return IncidentResponse.model_validate(incident)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{incident_id}/assign", response_model=IncidentResponse)
async def assign_incident(
    incident_id: UUID,
    data: IncidentAssignRequest,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Assign incident to team/user."""
    try:
        service = IncidentService(db)
        incident = await service.assign_incident(
            incident_id=incident_id,
            organization_id=current_org.id,
            user_id=current_user.id,
            assigned_team_id=data.assigned_team_id,
            assigned_user_id=data.assigned_user_id,
        )
        return IncidentResponse.model_validate(incident)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{incident_id}/timeline", response_model=List[IncidentTimelineResponse])
async def get_incident_timeline(
    incident_id: UUID,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Get incident timeline."""
    try:
        service = IncidentService(db)
        timeline = await service.get_timeline(incident_id, current_org.id)
        return [IncidentTimelineResponse.model_validate(t) for t in timeline]
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{incident_id}/comments", response_model=List[IncidentCommentResponse])
async def get_incident_comments(
    incident_id: UUID,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Get incident comments."""
    try:
        service = IncidentService(db)
        comments = await service.get_comments(incident_id, current_org.id)
        return [IncidentCommentResponse.model_validate(c) for c in comments]
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{incident_id}/comments", response_model=IncidentCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_incident_comment(
    incident_id: UUID,
    data: IncidentCommentCreate,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Add a comment to an incident."""
    try:
        service = IncidentService(db)
        comment = await service.add_comment(
            incident_id=incident_id,
            organization_id=current_org.id,
            user_id=current_user.id,
            content=data.content,
            is_internal=data.is_internal,
            attachments=data.attachments,
        )
        return IncidentCommentResponse.model_validate(comment)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
