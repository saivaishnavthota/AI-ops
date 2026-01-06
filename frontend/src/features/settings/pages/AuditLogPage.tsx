import React, { useState } from 'react';
import { Card, Table, Tag, Typography, Space, Input, Select, Button, Drawer, Descriptions, Timeline, Avatar, Row, Col, Statistic } from 'antd';
import { SearchOutlined, UserOutlined, EyeOutlined, DownloadOutlined, ReloadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useGetAuditLogsQuery,
  useGetAuditLogStatsQuery,
  AuditLogEntry,
} from '../../../store/api/auditLogsApi';

const { Title, Text, Paragraph } = Typography;

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

const AuditLogPage: React.FC = () => {
  const [searchText, setSearchText] = useState('');
  const [selectedResourceType, setSelectedResourceType] = useState('All');
  const [selectedAction, setSelectedAction] = useState('All');
  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [selectedLog, setSelectedLog] = useState<AuditLogEntry | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const { data: logsData, isLoading, refetch } = useGetAuditLogsQuery({
    page,
    page_size: pageSize,
    resource_type: selectedResourceType !== 'All' ? selectedResourceType : undefined,
  });

  const { data: stats } = useGetAuditLogStatsQuery();

  const logs = logsData?.items || [];

  const filteredLogs = logs.filter((log) => {
    const matchesSearch = !searchText ||
      log.description.toLowerCase().includes(searchText.toLowerCase()) ||
      (log.user_name && log.user_name.toLowerCase().includes(searchText.toLowerCase())) ||
      (log.resource_name && log.resource_name.toLowerCase().includes(searchText.toLowerCase()));
    const matchesAction = selectedAction === 'All' ||
      log.action.toLowerCase().includes(selectedAction.toLowerCase());
    return matchesSearch && matchesAction;
  });

  const handleRefresh = () => {
    refetch();
  };

  const handleExport = () => {
    const csvContent = [
      ['Timestamp', 'User', 'Action', 'Resource Type', 'Resource', 'Status', 'IP Address'],
      ...filteredLogs.map(log => [
        log.created_at,
        log.user_name || 'Unknown',
        log.action,
        log.resource_type,
        log.resource_name || '',
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
      render: (date: string) => new Date(date).toLocaleString(),
      sorter: (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
      defaultSortOrder: 'descend',
    },
    {
      title: 'User',
      dataIndex: 'user_name',
      key: 'user_name',
      width: 150,
      render: (name: string | null, record: AuditLogEntry) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          <div>
            <div>{name || 'Unknown'}</div>
            <Text type="secondary" style={{ fontSize: 11 }}>{record.user_email || 'N/A'}</Text>
          </div>
        </Space>
      ),
    },
    {
      title: 'Action',
      dataIndex: 'action',
      key: 'action',
      width: 150,
      render: (action: string) => (
        <Tag color={actionColors[action] || 'default'}>{action.replace(/\./g, ' ').replace(/_/g, ' ').toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Resource',
      key: 'resource',
      render: (_: any, record: AuditLogEntry) => (
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
      render: (status: string) => (
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
      render: (_: any, record: AuditLogEntry) => (
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

  const failedActions = stats?.by_action ? Object.values(stats.by_action).reduce((a, b) => a + b, 0) : 0;
  const uniqueUsers = stats?.by_user?.length || 0;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Audit Log</Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh} loading={isLoading}>
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
            <Statistic title="Total Actions Today" value={stats?.actions_today || 0} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Total Actions"
              value={stats?.total_actions || 0}
            />
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
        </Space>
      </Card>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredLogs}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: logsData?.total || 0,
            showSizeChanger: true,
            onChange: (newPage, newPageSize) => {
              setPage(newPage);
              setPageSize(newPageSize || 20);
            },
          }}
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
                  {selectedLog.user_name || 'Unknown'} ({selectedLog.user_email || 'N/A'})
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
                          <Tag color="red">Old: {String((change as any).old) || 'null'}</Tag>
                          <Tag color="green">New: {String((change as any).new)}</Tag>
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
