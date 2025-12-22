import React, { useState } from 'react';
import { Table, Tag, Button, Space, Input, Select, Card, Typography, Tooltip, Badge, Modal, message } from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  CheckOutlined,
  StopOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

import {
  useListAlertsQuery,
  useAcknowledgeAlertMutation,
  useResolveAlertMutation,
  useCreateIncidentFromAlertMutation,
} from '../../../store/api/alertsApi';
import type { Alert, AlertStatus, AlertSeverity } from '../../../types/models.types';

dayjs.extend(relativeTime);

const { Title } = Typography;
const { Option } = Select;

const statusColors: Record<AlertStatus, string> = {
  firing: 'red',
  acknowledged: 'blue',
  resolved: 'green',
  suppressed: 'default',
};

const severityColors: Record<AlertSeverity, string> = {
  critical: 'red',
  warning: 'orange',
  info: 'blue',
};

const AlertListPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string[]>([]);
  const [severityFilter, setSeverityFilter] = useState<string[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const { data, isLoading, refetch } = useListAlertsQuery({
    page,
    page_size: pageSize,
    search: search || undefined,
    status: statusFilter.length > 0 ? statusFilter : undefined,
    severity: severityFilter.length > 0 ? severityFilter : undefined,
    sort_by: 'created_at',
    sort_order: 'desc',
  });

  const [acknowledge, { isLoading: acknowledging }] = useAcknowledgeAlertMutation();
  const [resolve, { isLoading: resolving }] = useResolveAlertMutation();
  const [createIncident, { isLoading: creatingIncident }] = useCreateIncidentFromAlertMutation();

  const handleAcknowledge = async (id: string) => {
    try {
      await acknowledge(id).unwrap();
      message.success('Alert acknowledged');
    } catch {
      message.error('Failed to acknowledge alert');
    }
  };

  const handleResolve = async (id: string) => {
    try {
      await resolve(id).unwrap();
      message.success('Alert resolved');
    } catch {
      message.error('Failed to resolve alert');
    }
  };

  const handleCreateIncident = async (alert: Alert) => {
    try {
      await createIncident({
        id: alert.id,
        data: {
          title: alert.title || undefined,
          description: alert.message || undefined,
        },
      }).unwrap();
      message.success('Incident created from alert');
    } catch {
      message.error('Failed to create incident');
    }
  };

  const columns: ColumnsType<Alert> = [
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity: AlertSeverity) => (
        <Tag color={severityColors[severity]}>{severity.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (title: string, record: Alert) => (
        <Tooltip title={title}>
          <a onClick={() => setSelectedAlert(record)}>{title || 'No title'}</a>
        </Tooltip>
      ),
    },
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
      width: 120,
      render: (source: string) => <Tag>{source}</Tag>,
    },
    {
      title: 'Host',
      dataIndex: 'host',
      key: 'host',
      width: 150,
      ellipsis: true,
      render: (host: string | null) => host || '-',
    },
    {
      title: 'Service',
      dataIndex: 'service',
      key: 'service',
      width: 120,
      render: (service: string | null) => service || '-',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: AlertStatus) => (
        <Tag color={statusColors[status]}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Count',
      dataIndex: 'occurrence_count',
      key: 'occurrence_count',
      width: 70,
      render: (count: number) => (
        <Badge count={count} showZero style={{ backgroundColor: count > 1 ? '#faad14' : '#52c41a' }} />
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (date: string) => (
        <Tooltip title={dayjs(date).format('YYYY-MM-DD HH:mm:ss')}>
          {dayjs(date).fromNow()}
        </Tooltip>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_: unknown, record: Alert) => (
        <Space size="small">
          <Tooltip title="View">
            <Button type="text" size="small" icon={<EyeOutlined />} onClick={() => setSelectedAlert(record)} />
          </Tooltip>
          {record.status === 'firing' && (
            <Tooltip title="Acknowledge">
              <Button
                type="text"
                size="small"
                icon={<CheckOutlined />}
                onClick={() => handleAcknowledge(record.id)}
              />
            </Tooltip>
          )}
          {record.status !== 'resolved' && (
            <Tooltip title="Resolve">
              <Button
                type="text"
                size="small"
                icon={<StopOutlined />}
                onClick={() => handleResolve(record.id)}
              />
            </Tooltip>
          )}
          {!record.incident_id && (
            <Tooltip title="Create Incident">
              <Button
                type="text"
                size="small"
                icon={<ExclamationCircleOutlined />}
                onClick={() => handleCreateIncident(record)}
              />
            </Tooltip>
          )}
        </Space>
      ),
    },
  ];

  const handleTableChange = (pagination: TablePaginationConfig) => {
    setPage(pagination.current || 1);
    setPageSize(pagination.pageSize || 50);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ margin: 0 }}>Alerts</Title>
      </div>

      <Card>
        {/* Filters */}
        <Space style={{ marginBottom: 16 }} wrap>
          <Input
            placeholder="Search alerts..."
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 250 }}
            allowClear
          />
          <Select
            mode="multiple"
            placeholder="Status"
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ minWidth: 150 }}
            allowClear
          >
            <Option value="firing">Firing</Option>
            <Option value="acknowledged">Acknowledged</Option>
            <Option value="resolved">Resolved</Option>
            <Option value="suppressed">Suppressed</Option>
          </Select>
          <Select
            mode="multiple"
            placeholder="Severity"
            value={severityFilter}
            onChange={setSeverityFilter}
            style={{ minWidth: 120 }}
            allowClear
          >
            <Option value="critical">Critical</Option>
            <Option value="warning">Warning</Option>
            <Option value="info">Info</Option>
          </Select>
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            Refresh
          </Button>
        </Space>

        {/* Table */}
        <Table
          columns={columns}
          dataSource={data?.items}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: page,
            pageSize,
            total: data?.total || 0,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} alerts`,
          }}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* Alert Detail Modal */}
      <Modal
        title={selectedAlert?.title || 'Alert Details'}
        open={!!selectedAlert}
        onCancel={() => setSelectedAlert(null)}
        footer={null}
        width={600}
      >
        {selectedAlert && (
          <div>
            <p><strong>Source:</strong> {selectedAlert.source}</p>
            <p><strong>Host:</strong> {selectedAlert.host || '-'}</p>
            <p><strong>Service:</strong> {selectedAlert.service || '-'}</p>
            <p><strong>Severity:</strong> <Tag color={severityColors[selectedAlert.severity]}>{selectedAlert.severity.toUpperCase()}</Tag></p>
            <p><strong>Status:</strong> <Tag color={statusColors[selectedAlert.status]}>{selectedAlert.status.toUpperCase()}</Tag></p>
            <p><strong>Message:</strong></p>
            <p style={{ background: '#f5f5f5', padding: 12, borderRadius: 4 }}>{selectedAlert.message || 'No message'}</p>
            <p><strong>Occurrences:</strong> {selectedAlert.occurrence_count}</p>
            <p><strong>First Seen:</strong> {dayjs(selectedAlert.first_occurrence_at).format('YYYY-MM-DD HH:mm:ss')}</p>
            <p><strong>Last Seen:</strong> {dayjs(selectedAlert.last_occurrence_at).format('YYYY-MM-DD HH:mm:ss')}</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AlertListPage;
