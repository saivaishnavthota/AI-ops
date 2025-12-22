import React, { useState } from 'react';
import { Card, Table, Tag, Typography, Space, Input, Select, DatePicker, Button, Drawer, Descriptions, Timeline, Avatar, Row, Col, Statistic } from 'antd';
import { SearchOutlined, UserOutlined, EyeOutlined, DownloadOutlined, ReloadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text, Paragraph } = Typography;
const { RangePicker } = DatePicker;

interface AuditLogEntry {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  resource_name: string;
  user_id: string;
  user_name: string;
  user_email: string;
  description: string;
  changes?: Record<string, { old: unknown; new: unknown }>;
  ip_address: string;
  user_agent: string;
  status: 'success' | 'failed';
  error_message?: string;
  created_at: string;
}

const mockAuditLogs: AuditLogEntry[] = [
  {
    id: '1',
    action: 'incident.created',
    resource_type: 'incident',
    resource_id: 'INC-2025-001',
    resource_name: 'Database Connection Failure',
    user_id: '1',
    user_name: 'Alex Chen',
    user_email: 'alex.chen@example.com',
    description: 'Created new incident: Database Connection Failure',
    ip_address: '192.168.1.100',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    status: 'success',
    created_at: '2025-12-22T10:30:00Z',
  },
  {
    id: '2',
    action: 'incident.assigned',
    resource_type: 'incident',
    resource_id: 'INC-2025-001',
    resource_name: 'Database Connection Failure',
    user_id: '2',
    user_name: 'Sarah Johnson',
    user_email: 'sarah.johnson@example.com',
    description: 'Assigned incident to Mike Wilson',
    changes: {
      assigned_user_id: { old: null, new: 'Mike Wilson' },
    },
    ip_address: '192.168.1.101',
    user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    status: 'success',
    created_at: '2025-12-22T10:35:00Z',
  },
  {
    id: '3',
    action: 'alert.acknowledged',
    resource_type: 'alert',
    resource_id: 'ALT-5678',
    resource_name: 'High CPU Usage Alert',
    user_id: '3',
    user_name: 'Mike Wilson',
    user_email: 'mike.wilson@example.com',
    description: 'Acknowledged alert: High CPU Usage',
    changes: {
      status: { old: 'active', new: 'acknowledged' },
    },
    ip_address: '192.168.1.102',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    status: 'success',
    created_at: '2025-12-22T10:40:00Z',
  },
  {
    id: '4',
    action: 'playbook.executed',
    resource_type: 'playbook',
    resource_id: 'PB-001',
    resource_name: 'Auto-Scale Cluster',
    user_id: '1',
    user_name: 'Alex Chen',
    user_email: 'alex.chen@example.com',
    description: 'Executed playbook: Auto-Scale Cluster',
    ip_address: '192.168.1.100',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    status: 'success',
    created_at: '2025-12-22T10:45:00Z',
  },
  {
    id: '5',
    action: 'user.role_changed',
    resource_type: 'user',
    resource_id: 'USR-123',
    resource_name: 'John Smith',
    user_id: '2',
    user_name: 'Sarah Johnson',
    user_email: 'sarah.johnson@example.com',
    description: 'Changed user role from Viewer to Operator',
    changes: {
      role: { old: 'viewer', new: 'operator' },
    },
    ip_address: '192.168.1.101',
    user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    status: 'success',
    created_at: '2025-12-22T09:30:00Z',
  },
  {
    id: '6',
    action: 'integration.configured',
    resource_type: 'integration',
    resource_id: 'INT-SLACK',
    resource_name: 'Slack Integration',
    user_id: '2',
    user_name: 'Sarah Johnson',
    user_email: 'sarah.johnson@example.com',
    description: 'Updated Slack integration configuration',
    changes: {
      channel: { old: '#alerts', new: '#ops-alerts' },
    },
    ip_address: '192.168.1.101',
    user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    status: 'success',
    created_at: '2025-12-22T09:00:00Z',
  },
  {
    id: '7',
    action: 'login',
    resource_type: 'auth',
    resource_id: '',
    resource_name: '',
    user_id: '1',
    user_name: 'Alex Chen',
    user_email: 'alex.chen@example.com',
    description: 'User logged in successfully',
    ip_address: '192.168.1.100',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    status: 'success',
    created_at: '2025-12-22T08:00:00Z',
  },
  {
    id: '8',
    action: 'login_failed',
    resource_type: 'auth',
    resource_id: '',
    resource_name: '',
    user_id: '',
    user_name: 'Unknown',
    user_email: 'unknown@example.com',
    description: 'Failed login attempt',
    error_message: 'Invalid credentials',
    ip_address: '10.0.0.50',
    user_agent: 'curl/7.68.0',
    status: 'failed',
    created_at: '2025-12-22T07:45:00Z',
  },
  {
    id: '9',
    action: 'incident.resolved',
    resource_type: 'incident',
    resource_id: 'INC-2025-001',
    resource_name: 'Database Connection Failure',
    user_id: '3',
    user_name: 'Mike Wilson',
    user_email: 'mike.wilson@example.com',
    description: 'Resolved incident: Database Connection Failure',
    changes: {
      status: { old: 'in_progress', new: 'resolved' },
    },
    ip_address: '192.168.1.102',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    status: 'success',
    created_at: '2025-12-22T11:30:00Z',
  },
  {
    id: '10',
    action: 'resource.stopped',
    resource_type: 'cloud_resource',
    resource_id: 'i-0abc123',
    resource_name: 'dev-server-01',
    user_id: '1',
    user_name: 'Alex Chen',
    user_email: 'alex.chen@example.com',
    description: 'Stopped EC2 instance: dev-server-01',
    changes: {
      state: { old: 'running', new: 'stopped' },
    },
    ip_address: '192.168.1.100',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    status: 'success',
    created_at: '2025-12-21T18:00:00Z',
  },
];

