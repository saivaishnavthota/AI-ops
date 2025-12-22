import React, { useState } from 'react';
import { Card, Table, Tag, Typography, Space, Statistic, Row, Col, Badge, Button, Modal, message, Popconfirm, Drawer, Timeline, Descriptions } from 'antd';
import { SafetyOutlined, WarningOutlined, ExclamationCircleOutlined, SearchOutlined, CloseCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text, Paragraph } = Typography;

interface SecurityEvent {
  id: string;
  timestamp: string;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  source: string;
  description: string;
  status: 'open' | 'investigating' | 'resolved' | 'false_positive';
  affectedAsset: string;
  details?: string;
  ipAddress?: string;
  user?: string;
}

const initialEvents: SecurityEvent[] = [
  {
    id: '1',
    timestamp: '2025-12-22T10:45:00Z',
    type: 'Failed Login Attempt',
    severity: 'medium',
    source: 'Auth Service',
    description: 'Multiple failed login attempts detected from IP 192.168.1.100',
    status: 'investigating',
    affectedAsset: 'auth.example.com',
    details: '15 failed login attempts in the last 5 minutes. All attempts used the same username but different passwords.',
    ipAddress: '192.168.1.100',
    user: 'admin@example.com',
  },
  {
    id: '2',
    timestamp: '2025-12-22T10:30:00Z',
    type: 'Suspicious API Activity',
    severity: 'high',
    source: 'API Gateway',
    description: 'Unusual rate of API calls from user account detected',
    status: 'open',
    affectedAsset: 'api.example.com',
    details: 'User made 10,000 API calls in 1 hour, which is 50x the normal rate.',
    ipAddress: '203.45.67.89',
    user: 'service-account-1',
  },
  {
    id: '3',
    timestamp: '2025-12-22T09:15:00Z',
    type: 'SSL Certificate Expiring',
    severity: 'medium',
    source: 'Certificate Monitor',
    description: 'SSL certificate for app.example.com expires in 14 days',
    status: 'open',
    affectedAsset: 'app.example.com',
    details: 'Certificate issued by Let\'s Encrypt, expires on 2025-01-05.',
  },
  {
    id: '4',
    timestamp: '2025-12-22T08:00:00Z',
    type: 'Vulnerability Detected',
    severity: 'critical',
    source: 'Security Scanner',
    description: 'Critical CVE-2025-1234 detected in production container images',
    status: 'investigating',
    affectedAsset: 'prod-api:latest',
    details: 'CVE-2025-1234 affects the base image. CVSS score: 9.8. Remote code execution vulnerability.',
  },
  {
    id: '5',
    timestamp: '2025-12-21T22:30:00Z',
    type: 'Firewall Rule Change',
    severity: 'info',
    source: 'AWS CloudTrail',
    description: 'Security group sg-12345 modified by admin user',
    status: 'resolved',
    affectedAsset: 'sg-12345',
    details: 'Port 22 was opened to 10.0.0.0/8 CIDR range by user admin@example.com.',
    user: 'admin@example.com',
  },
  {
    id: '6',
    timestamp: '2025-12-21T18:45:00Z',
    type: 'Port Scan Detected',
    severity: 'low',
    source: 'IDS',
    description: 'Port scan activity detected from external IP',
    status: 'false_positive',
    affectedAsset: 'edge-firewall',
    ipAddress: '8.8.8.8',
    details: 'Detected as Google\'s DNS server performing legitimate health checks.',
  },
];

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
  const [events, setEvents] = useState<SecurityEvent[]>(initialEvents);
  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);

  const criticalCount = events.filter(e => e.severity === 'critical' && e.status !== 'resolved').length;
  const highCount = events.filter(e => e.severity === 'high' && e.status !== 'resolved').length;
  const openCount = events.filter(e => e.status === 'open' || e.status === 'investigating').length;

  const handleInvestigate = (event: SecurityEvent) => {
    setEvents(events.map(e =>
      e.id === event.id ? { ...e, status: 'investigating' } : e
    ));
    message.info(`Investigation started for: ${event.type}`);
  };

  const handleResolve = (event: SecurityEvent) => {
    setEvents(events.map(e =>
      e.id === event.id ? { ...e, status: 'resolved' } : e
    ));
    message.success(`Event resolved: ${event.type}`);
  };

  const handleMarkFalsePositive = (event: SecurityEvent) => {
    setEvents(events.map(e =>
      e.id === event.id ? { ...e, status: 'false_positive' } : e
    ));
    message.info(`Marked as false positive: ${event.type}`);
  };

  const handleViewDetails = (event: SecurityEvent) => {
    setSelectedEvent(event);
    setIsDetailDrawerOpen(true);
  };

  const columns: ColumnsType<SecurityEvent> = [
    {
      title: 'Time',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (ts) => new Date(ts).toLocaleString(),
    },
    {
      title: 'Event',
      dataIndex: 'type',
      key: 'type',
      render: (type, record) => (
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
      render: (severity) => (
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
      dataIndex: 'affectedAsset',
      key: 'affectedAsset',
      width: 160,
      render: (asset) => <code>{asset}</code>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => (
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
      render: (_, record) => (
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
              value={criticalCount}
              valueStyle={{ color: '#cf1322' }}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="High"
              value={highCount}
              valueStyle={{ color: '#fa8c16' }}
              prefix={<WarningOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Open Events"
              value={openCount}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Total Events"
              value={events.length}
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
              <Descriptions.Item label="Timestamp">{new Date(selectedEvent.timestamp).toLocaleString()}</Descriptions.Item>
              <Descriptions.Item label="Severity">
                <Tag color={severityColors[selectedEvent.severity]}>{selectedEvent.severity.toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Status">
                <Badge status={statusBadge[selectedEvent.status]} text={selectedEvent.status.replace('_', ' ').toUpperCase()} />
              </Descriptions.Item>
              <Descriptions.Item label="Source">{selectedEvent.source}</Descriptions.Item>
              <Descriptions.Item label="Affected Asset"><code>{selectedEvent.affectedAsset}</code></Descriptions.Item>
              {selectedEvent.ipAddress && (
                <Descriptions.Item label="IP Address"><code>{selectedEvent.ipAddress}</code></Descriptions.Item>
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
                        <div><Text type="secondary">{new Date(selectedEvent.timestamp).toLocaleString()}</Text></div>
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
