"""WebSocket message handlers."""
from typing import Any
from fastapi import WebSocket

from app.config.logging import get_logger
from .manager import websocket_manager
from .events import WebSocketEvent, EventType

logger = get_logger(__name__)


async def handle_websocket_message(
    websocket: WebSocket,
    message: dict[str, Any],
    organization_id: str,
    user_id: str
):
    """Handle incoming WebSocket messages."""
    action = message.get("action")
    data = message.get("data", {})

    if action == "subscribe":
        channel = data.get("channel")
        if channel:
            await websocket_manager.subscribe(websocket, channel)
            await websocket_manager.send_personal_message(
                websocket,
                WebSocketEvent(
                    event_type=EventType.SYSTEM_STATUS,
                    data={"status": "subscribed", "channel": channel}
                )
            )

    elif action == "unsubscribe":
        channel = data.get("channel")
        if channel:
            await websocket_manager.unsubscribe(websocket, channel)
            await websocket_manager.send_personal_message(
                websocket,
                WebSocketEvent(
                    event_type=EventType.SYSTEM_STATUS,
                    data={"status": "unsubscribed", "channel": channel}
                )
            )

    elif action == "ping":
        await websocket_manager.send_personal_message(
            websocket,
            WebSocketEvent(
                event_type=EventType.SYSTEM_STATUS,
                data={"status": "pong"}
            )
        )

    elif action == "get_online_users":
        online_users = websocket_manager.get_online_users(organization_id)
        await websocket_manager.send_personal_message(
            websocket,
            WebSocketEvent(
                event_type=EventType.SYSTEM_STATUS,
                data={"online_users": online_users, "count": len(online_users)}
            )
        )

    else:
        logger.warning(f"Unknown WebSocket action: {action}")


# Helper functions for broadcasting events from other parts of the application

async def broadcast_incident_created(organization_id: str, incident_data: dict):
    """Broadcast incident created event."""
    await websocket_manager.broadcast_to_organization(
        organization_id,
        WebSocketEvent(
            event_type=EventType.INCIDENT_CREATED,
            data=incident_data
        )
    )


async def broadcast_incident_updated(organization_id: str, incident_data: dict):
    """Broadcast incident updated event."""
    await websocket_manager.broadcast_to_organization(
        organization_id,
        WebSocketEvent(
            event_type=EventType.INCIDENT_UPDATED,
            data=incident_data
        )
    )


async def broadcast_alert_created(organization_id: str, alert_data: dict):
    """Broadcast alert created event."""
    await websocket_manager.broadcast_to_organization(
        organization_id,
        WebSocketEvent(
            event_type=EventType.ALERT_CREATED,
            data=alert_data
        )
    )


async def broadcast_alert_resolved(organization_id: str, alert_data: dict):
    """Broadcast alert resolved event."""
    await websocket_manager.broadcast_to_organization(
        organization_id,
        WebSocketEvent(
            event_type=EventType.ALERT_RESOLVED,
            data=alert_data
        )
    )


async def broadcast_playbook_started(organization_id: str, playbook_data: dict):
    """Broadcast playbook started event."""
    await websocket_manager.broadcast_to_organization(
        organization_id,
        WebSocketEvent(
            event_type=EventType.PLAYBOOK_STARTED,
            data=playbook_data
        )
    )


async def broadcast_playbook_completed(organization_id: str, playbook_data: dict):
    """Broadcast playbook completed event."""
    await websocket_manager.broadcast_to_organization(
        organization_id,
        WebSocketEvent(
            event_type=EventType.PLAYBOOK_COMPLETED,
            data=playbook_data
        )
    )


async def broadcast_notification(user_id: str, notification_data: dict):
    """Broadcast notification to a specific user."""
    await websocket_manager.broadcast_to_user(
        user_id,
        WebSocketEvent(
            event_type=EventType.NOTIFICATION_NEW,
            data=notification_data
        )
    )


async def broadcast_ai_prediction(organization_id: str, prediction_data: dict):
    """Broadcast AI prediction event."""
    await websocket_manager.broadcast_to_organization(
        organization_id,
        WebSocketEvent(
            event_type=EventType.AI_PREDICTION,
            data=prediction_data
        )
    )


async def broadcast_resource_update(organization_id: str, resource_data: dict):
    """Broadcast resource status update."""
    await websocket_manager.broadcast_to_organization(
        organization_id,
        WebSocketEvent(
            event_type=EventType.RESOURCE_STATUS_CHANGE,
            data=resource_data
        )
    )