const actionColors: Record<string, string> = {
  'incident.created': 'blue',
  'incident.updated': 'cyan',
  'incident.assigned': 'purple',
  'incident.resolved': 'green',
  'incident.closed': 'default',
  'alert.created': 'orange',
  'alert.acknowledged': 'blue',
  'alert.resolved': 'green',
  'playbook.executed': 'magenta',
  'user.role_changed': 'gold',
  'integration.configured': 'cyan',
  'resource.stopped': 'volcano',
  'resource.started': 'green',
  login: 'green',
  login_failed: 'red',
  logout: 'default',
};

const resourceTypes = ['All', 'incident', 'alert', 'playbook', 'user', 'integration', 'cloud_resource', 'auth'];
const actions = ['All', 'Created', 'Updated', 'Assigned', 'Resolved', 'Executed', 'Login', 'Login Failed'];

const AuditLogPage: React.FC = () => {
  const [searchText, setSearchText] = useState('');
  const [selectedResourceType, setSelectedResourceType] = useState('All');
  const [selectedAction, setSelectedAction] = useState('All');
  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [selectedLog, setSelectedLog] = useState<AuditLogEntry | null>(null);
  const [loading, setLoading] = useState(false);

  const filteredLogs = mockAuditLogs.filter((log) => {
    const matchesSearch = !searchText ||
      log.description.toLowerCase().includes(searchText.toLowerCase()) ||
      log.user_name.toLowerCase().includes(searchText.toLowerCase()) ||
      log.resource_name.toLowerCase().includes(searchText.toLowerCase());
    const matchesResourceType = selectedResourceType === 'All' || log.resource_type === selectedResourceType;
    const matchesAction = selectedAction === 'All' ||
      log.action.toLowerCase().includes(selectedAction.toLowerCase());
    return matchesSearch && matchesResourceType && matchesAction;
  });

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 1000);
  };

  const handleExport = () => {
    const csvContent = [
      ['Timestamp', 'User', 'Action', 'Resource Type', 'Resource', 'Status', 'IP Address'],
      ...filteredLogs.map(log => [
        log.created_at,
        log.user_name,
        log.action,
        log.resource_type,
        log.resource_name,
        log.status,
        log.ip_address,
      ]),
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-log-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const columns: ColumnsType<AuditLogEntry> = [
    {
      title: 'Timestamp',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date) => new Date(date).toLocaleString(),
      sorter: (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
      defaultSortOrder: 'descend',
    },
    {
      title: 'User',
      dataIndex: 'user_name',
      key: 'user_name',
      width: 150,
      render: (name, record) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          <div>
            <div>{name}</div>
            <Text type="secondary" style={{ fontSize: 11 }}>{record.user_email}</Text>
          </div>
        </Space>
      ),
    },
    {
      title: 'Action',
      dataIndex: 'action',
      key: 'action',
      width: 150,
      render: (action) => (
        <Tag color={actionColors[action] || 'default'}>{action.replace(/\./g, ' ').replace(/_/g, ' ').toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Resource',
      key: 'resource',
      render: (_, record) => (
        <div>
          <Tag>{record.resource_type}</Tag>
          {record.resource_name && <Text>{record.resource_name}</Text>}
          {record.resource_id && (
            <div><Text type="secondary" style={{ fontSize: 11 }}>{record.resource_id}</Text></div>
          )}
        </div>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={status === 'success' ? 'green' : 'red'}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'IP Address',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 130,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 80,
      render: (_, record) => (
        <Button
          type="text"
          icon={<EyeOutlined />}
          onClick={() => {
            setSelectedLog(record);
            setIsDetailDrawerOpen(true);
          }}
        />
      ),
    },
  ];

  // Calculate stats
  const todayLogs = mockAuditLogs.filter(
    log => new Date(log.created_at).toDateString() === new Date().toDateString()
  );
  const failedActions = mockAuditLogs.filter(log => log.status === 'failed').length;
  const uniqueUsers = new Set(mockAuditLogs.map(log => log.user_id)).size;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Audit Log</Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh} loading={loading}>
            Refresh
          </Button>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>
            Export
          </Button>
        </Space>
      </div>

      {/* Stats */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic title="Total Actions Today" value={todayLogs.length} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic title="Failed Actions" value={failedActions} valueStyle={{ color: failedActions > 0 ? '#ff4d4f' : '#52c41a' }} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic title="Active Users" value={uniqueUsers} />
          </Card>
        </Col>
      </Row>

      {/* Filters */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Input
            placeholder="Search logs..."
            prefix={<SearchOutlined />}
            style={{ width: 250 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <Select
            placeholder="Resource Type"
            style={{ width: 150 }}
            value={selectedResourceType}
            onChange={setSelectedResourceType}
          >
            {resourceTypes.map(type => (
              <Select.Option key={type} value={type}>{type}</Select.Option>
            ))}
          </Select>
          <Select
            placeholder="Action"
            style={{ width: 150 }}
            value={selectedAction}
            onChange={setSelectedAction}
          >
            {actions.map(action => (
              <Select.Option key={action} value={action}>{action}</Select.Option>
            ))}
          </Select>
          <RangePicker />
        </Space>
      </Card>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredLogs}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 20, showSizeChanger: true }}
        />
      </Card>

      {/* Detail Drawer */}
      <Drawer
        title="Audit Log Details"
        open={isDetailDrawerOpen}
        onClose={() => { setIsDetailDrawerOpen(false); setSelectedLog(null); }}
        width={600}
      >
        {selectedLog && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Descriptions bordered column={1}>
              <Descriptions.Item label="Timestamp">
                {new Date(selectedLog.created_at).toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label="User">
                <Space>
                  <Avatar size="small" icon={<UserOutlined />} />
                  {selectedLog.user_name} ({selectedLog.user_email})
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="Action">
                <Tag color={actionColors[selectedLog.action] || 'default'}>
                  {selectedLog.action.toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Resource Type">
                <Tag>{selectedLog.resource_type}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Resource ID">
                {selectedLog.resource_id || 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="Resource Name">
                {selectedLog.resource_name || 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={selectedLog.status === 'success' ? 'green' : 'red'}>
                  {selectedLog.status.toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="IP Address">
                {selectedLog.ip_address}
              </Descriptions.Item>
              <Descriptions.Item label="User Agent">
                <Text ellipsis style={{ maxWidth: 400 }}>{selectedLog.user_agent}</Text>
              </Descriptions.Item>
            </Descriptions>

            <Card title="Description" size="small">
              <Paragraph>{selectedLog.description}</Paragraph>
            </Card>

            {selectedLog.changes && Object.keys(selectedLog.changes).length > 0 && (
              <Card title="Changes" size="small">
                <Timeline
                  items={Object.entries(selectedLog.changes).map(([field, change]) => ({
                    color: 'blue',
                    children: (
                      <div>
                        <Text strong>{field}</Text>
                        <div style={{ marginTop: 4 }}>
                          <Tag color="red">Old: {String(change.old) || 'null'}</Tag>
                          <Tag color="green">New: {String(change.new)}</Tag>
                        </div>
                      </div>
                    ),
                  }))}
                />
              </Card>
            )}

            {selectedLog.error_message && (
              <Card title="Error" size="small">
                <Text type="danger">{selectedLog.error_message}</Text>
              </Card>
            )}
          </Space>
        )}
      </Drawer>
    </div>
  );
};

export default AuditLogPage;
