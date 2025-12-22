/**
 * WebSocket service for real-time updates
 */

export type EventType =
  | 'connected'
  | 'disconnected'
  | 'incident.created'
  | 'incident.updated'
  | 'incident.resolved'
  | 'incident.assigned'
  | 'alert.created'
  | 'alert.updated'
  | 'alert.resolved'
  | 'alert.escalated'
  | 'playbook.started'
  | 'playbook.completed'
  | 'playbook.failed'
  | 'playbook.step_completed'
  | 'notification.new'
  | 'notification.read'
  | 'system.status'
  | 'system.alert'
  | 'ai.prediction'
  | 'ai.analysis_complete'
  | 'ai.recommendation'
  | 'resource.status_change'
  | 'resource.metric_update';

export interface WebSocketEvent {
  event_type: EventType;
  data: Record<string, unknown>;
  timestamp: string;
  organization_id?: string;
  user_id?: string;
}

type EventHandler = (event: WebSocketEvent) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private handlers: Map<EventType | 'all', Set<EventHandler>> = new Map();
  private token: string | null = null;
  private isConnecting = false;

  connect(token: string): void {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.token = token;
    this.isConnecting = true;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/v1/ws?token=${encodeURIComponent(token)}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const wsEvent: WebSocketEvent = JSON.parse(event.data);
          this.handleEvent(wsEvent);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        this.isConnecting = false;
        this.ws = null;

        // Attempt to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts && this.token) {
          this.reconnectAttempts++;
          const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
          console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
          setTimeout(() => {
            if (this.token) {
              this.connect(this.token);
            }
          }, delay);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.isConnecting = false;
    }
  }

  disconnect(): void {
    this.token = null;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.handlers.clear();
  }

  subscribe(channel: string): void {
    this.send({
      action: 'subscribe',
      data: { channel },
    });
  }

  unsubscribe(channel: string): void {
    this.send({
      action: 'unsubscribe',
      data: { channel },
    });
  }

  ping(): void {
    this.send({ action: 'ping', data: {} });
  }

  getOnlineUsers(): void {
    this.send({ action: 'get_online_users', data: {} });
  }

  private send(message: { action: string; data: Record<string, unknown> }): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  private handleEvent(event: WebSocketEvent): void {
    // Call specific event handlers
    const specificHandlers = this.handlers.get(event.event_type);
    if (specificHandlers) {
      specificHandlers.forEach((handler) => handler(event));
    }

    // Call global handlers
    const globalHandlers = this.handlers.get('all');
    if (globalHandlers) {
      globalHandlers.forEach((handler) => handler(event));
    }
  }

  on(eventType: EventType | 'all', handler: EventHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.handlers.get(eventType)?.delete(handler);
    };
  }

  off(eventType: EventType | 'all', handler: EventHandler): void {
    this.handlers.get(eventType)?.delete(handler);
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();
export default websocketService;
