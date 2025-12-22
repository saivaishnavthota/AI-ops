# WebSocket module for real-time updates
from .manager import ConnectionManager, websocket_manager
from .events import WebSocketEvent, EventType

__all__ = ["ConnectionManager", "websocket_manager", "WebSocketEvent", "EventType"]
