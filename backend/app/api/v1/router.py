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
    users,
    analytics,
    cloud,
    teams,
    tickets,
    playbooks,
    predictions,
    virtual_agent,
    # Temporarily disabled until converted to async
    # security,
    # investigations,
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(incidents.router)
api_router.include_router(alerts.router)
api_router.include_router(ai.router)
api_router.include_router(analytics.router)
api_router.include_router(cloud.router)
api_router.include_router(teams.router)
api_router.include_router(tickets.router)
api_router.include_router(tickets.kb_router)
api_router.include_router(playbooks.router)
api_router.include_router(predictions.router)
api_router.include_router(virtual_agent.router)
# Temporarily disabled until converted to async
# api_router.include_router(security.router)
# api_router.include_router(investigations.router)
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
api_router.include_router(users.router)
