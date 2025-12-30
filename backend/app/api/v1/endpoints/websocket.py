"""WebSocket endpoint for real-time updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import json
import asyncio

from app.config.logging import get_logger
from app.websocket.manager import websocket_manager
from app.websocket.handlers import handle_websocket_message
from app.core.jwt import verify_token

logger = get_logger(__name__)
router = APIRouter()

# Authentication timeout in seconds
AUTH_TIMEOUT_SECONDS = 10


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time updates.

    Authentication methods (in order of preference):
    1. Message-based (RECOMMENDED): Connect without token, then send authenticate message
       ws://host/api/v1/ws
       First message: {"action": "authenticate", "data": {"token": "<jwt_token>"}}

    2. Query parameter (DEPRECATED - token visible in logs):
       ws://host/api/v1/ws?token=<jwt_token>

    Message format:
    {
        "action": "subscribe" | "unsubscribe" | "ping" | "get_online_users" | "authenticate",
        "data": { ... }
    }

    Channels:
    - org:<organization_id> - Organization-wide events
    - user:<user_id> - User-specific events
    - alerts - All alert events
    - incidents - All incident events
    - playbooks - Playbook execution events
    """
    # Accept the WebSocket connection first
    await websocket.accept()

    user_id = None
    organization_id = None
    connection_id = None
    is_authenticated = False

    # Check for token in query parameter (legacy, deprecated)
    if token:
        logger.warning(
            "WebSocket authentication via URL query parameter is deprecated. "
            "Use message-based authentication instead for security."
        )
        payload = verify_token(token, "access")
        if payload:
            user_id = payload.get("sub")
            organization_id = payload.get("org", "default")
            is_authenticated = True
            connection_id = await websocket_manager.connect(websocket, organization_id, user_id)

    # If not authenticated via query param, wait for authenticate message
    if not is_authenticated:
        try:
            # Wait for authentication message with timeout
            data = await asyncio.wait_for(
                websocket.receive_text(),
                timeout=AUTH_TIMEOUT_SECONDS
            )
            message = json.loads(data)

            if message.get("action") == "authenticate":
                auth_token = message.get("data", {}).get("token")
                if auth_token:
                    payload = verify_token(auth_token, "access")
                    if payload:
                        user_id = payload.get("sub")
                        organization_id = payload.get("org", "default")
                        is_authenticated = True
                        connection_id = await websocket_manager.connect(websocket, organization_id, user_id)
                        # Send authentication success
                        await websocket.send_json({
                            "event_type": "authenticated",
                            "data": {"success": True, "user_id": user_id},
                            "timestamp": None
                        })
                    else:
                        await websocket.send_json({
                            "event_type": "error",
                            "data": {"code": 4002, "message": "Invalid authentication token"},
                            "timestamp": None
                        })
                        await websocket.close(code=4002, reason="Invalid authentication token")
                        return
                else:
                    await websocket.send_json({
                        "event_type": "error",
                        "data": {"code": 4001, "message": "Missing token in authenticate message"},
                        "timestamp": None
                    })
                    await websocket.close(code=4001, reason="Missing token")
                    return
            else:
                await websocket.send_json({
                    "event_type": "error",
                    "data": {"code": 4003, "message": "First message must be authenticate"},
                    "timestamp": None
                })
                await websocket.close(code=4003, reason="Authentication required")
                return

        except asyncio.TimeoutError:
            logger.warning("WebSocket authentication timeout")
            await websocket.close(code=4004, reason="Authentication timeout")
            return
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in authentication message")
            await websocket.close(code=4005, reason="Invalid message format")
            return
        except Exception as e:
            logger.error(f"WebSocket authentication error: {e}")
            await websocket.close(code=4000, reason="Authentication failed")
            return

    if not is_authenticated:
        await websocket.close(code=4001, reason="Authentication required")
        return

    try:
        while True:
            # Receive and process messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Skip authenticate action for already authenticated connections
                if message.get("action") == "authenticate":
                    await websocket.send_json({
                        "event_type": "info",
                        "data": {"message": "Already authenticated"},
                        "timestamp": None
                    })
                    continue
                await handle_websocket_message(websocket, message, organization_id, user_id)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {data[:100]}")
            except Exception as e:
                logger.error(f"Error handling message: {e}")

    except WebSocketDisconnect:
        if connection_id:
            websocket_manager.disconnect(websocket, organization_id, user_id)
            logger.info(f"WebSocket disconnected: {connection_id}")


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status."""
    return {
        "total_connections": websocket_manager.get_connection_count(),
        "channels": list(websocket_manager.channel_subscriptions.keys()),
    }
