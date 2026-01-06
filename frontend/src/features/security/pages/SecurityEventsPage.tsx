import React, { useState } from 'react';
import { Card, Table, Tag, Typography, Space, Statistic, Row, Col, Badge, Button, Popconfirm, Drawer, Timeline, Descriptions, message } from 'antd';
import { SafetyOutlined, WarningOutlined, ExclamationCircleOutlined, SearchOutlined, CloseCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useGetSecurityEventsQuery,
  useGetSecurityEventStatsQuery,
  useUpdateSecurityEventMutation,
  SecurityEvent,
} from '../../../store/api/securityApi';

const { Title, Text, Paragraph } = Typography;

const severityColors: Record<string, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'gold',
  low: 'blue',
  info: 'default',
};

const statusBadge: Record<string, 'success' | 'processing' | 'error' | 'default'> = {
  open: 'error',
  investigating: 'processing',
  resolved: 'success',
  false_positive: 'default',
};

const SecurityEventsPage: React.FC = () => {
  const { data: eventsData, isLoading } = useGetSecurityEventsQuery({ skip: 0, limit: 100 });
  const { data: stats } = useGetSecurityEventStatsQuery();
  const [updateEvent] = useUpdateSecurityEventMutation();

  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);

  const events = eventsData?.items || [];

  const handleInvestigate = async (event: SecurityEvent) => {
    try {
      await updateEvent({ id: event.id, data: { status: 'investigating' } }).unwrap();
      message.info(`Investigation started for: ${event.type}`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to update event');
    }
  };

  const handleResolve = async (event: SecurityEvent) => {
    try {
      await updateEvent({ id: event.id, data: { status: 'resolved' } }).unwrap();
      message.success(`Event resolved: ${event.type}`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to resolve event');
    }
  };

  const handleMarkFalsePositive = async (event: SecurityEvent) => {
    try {
      await updateEvent({ id: event.id, data: { status: 'false_positive' } }).unwrap();
      message.info(`Marked as false positive: ${event.type}`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to update event');
    }
  };

  const handleViewDetails = (event: SecurityEvent) => {
    setSelectedEvent(event);
    setIsDetailDrawerOpen(true);
  };

  const columns: ColumnsType<SecurityEvent> = [
    {
      title: 'Time',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (ts: string) => new Date(ts).toLocaleString(),
    },
    {
      title: 'Event',
      dataIndex: 'type',
      key: 'type',
      render: (type: string, record: SecurityEvent) => (
        <div>
          <div style={{ fontWeight: 500 }}>{type}</div>
          <div style={{ fontSize: 12, color: '#666' }}>{record.description}</div>
        </div>
      ),
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity: string) => (
        <Tag color={severityColors[severity]}>{severity.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
      width: 140,
    },
    {
      title: 'Asset',
      dataIndex: 'affected_asset',
      key: 'affected_asset',
      width: 160,
      render: (asset: string) => asset ? <code>{asset}</code> : '-',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => (
        <Badge
          status={statusBadge[status]}
          text={status.replace('_', ' ').toUpperCase()}
        />
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (_: any, record: SecurityEvent) => (
        <Space>
          <Button
            type="text"
            icon={<SearchOutlined />}
            onClick={() => handleViewDetails(record)}
            title="View Details"
          />
          {record.status === 'open' && (
            <Button
              type="primary"
              size="small"
              onClick={() => handleInvestigate(record)}
            >
              Investigate
            </Button>
          )}
          {record.status === 'investigating' && (
            <Popconfirm
              title="Resolve Event"
              description="Mark this security event as resolved?"
              onConfirm={() => handleResolve(record)}
              okText="Resolve"
              cancelText="Cancel"
            >
              <Button size="small" type="primary" icon={<CheckCircleOutlined />}>
                Resolve
              </Button>
            </Popconfirm>
          )}
          {(record.status === 'open' || record.status === 'investigating') && (
            <Popconfirm
              title="Mark as False Positive"
              description="Are you sure this is a false positive?"
              onConfirm={() => handleMarkFalsePositive(record)}
              okText="Yes"
              cancelText="No"
            >
              <Button size="small" icon={<CloseCircleOutlined />}>
                False +
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>Security Events</Title>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Critical"
              value={stats?.critical_count || 0}
              valueStyle={{ color: '#cf1322' }}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="High"
              value={stats?.high_count || 0}
              valueStyle={{ color: '#fa8c16' }}
              prefix={<WarningOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Open Events"
              value={stats?.open_count || 0}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Total Events"
              value={stats?.total_events || 0}
              prefix={<SafetyOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Table
          columns={columns}
          dataSource={events}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Detail Drawer */}
      <Drawer
        title={`Security Event: ${selectedEvent?.type}`}
        open={isDetailDrawerOpen}
        onClose={() => { setIsDetailDrawerOpen(false); setSelectedEvent(null); }}
        width={600}
        extra={
          selectedEvent?.status === 'open' && (
            <Button type="primary" onClick={() => { handleInvestigate(selectedEvent); }}>
              Start Investigation
            </Button>
          )
        }
      >
        {selectedEvent && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Descriptions bordered column={1}>
              <Descriptions.Item label="Event Type">{selectedEvent.type}</Descriptions.Item>
              <Descriptions.Item label="Timestamp">{new Date(selectedEvent.created_at).toLocaleString()}</Descriptions.Item>
              <Descriptions.Item label="Severity">
                <Tag color={severityColors[selectedEvent.severity]}>{selectedEvent.severity.toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Status">
                <Badge status={statusBadge[selectedEvent.status]} text={selectedEvent.status.replace('_', ' ').toUpperCase()} />
              </Descriptions.Item>
              <Descriptions.Item label="Source">{selectedEvent.source}</Descriptions.Item>
              <Descriptions.Item label="Affected Asset">{selectedEvent.affected_asset ? <code>{selectedEvent.affected_asset}</code> : '-'}</Descriptions.Item>
              {selectedEvent.ip_address && (
                <Descriptions.Item label="IP Address"><code>{selectedEvent.ip_address}</code></Descriptions.Item>
              )}
              {selectedEvent.user && (
                <Descriptions.Item label="User"><code>{selectedEvent.user}</code></Descriptions.Item>
              )}
            </Descriptions>

            <Card title="Description" size="small">
              <Paragraph>{selectedEvent.description}</Paragraph>
            </Card>

            {selectedEvent.details && (
              <Card title="Details" size="small">
                <Paragraph>{selectedEvent.details}</Paragraph>
              </Card>
            )}

            <Card title="Event Timeline" size="small">
              <Timeline
                items={[
                  {
                    color: 'blue',
                    children: (
                      <div>
                        <Text strong>Event Detected</Text>
                        <div><Text type="secondary">{new Date(selectedEvent.created_at).toLocaleString()}</Text></div>
                      </div>
                    ),
                  },
                  ...(selectedEvent.status !== 'open' ? [{
                    color: 'orange',
                    children: (
                      <div>
                        <Text strong>Investigation Started</Text>
                        <div><Text type="secondary">Security team notified</Text></div>
                      </div>
                    ),
                  }] : []),
                  ...(selectedEvent.status === 'resolved' ? [{
                    color: 'green',
                    children: (
                      <div>
                        <Text strong>Resolved</Text>
                        <div><Text type="secondary">Event marked as resolved</Text></div>
                      </div>
                    ),
                  }] : []),
                  ...(selectedEvent.status === 'false_positive' ? [{
                    color: 'gray',
                    children: (
                      <div>
                        <Text strong>False Positive</Text>
                        <div><Text type="secondary">Event marked as false positive</Text></div>
                      </div>
                    ),
                  }] : []),
                ]}
              />
            </Card>
          </Space>
        )}
      </Drawer>
    </div>
  );
};

export default SecurityEventsPage;
