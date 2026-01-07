import React, { useState } from 'react';
import {
    Card,
    List,
    Typography,
    Space,
    Avatar,
    Tag,
    Button,
    Empty,
    Spin,
    Pagination,
    Select,
    Row,
    Col,
    Statistic,
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
    useGetNotificationStatsQuery,
    useMarkNotificationReadMutation,
    useMarkAllReadMutation,
    useDeleteNotificationMutation,
    type Notification,
} from '../../store/api/notificationsApi';

const { Title, Text } = Typography;
const { Option } = Select;

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

const NotificationsPage: React.FC = () => {
    const navigate = useNavigate();
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(20);
    const [typeFilter, setTypeFilter] = useState<string | undefined>();
    const [priorityFilter, setPriorityFilter] = useState<string | undefined>();
    const [unreadOnly, setUnreadOnly] = useState(false);

    const {
        data: notificationsData,
        isLoading,
        refetch,
    } = useGetNotificationsQuery({
        page,
        page_size: pageSize,
        type: typeFilter,
        priority: priorityFilter,
        unread_only: unreadOnly,
    });

    const { data: stats } = useGetNotificationStatsQuery();

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
    };

    const handleMarkAllRead = async () => {
        await markAllRead();
        refetch();
    };

    const handleDelete = async (notificationId: string) => {
        await deleteNotification(notificationId);
        refetch();
    };

    const notifications = notificationsData?.items || [];
    const total = notificationsData?.total || 0;
    const unreadCount = notificationsData?.unread_count || 0;

    return (
        <div style={{ padding: '24px' }}>
            <div style={{ marginBottom: 24 }}>
                <Title level={2}>Notifications</Title>

                {/* Statistics */}
                <Row gutter={16} style={{ marginBottom: 24 }}>
                    <Col span={6}>
                        <Card>
                            <Statistic
                                title="Total Notifications"
                                value={stats?.total || 0}
                                prefix={<BellOutlined />}
                            />
                        </Card>
                    </Col>
                    <Col span={6}>
                        <Card>
                            <Statistic
                                title="Unread"
                                value={stats?.unread || 0}
                                prefix={<ExclamationCircleOutlined />}
                                valueStyle={{ color: '#cf1322' }}
                            />
                        </Card>
                    </Col>
                    <Col span={6}>
                        <Card>
                            <Statistic
                                title="High Priority"
                                value={stats?.by_priority?.high || 0}
                                prefix={<WarningOutlined />}
                                valueStyle={{ color: '#fa8c16' }}
                            />
                        </Card>
                    </Col>
                    <Col span={6}>
                        <Card>
                            <Statistic
                                title="Alerts"
                                value={stats?.by_type?.alert || 0}
                                prefix={<AlertOutlined />}
                                valueStyle={{ color: '#fa541c' }}
                            />
                        </Card>
                    </Col>
                </Row>

                {/* Filters */}
                <Card style={{ marginBottom: 16 }}>
                    <Row gutter={16} align="middle">
                        <Col>
                            <Space>
                                <Text>Filters:</Text>
                                <Select
                                    placeholder="Type"
                                    style={{ width: 120 }}
                                    allowClear
                                    value={typeFilter}
                                    onChange={setTypeFilter}
                                >
                                    <Option value="info">Info</Option>
                                    <Option value="warning">Warning</Option>
                                    <Option value="error">Error</Option>
                                    <Option value="success">Success</Option>
                                    <Option value="alert">Alert</Option>
                                    <Option value="incident">Incident</Option>
                                    <Option value="system">System</Option>
                                </Select>
                                <Select
                                    placeholder="Priority"
                                    style={{ width: 120 }}
                                    allowClear
                                    value={priorityFilter}
                                    onChange={setPriorityFilter}
                                >
                                    <Option value="low">Low</Option>
                                    <Option value="medium">Medium</Option>
                                    <Option value="high">High</Option>
                                    <Option value="urgent">Urgent</Option>
                                </Select>
                                <Button
                                    type={unreadOnly ? 'primary' : 'default'}
                                    onClick={() => setUnreadOnly(!unreadOnly)}
                                >
                                    Unread Only
                                </Button>
                            </Space>
                        </Col>
                        <Col flex="auto" />
                        <Col>
                            {unreadCount > 0 && (
                                <Button
                                    type="primary"
                                    icon={<CheckOutlined />}
                                    onClick={handleMarkAllRead}
                                >
                                    Mark All Read ({unreadCount})
                                </Button>
                            )}
                        </Col>
                    </Row>
                </Card>
            </div>

            {/* Notifications List */}
            <Card>
                {isLoading ? (
                    <div style={{ textAlign: 'center', padding: 48 }}>
                        <Spin size="large" />
                    </div>
                ) : notifications.length === 0 ? (
                    <Empty
                        description="No notifications found"
                        style={{ padding: 48 }}
                    />
                ) : (
                    <>
                        <List
                            dataSource={notifications}
                            renderItem={(notification) => (
                                <List.Item
                                    style={{
                                        backgroundColor: notification.is_read ? 'transparent' : '#f6ffed',
                                        cursor: notification.action_url ? 'pointer' : 'default',
                                        padding: '16px 24px',
                                    }}
                                    onClick={() => notification.action_url && handleNotificationClick(notification)}
                                    actions={[
                                        !notification.is_read && (
                                            <Button
                                                type="text"
                                                size="small"
                                                icon={<CheckOutlined />}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    markRead(notification.id);
                                                }}
                                                title="Mark as read"
                                            />
                                        ),
                                        <Button
                                            type="text"
                                            size="small"
                                            icon={<DeleteOutlined />}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDelete(notification.id);
                                            }}
                                            title="Delete"
                                            danger
                                        />,
                                    ].filter(Boolean)}
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
                                                <Text type="secondary" style={{ fontSize: 12 }}>
                                                    {formatTimeAgo(notification.created_at)}
                                                </Text>
                                            </div>
                                        }
                                        description={
                                            <div>
                                                <Text type="secondary">{notification.message}</Text>
                                                {notification.action_label && (
                                                    <div style={{ marginTop: 8 }}>
                                                        <Button type="link" size="small" style={{ padding: 0 }}>
                                                            {notification.action_label} →
                                                        </Button>
                                                    </div>
                                                )}
                                            </div>
                                        }
                                    />
                                </List.Item>
                            )}
                        />

                        {total > pageSize && (
                            <div style={{ textAlign: 'center', marginTop: 16 }}>
                                <Pagination
                                    current={page}
                                    pageSize={pageSize}
                                    total={total}
                                    showSizeChanger
                                    showQuickJumper
                                    showTotal={(total, range) =>
                                        `${range[0]}-${range[1]} of ${total} notifications`
                                    }
                                    onChange={(newPage, newPageSize) => {
                                        setPage(newPage);
                                        if (newPageSize !== pageSize) {
                                            setPageSize(newPageSize);
                                        }
                                    }}
                                />
                            </div>
                        )}
                    </>
                )}
            </Card>
        </div>
    );
};

export default NotificationsPage;