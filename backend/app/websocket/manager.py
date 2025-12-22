"""WebSocket connection manager for real-time updates."""
import json
from typing import Optional
from fastapi import WebSocket
from datetime import datetime
import asyncio

from app.config.logging import get_logger
from .events import WebSocketEvent, EventType

logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        # Active connections: {organization_id: {user_id: [WebSocket, ...]}}
        self.active_connections: dict[str, dict[str, list[WebSocket]]] = {}
        # Channel subscriptions: {channel: set(websocket_ids)}
        self.channel_subscriptions: dict[str, set[str]] = {}
        # WebSocket to ID mapping
        self.websocket_ids: dict[WebSocket, str] = {}
        # Connection count
        self.connection_count = 0

    async def connect(
        self,
        websocket: WebSocket,
        organization_id: str,
        user_id: str
    ) -> str:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()

        # Generate unique connection ID
        self.connection_count += 1
        ws_id = f"{organization_id}:{user_id}:{self.connection_count}"
        self.websocket_ids[websocket] = ws_id

        # Register connection
        if organization_id not in self.active_connections:
            self.active_connections[organization_id] = {}

        if user_id not in self.active_connections[organization_id]:
            self.active_connections[organization_id][user_id] = []

        self.active_connections[organization_id][user_id].append(websocket)

        # Subscribe to default channels
        await self.subscribe(websocket, f"org:{organization_id}")
        await self.subscribe(websocket, f"user:{user_id}")

        logger.info(f"WebSocket connected: {ws_id}")

        # Send connection confirmation
        await self.send_personal_message(
            websocket,
            WebSocketEvent(
                event_type=EventType.CONNECTED,
                data={"connection_id": ws_id, "timestamp": datetime.utcnow().isoformat()}
            )
        )

        return ws_id

    def disconnect(self, websocket: WebSocket, organization_id: str, user_id: str):
        """Remove a WebSocket connection."""
        ws_id = self.websocket_ids.get(websocket, "unknown")

        # Remove from active connections
        if organization_id in self.active_connections:
            if user_id in self.active_connections[organization_id]:
                if websocket in self.active_connections[organization_id][user_id]:
                    self.active_connections[organization_id][user_id].remove(websocket)

                # Clean up empty user list
                if not self.active_connections[organization_id][user_id]:
                    del self.active_connections[organization_id][user_id]

            # Clean up empty organization
            if not self.active_connections[organization_id]:
                del self.active_connections[organization_id]

        # Remove from subscriptions
        for channel, subscribers in self.channel_subscriptions.items():
            subscribers.discard(ws_id)

        # Remove ID mapping
        if websocket in self.websocket_ids:
            del self.websocket_ids[websocket]

        logger.info(f"WebSocket disconnected: {ws_id}")

    async def subscribe(self, websocket: WebSocket, channel: str):
        """Subscribe a WebSocket to a channel."""
        ws_id = self.websocket_ids.get(websocket)
        if ws_id:
            if channel not in self.channel_subscriptions:
                self.channel_subscriptions[channel] = set()
            self.channel_subscriptions[channel].add(ws_id)
            logger.debug(f"WebSocket {ws_id} subscribed to {channel}")

    async def unsubscribe(self, websocket: WebSocket, channel: str):
        """Unsubscribe a WebSocket from a channel."""
        ws_id = self.websocket_ids.get(websocket)
        if ws_id and channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(ws_id)
            logger.debug(f"WebSocket {ws_id} unsubscribed from {channel}")

    async def send_personal_message(self, websocket: WebSocket, event: WebSocketEvent):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(event.model_dump(mode="json"))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_organization(
        self,
        organization_id: str,
        event: WebSocketEvent,
        exclude_user: Optional[str] = None
    ):
        """Broadcast a message to all connections in an organization."""
        if organization_id not in self.active_connections:
            return

        event.organization_id = organization_id
        tasks = []

        for user_id, connections in self.active_connections[organization_id].items():
            if exclude_user and user_id == exclude_user:
                continue

            for websocket in connections:
                tasks.append(self._safe_send(websocket, event))

        if tasks:
            await asyncio.gather(*tasks)
            logger.debug(f"Broadcast to org {organization_id}: {event.event_type}")

    async def broadcast_to_user(self, user_id: str, event: WebSocketEvent):
        """Broadcast a message to all connections of a specific user."""
        event.user_id = user_id
        tasks = []

        for org_connections in self.active_connections.values():
            if user_id in org_connections:
                for websocket in org_connections[user_id]:
                    tasks.append(self._safe_send(websocket, event))

        if tasks:
            await asyncio.gather(*tasks)
            logger.debug(f"Broadcast to user {user_id}: {event.event_type}")

    async def broadcast_to_channel(self, channel: str, event: WebSocketEvent):
        """Broadcast a message to all subscribers of a channel."""
        if channel not in self.channel_subscriptions:
            return

        tasks = []
        for ws_id in self.channel_subscriptions[channel]:
            # Find websocket by ID
            for websocket, stored_id in self.websocket_ids.items():
                if stored_id == ws_id:
                    tasks.append(self._safe_send(websocket, event))
                    break

        if tasks:
            await asyncio.gather(*tasks)
            logger.debug(f"Broadcast to channel {channel}: {event.event_type}")

    async def broadcast_global(self, event: WebSocketEvent):
        """Broadcast a message to all connected clients."""
        tasks = []

        for org_connections in self.active_connections.values():
            for user_connections in org_connections.values():
                for websocket in user_connections:
                    tasks.append(self._safe_send(websocket, event))

        if tasks:
            await asyncio.gather(*tasks)
            logger.debug(f"Global broadcast: {event.event_type}")

    async def _safe_send(self, websocket: WebSocket, event: WebSocketEvent):
        """Safely send a message, handling errors."""
        try:
            await websocket.send_json(event.model_dump(mode="json"))
        except Exception as e:
            logger.error(f"Error sending to websocket: {e}")

    def get_connection_count(self, organization_id: Optional[str] = None) -> int:
        """Get the number of active connections."""
        if organization_id:
            if organization_id in self.active_connections:
                return sum(
                    len(connections)
                    for connections in self.active_connections[organization_id].values()
                )
            return 0

        return sum(
            len(connections)
            for org in self.active_connections.values()
            for connections in org.values()
        )

    def get_online_users(self, organization_id: str) -> list[str]:
        """Get list of online user IDs in an organization."""
        if organization_id in self.active_connections:
            return list(self.active_connections[organization_id].keys())
        return []


# Global WebSocket manager instance
websocket_manager = ConnectionManager()
