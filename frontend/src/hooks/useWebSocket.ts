/**
 * React hook for WebSocket integration
 */
import { useEffect, useCallback, useState } from 'react';
import { useSelector } from 'react-redux';
import { websocketService, WebSocketEvent, EventType } from '../services/websocket';
import { RootState } from '../app/store';

export function useWebSocket() {
  const token = useSelector((state: RootState) => state.auth.accessToken);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (token) {
      websocketService.connect(token);

      const unsubscribeConnected = websocketService.on('connected', () => {
        setIsConnected(true);
      });

      const unsubscribeDisconnected = websocketService.on('disconnected', () => {
        setIsConnected(false);
      });

      return () => {
        unsubscribeConnected();
        unsubscribeDisconnected();
        websocketService.disconnect();
      };
    }
  }, [token]);

  const subscribe = useCallback((channel: string) => {
    websocketService.subscribe(channel);
  }, []);

  const unsubscribe = useCallback((channel: string) => {
    websocketService.unsubscribe(channel);
  }, []);

  return {
    isConnected,
    subscribe,
    unsubscribe,
    ping: websocketService.ping.bind(websocketService),
    getOnlineUsers: websocketService.getOnlineUsers.bind(websocketService),
  };
}

export function useWebSocketEvent(
  eventType: EventType | 'all',
  handler: (event: WebSocketEvent) => void,
  deps: React.DependencyList = []
) {
  useEffect(() => {
    const unsubscribe = websocketService.on(eventType, handler);
    return unsubscribe;
  }, [eventType, ...deps]);
}

export function useIncidentUpdates(onUpdate: (data: Record<string, unknown>) => void) {
  useWebSocketEvent('incident.created', (event) => onUpdate(event.data), [onUpdate]);
  useWebSocketEvent('incident.updated', (event) => onUpdate(event.data), [onUpdate]);
  useWebSocketEvent('incident.resolved', (event) => onUpdate(event.data), [onUpdate]);
}

export function useAlertUpdates(onUpdate: (data: Record<string, unknown>) => void) {
  useWebSocketEvent('alert.created', (event) => onUpdate(event.data), [onUpdate]);
  useWebSocketEvent('alert.updated', (event) => onUpdate(event.data), [onUpdate]);
  useWebSocketEvent('alert.resolved', (event) => onUpdate(event.data), [onUpdate]);
}

export function useNotificationUpdates(onNewNotification: (data: Record<string, unknown>) => void) {
  useWebSocketEvent('notification.new', (event) => onNewNotification(event.data), [onNewNotification]);
}

export function usePlaybookUpdates(onUpdate: (data: Record<string, unknown>) => void) {
  useWebSocketEvent('playbook.started', (event) => onUpdate(event.data), [onUpdate]);
  useWebSocketEvent('playbook.completed', (event) => onUpdate(event.data), [onUpdate]);
  useWebSocketEvent('playbook.failed', (event) => onUpdate(event.data), [onUpdate]);
}

export function useAIUpdates(onUpdate: (data: Record<string, unknown>) => void) {
  useWebSocketEvent('ai.prediction', (event) => onUpdate(event.data), [onUpdate]);
  useWebSocketEvent('ai.analysis_complete', (event) => onUpdate(event.data), [onUpdate]);
  useWebSocketEvent('ai.recommendation', (event) => onUpdate(event.data), [onUpdate]);
}
