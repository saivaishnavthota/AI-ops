"""WebSocket endpoint for real-time updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional
import json

from app.config.logging import get_logger
from app.websocket.manager import websocket_manager
from app.websocket.handlers import handle_websocket_message
from app.core.jwt import verify_token

logger = get_logger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time updates.

    Connect with: ws://host/api/v1/ws?token=<jwt_token>

    Message format:
    {
        "action": "subscribe" | "unsubscribe" | "ping" | "get_online_users",
        "data": { ... }
    }

    Channels:
    - org:<organization_id> - Organization-wide events
    - user:<user_id> - User-specific events
    - alerts - All alert events
    - incidents - All incident events
    - playbooks - Playbook execution events
    """
    # Validate token
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return

    payload = verify_token(token, "access")
    if not payload:
        logger.error("WebSocket auth failed: Invalid token")
        await websocket.close(code=4002, reason="Invalid authentication token")
        return

    user_id = payload.get("sub")
    organization_id = payload.get("org", "default")

    # Connect
    connection_id = await websocket_manager.connect(websocket, organization_id, user_id)

    try:
        while True:
            # Receive and process messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, message, organization_id, user_id)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {data[:100]}")
            except Exception as e:
                logger.error(f"Error handling message: {e}")

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, organization_id, user_id)
        logger.info(f"WebSocket disconnected: {connection_id}")


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status."""
    return {
        "total_connections": websocket_manager.get_connection_count(),
        "channels": list(websocket_manager.channel_subscriptions.keys()),
    }
