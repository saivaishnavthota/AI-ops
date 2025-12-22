import React, { useState } from 'react';
import { Badge, Dropdown, List, Typography, Space, Tag, Button, Empty, Spin, message } from 'antd';
import { BellOutlined, CheckOutlined, InfoCircleOutlined, WarningOutlined, CloseCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useNotificationUpdates } from '../../hooks/useWebSocket';

const { Text, Paragraph } = Typography;

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success' | 'alert' | 'incident' | 'system';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  is_read: boolean;
  read_at?: string;
  action_url?: string;
  action_label?: string;
  related_entity_type?: string;
  related_entity_id?: string;
  created_at: string;
}

// Mock notifications for demo
const mockNotifications: Notification[] = [
  {
    id: '1',
    title: 'Critical Alert Triggered',
    message: 'High CPU usage detected on prod-server-01. Current usage: 95%',
    type: 'alert',
    priority: 'urgent',
    is_read: false,
    created_at: new Date(Date.now() - 5 * 60000).toISOString(),
    action_url: '/alerts',
    action_label: 'View Alert',
  },
  {
    id: '2',
    title: 'Incident Created',
    message: 'New P1 incident INC-2025-001: Database connection failures',
    type: 'incident',
    priority: 'high',
    is_read: false,
    created_at: new Date(Date.now() - 15 * 60000).toISOString(),
    action_url: '/incidents',
    action_label: 'View Incident',
  },
  {
    id: '3',
    title: 'Playbook Executed Successfully',
    message: 'Auto-scaling playbook completed. Added 2 instances to the cluster.',
    type: 'success',
    priority: 'medium',
    is_read: true,
    read_at: new Date(Date.now() - 20 * 60000).toISOString(),
    created_at: new Date(Date.now() - 30 * 60000).toISOString(),
  },
  {
    id: '4',
    title: 'AI Prediction Alert',
    message: 'Predicted disk space exhaustion on prod-db-01 within 5 days',
    type: 'warning',
    priority: 'high',
    is_read: false,
    created_at: new Date(Date.now() - 60 * 60000).toISOString(),
    action_url: '/predictions',
    action_label: 'View Prediction',
  },
  {
    id: '5',
    title: 'System Maintenance Scheduled',
    message: 'Scheduled maintenance window: Dec 25, 2025 02:00-04:00 UTC',
    type: 'info',
    priority: 'low',
    is_read: true,
    read_at: new Date(Date.now() - 2 * 60 * 60000).toISOString(),
    created_at: new Date(Date.now() - 24 * 60 * 60000).toISOString(),
  },
];

const typeIcons: Record<string, React.ReactNode> = {
  info: <InfoCircleOutlined style={{ color: '#1890ff' }} />,
  warning: <WarningOutlined style={{ color: '#faad14' }} />,
  error: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
  success: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
  alert: <WarningOutlined style={{ color: '#ff4d4f' }} />,
  incident: <WarningOutlined style={{ color: '#fa8c16' }} />,
  system: <InfoCircleOutlined style={{ color: '#722ed1' }} />,
};

const priorityColors: Record<string, string> = {
  low: 'default',
  medium: 'blue',
  high: 'orange',
  urgent: 'red',
};

const NotificationCenter: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);
  const [open, setOpen] = useState(false);
  const loading = false; // Would be set by API call

  const unreadCount = notifications.filter(n => !n.is_read).length;

  // Listen for real-time notifications
  useNotificationUpdates((data) => {
    const newNotification = data as unknown as Notification;
    setNotifications(prev => [newNotification, ...prev]);
    message.info({
      content: newNotification.title,
      icon: typeIcons[newNotification.type],
    });
  });

  const handleMarkAsRead = (id: string) => {
    setNotifications(notifications.map(n =>
      n.id === id ? { ...n, is_read: true, read_at: new Date().toISOString() } : n
    ));
  };

  const handleMarkAllAsRead = () => {
    setNotifications(notifications.map(n => ({
      ...n,
      is_read: true,
      read_at: n.read_at || new Date().toISOString(),
    })));
    message.success('All notifications marked as read');
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const dropdownContent = (
    <div style={{ width: 380, maxHeight: 500, overflow: 'auto', background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.15)' }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Text strong>Notifications</Text>
        {unreadCount > 0 && (
          <Button type="link" size="small" onClick={handleMarkAllAsRead}>
            Mark all as read
          </Button>
        )}
      </div>

      {loading ? (
        <div style={{ padding: 40, textAlign: 'center' }}>
          <Spin />
        </div>
      ) : notifications.length === 0 ? (
        <Empty description="No notifications" style={{ padding: 40 }} />
      ) : (
        <List
          dataSource={notifications}
          renderItem={(notification) => (
            <List.Item
              style={{
                padding: '12px 16px',
                background: notification.is_read ? 'transparent' : 'rgba(24, 144, 255, 0.05)',
                cursor: 'pointer',
              }}
              onClick={() => !notification.is_read && handleMarkAsRead(notification.id)}
            >
              <List.Item.Meta
                avatar={typeIcons[notification.type]}
                title={
                  <Space>
                    <Text strong={!notification.is_read}>{notification.title}</Text>
                    <Tag color={priorityColors[notification.priority]} style={{ fontSize: 10 }}>
                      {notification.priority.toUpperCase()}
                    </Tag>
                  </Space>
                }
                description={
                  <div>
                    <Paragraph ellipsis={{ rows: 2 }} style={{ marginBottom: 4, fontSize: 12, color: '#666' }}>
                      {notification.message}
                    </Paragraph>
                    <Space>
                      <Text type="secondary" style={{ fontSize: 11 }}>
                        {formatTime(notification.created_at)}
                      </Text>
                      {notification.action_url && (
                        <Button type="link" size="small" style={{ padding: 0, height: 'auto', fontSize: 11 }}>
                          {notification.action_label || 'View'}
                        </Button>
                      )}
                    </Space>
                  </div>
                }
              />
              {!notification.is_read && (
                <Button
                  type="text"
                  size="small"
                  icon={<CheckOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleMarkAsRead(notification.id);
                  }}
                />
              )}
            </List.Item>
          )}
        />
      )}

      <div style={{ padding: '8px 16px', borderTop: '1px solid #f0f0f0', textAlign: 'center' }}>
        <Button type="link" size="small">View All Notifications</Button>
      </div>
    </div>
  );

  return (
    <Dropdown
      overlay={dropdownContent}
      trigger={['click']}
      open={open}
      onOpenChange={setOpen}
      placement="bottomRight"
    >
      <Badge count={unreadCount} size="small" offset={[-2, 2]}>
        <Button
          type="text"
          icon={<BellOutlined style={{ fontSize: 20 }} />}
          style={{ width: 40, height: 40 }}
        />
      </Badge>
    </Dropdown>
  );
};

export default NotificationCenter;
