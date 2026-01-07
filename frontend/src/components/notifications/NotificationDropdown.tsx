import React, { useState } from 'react';
import {
    Dropdown,
    Badge,
    Button,
    List,
    Typography,
    Space,
    Avatar,
    Tag,
    Empty,
    Spin,
    Divider,
} from 'antd';
import {
    BellOutlined,
    CheckOutlined,
    DeleteOutlined,
    ExclamationCircleOutlined,
    InfoCircleOutlined,
    WarningOutlined,
    CheckCircleOutlined,
    AlertOutlined,
    IssuesCloseOutlined,
    SettingOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import {
    useGetNotificationsQuery,
    useMarkNotificationReadMutation,
    useMarkAllReadMutation,
    useDeleteNotificationMutation,
    type Notification,
} from '../../store/api/notificationsApi';

const { Text, Title } = Typography;

const getNotificationIcon = (type: string) => {
    switch (type) {
        case 'error':
            return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
        case 'warning':
            return <WarningOutlined style={{ color: '#faad14' }} />;
        case 'success':
            return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
        case 'alert':
            return <AlertOutlined style={{ color: '#ff7a45' }} />;
        case 'incident':
            return <IssuesCloseOutlined style={{ color: '#f759ab' }} />;
        case 'system':
            return <SettingOutlined style={{ color: '#722ed1' }} />;
        default:
            return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
    }
};

const getPriorityColor = (priority: string) => {
    switch (priority) {
        case 'urgent':
            return 'red';
        case 'high':
            return 'orange';
        case 'medium':
            return 'blue';
        case 'low':
            return 'default';
        default:
            return 'default';
    }
};

const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
};

const NotificationDropdown: React.FC = () => {
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);

    const {
        data: notificationsData,
        isLoading,
        refetch,
    } = useGetNotificationsQuery({
        page: 1,
        page_size: 10,
    });

    const [markRead] = useMarkNotificationReadMutation();
    const [markAllRead] = useMarkAllReadMutation();
    const [deleteNotification] = useDeleteNotificationMutation();

    const handleNotificationClick = async (notification: Notification) => {
        // Mark as read if not already read
        if (!notification.is_read) {
            await markRead(notification.id);
        }

        // Navigate to action URL if available
        if (notification.action_url) {
            navigate(notification.action_url);
        }

        setOpen(false);
    };

    const handleMarkAllRead = async () => {
        await markAllRead();
        refetch();
    };

    const handleDelete = async (e: React.MouseEvent, notificationId: string) => {
        e.stopPropagation();
        await deleteNotification(notificationId);
        refetch();
    };

    const unreadCount = notificationsData?.unread_count || 0;
    const notifications = notificationsData?.items || [];

    const dropdownContent = (
        <div style={{ width: 400, maxHeight: 500, overflow: 'hidden' }}>
            <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Title level={5} style={{ margin: 0 }}>
                        Notifications
                    </Title>
                    {unreadCount > 0 && (
                        <Button
                            type="link"
                            size="small"
                            icon={<CheckOutlined />}
                            onClick={handleMarkAllRead}
                        >
                            Mark all read
                        </Button>
                    )}
                </div>
            </div>

            <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                {isLoading ? (
                    <div style={{ padding: 24, textAlign: 'center' }}>
                        <Spin />
                    </div>
                ) : notifications.length === 0 ? (
                    <Empty
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                        description="No notifications"
                        style={{ padding: 24 }}
                    />
                ) : (
                    <List
                        dataSource={notifications}
                        renderItem={(notification) => (
                            <List.Item
                                style={{
                                    padding: '12px 16px',
                                    cursor: 'pointer',
                                    backgroundColor: notification.is_read ? 'transparent' : '#f6ffed',
                                    borderBottom: '1px solid #f0f0f0',
                                }}
                                onClick={() => handleNotificationClick(notification)}
                                actions={[
                                    <Button
                                        type="text"
                                        size="small"
                                        icon={<DeleteOutlined />}
                                        onClick={(e) => handleDelete(e, notification.id)}
                                        style={{ color: '#999' }}
                                    />,
                                ]}
                            >
                                <List.Item.Meta
                                    avatar={
                                        <Avatar
                                            icon={getNotificationIcon(notification.type)}
                                            style={{ backgroundColor: 'transparent' }}
                                        />
                                    }
                                    title={
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                            <Text strong={!notification.is_read} style={{ flex: 1 }}>
                                                {notification.title}
                                            </Text>
                                            <Tag color={getPriorityColor(notification.priority)} size="small">
                                                {notification.priority}
                                            </Tag>
                                        </div>
                                    }
                                    description={
                                        <Space direction="vertical" size={4} style={{ width: '100%' }}>
                                            <Text type="secondary" style={{ fontSize: 12 }}>
                                                {notification.message}
                                            </Text>
                                            <Text type="secondary" style={{ fontSize: 11 }}>
                                                {formatTimeAgo(notification.created_at)}
                                            </Text>
                                        </Space>
                                    }
                                />
                            </List.Item>
                        )}
                    />
                )}
            </div>

            {notifications.length > 0 && (
                <>
                    <Divider style={{ margin: 0 }} />
                    <div style={{ padding: '8px 16px', textAlign: 'center' }}>
                        <Button
                            type="link"
                            size="small"
                            onClick={() => {
                                navigate('/notifications');
                                setOpen(false);
                            }}
                        >
                            View all notifications
                        </Button>
                    </div>
                </>
            )}
        </div>
    );

    return (
        <Dropdown
            open={open}
            onOpenChange={setOpen}
            dropdownRender={() => dropdownContent}
            placement="bottomRight"
            trigger={['click']}
        >
            <Badge count={unreadCount} size="small">
                <Button
                    type="text"
                    icon={<BellOutlined style={{ fontSize: 18 }} />}
                    style={{ border: 'none' }}
                />
            </Badge>
        </Dropdown>
    );
};

export default NotificationDropdown;