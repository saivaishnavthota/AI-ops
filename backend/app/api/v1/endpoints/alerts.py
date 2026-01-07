from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request

from app.api.v1.deps import CurrentUser, CurrentOrganization, DBSession
from app.services.alert_service import AlertService
from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertDetailResponse,
    AlertListResponse,
    AlertAcknowledgeRequest,
    AlertSuppressRequest,
    AlertCreateIncidentRequest,
    AlertStatsResponse,
    AlertSourceCreate,
    AlertSourceResponse,
)
from app.schemas.incident import IncidentResponse
from app.core.exceptions import NotFoundError, ValidationError
from app.core.audit_logger import log_create, log_acknowledge, log_resolve

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[List[str]] = Query(None),
    severity: Optional[List[str]] = Query(None),
    source: Optional[str] = None,
    host: Optional[str] = None,
    service: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    """List alerts with filters and pagination."""
    alert_service = AlertService(db)
    alerts, total = await alert_service.list_alerts(
        organization_id=current_org.id,
        page=page,
        page_size=page_size,
        status=status,
        severity=severity,
        source=source,
        host=host,
        service=service,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return AlertListResponse(
        items=[AlertResponse.model_validate(a) for a in alerts],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def ingest_alert(
    data: AlertCreate,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
    request: Request,
):
    """Ingest a new alert (webhook endpoint)."""
    alert_service = AlertService(db)
    alert = await alert_service.ingest_alert(
        organization_id=current_org.id,
        data=data,
    )
    
    # Audit log
    await log_create(
        db=db,
        user=current_user,
        resource_type="alert",
        resource_id=str(alert.id),
        resource_name=alert.title,
        request=request,
    )
    
    return AlertResponse.model_validate(alert)


@router.get("/statistics", response_model=AlertStatsResponse)
async def get_alert_statistics(
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Get alert statistics for the organization."""
    alert_service = AlertService(db)
    return await alert_service.get_statistics(current_org.id)


@router.get("/sources", response_model=List[AlertSourceResponse])
async def list_alert_sources(
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """List configured alert sources."""
    alert_service = AlertService(db)
    sources = await alert_service.list_sources(current_org.id)
    return [AlertSourceResponse.model_validate(s) for s in sources]


@router.post("/sources", response_model=AlertSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_source(
    data: AlertSourceCreate,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Create a new alert source configuration."""
    alert_service = AlertService(db)
    source = await alert_service.create_source(
        organization_id=current_org.id,
        data=data,
    )
    return AlertSourceResponse.model_validate(source)


@router.get("/{alert_id}", response_model=AlertDetailResponse)
async def get_alert(
    alert_id: UUID,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Get alert details."""
    alert_service = AlertService(db)
    alert = await alert_service.get_by_id(alert_id, current_org.id)

    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    return AlertDetailResponse.model_validate(alert)


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: UUID,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
    request: Request,
):
    """Acknowledge an alert."""
    try:
        alert_service = AlertService(db)
        alert = await alert_service.acknowledge_alert(
            alert_id=alert_id,
            organization_id=current_org.id,
            user_id=current_user.id,
        )
        
        # Audit log
        await log_acknowledge(
            db=db,
            user=current_user,
            resource_type="alert",
            resource_id=str(alert.id),
            resource_name=alert.title,
            request=request,
        )
        
        return AlertResponse.model_validate(alert)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: UUID,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
    request: Request,
):
    """Resolve an alert."""
    try:
        alert_service = AlertService(db)
        alert = await alert_service.resolve_alert(
            alert_id=alert_id,
            organization_id=current_org.id,
        )
        
        # Audit log
        await log_resolve(
            db=db,
            user=current_user,
            resource_type="alert",
            resource_id=str(alert.id),
            resource_name=alert.title,
            request=request,
        )
        
        return AlertResponse.model_validate(alert)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{alert_id}/suppress", response_model=AlertResponse)
async def suppress_alert(
    alert_id: UUID,
    data: AlertSuppressRequest,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Suppress an alert."""
    try:
        alert_service = AlertService(db)
        alert = await alert_service.suppress_alert(
            alert_id=alert_id,
            organization_id=current_org.id,
            reason=data.reason,
            duration_hours=data.duration_hours,
        )
        return AlertResponse.model_validate(alert)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{alert_id}/create-incident", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident_from_alert(
    alert_id: UUID,
    data: AlertCreateIncidentRequest,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """Create an incident from an alert."""
    try:
        alert_service = AlertService(db)
        incident = await alert_service.create_incident_from_alert(
            alert_id=alert_id,
            organization_id=current_org.id,
            user_id=current_user.id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            severity=data.severity,
            assigned_team_id=data.assigned_team_id,
        )
        return IncidentResponse.model_validate(incident)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

