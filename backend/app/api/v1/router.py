from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    incidents,
    alerts,
    organizations,
    ai,
    notifications,
    audit_logs,
    websocket,
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(incidents.router)
api_router.include_router(alerts.router)
api_router.include_router(ai.router)
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"],
)
api_router.include_router(
    audit_logs.router,
    prefix="/audit-logs",
    tags=["Audit Logs"],
)
api_router.include_router(
    websocket.router,
    tags=["WebSocket"],
)
