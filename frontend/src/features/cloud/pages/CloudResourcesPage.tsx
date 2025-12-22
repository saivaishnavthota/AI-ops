import React, { useState } from 'react';
import { Card, Table, Tag, Space, Typography, Progress, Statistic, Row, Col, Badge, Button, Modal, Descriptions, message, Popconfirm } from 'antd';
import { CloudServerOutlined, DatabaseOutlined, HddOutlined, GlobalOutlined, EyeOutlined, PlayCircleOutlined, PauseCircleOutlined, ReloadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

interface CloudResource {
  id: string;
  name: string;
  type: string;
  provider: string;
  region: string;
  status: 'running' | 'stopped' | 'pending' | 'error';
  cpu: number;
  memory: number;
  cost: number;
  instanceType?: string;
  privateIp?: string;
  publicIp?: string;
  launchTime?: string;
}

const initialResources: CloudResource[] = [
  { id: '1', name: 'prod-api-server-1', type: 'EC2', provider: 'AWS', region: 'us-east-1', status: 'running', cpu: 45, memory: 62, cost: 156.50, instanceType: 't3.large', privateIp: '10.0.1.15', publicIp: '54.123.45.67', launchTime: '2025-11-15T08:00:00Z' },
  { id: '2', name: 'prod-api-server-2', type: 'EC2', provider: 'AWS', region: 'us-east-1', status: 'running', cpu: 38, memory: 55, cost: 156.50, instanceType: 't3.large', privateIp: '10.0.1.16', publicIp: '54.123.45.68', launchTime: '2025-11-15T08:05:00Z' },
  { id: '3', name: 'prod-db-primary', type: 'RDS', provider: 'AWS', region: 'us-east-1', status: 'running', cpu: 72, memory: 85, cost: 450.00, instanceType: 'db.r5.xlarge', privateIp: '10.0.2.10', launchTime: '2025-10-01T00:00:00Z' },
  { id: '4', name: 'prod-db-replica', type: 'RDS', provider: 'AWS', region: 'us-west-2', status: 'running', cpu: 25, memory: 40, cost: 350.00, instanceType: 'db.r5.large', privateIp: '10.1.2.10', launchTime: '2025-10-01T00:00:00Z' },
  { id: '5', name: 'prod-redis-cluster', type: 'ElastiCache', provider: 'AWS', region: 'us-east-1', status: 'running', cpu: 15, memory: 45, cost: 89.00, instanceType: 'cache.r5.large', privateIp: '10.0.3.5', launchTime: '2025-09-15T00:00:00Z' },
  { id: '6', name: 'staging-api-server', type: 'EC2', provider: 'AWS', region: 'us-east-1', status: 'stopped', cpu: 0, memory: 0, cost: 0, instanceType: 't3.medium', privateIp: '10.0.4.10', launchTime: '2025-12-01T00:00:00Z' },
  { id: '7', name: 'dev-kubernetes-cluster', type: 'EKS', provider: 'AWS', region: 'us-west-2', status: 'running', cpu: 55, memory: 70, cost: 245.00, instanceType: '3 nodes', privateIp: '10.1.0.0/16', launchTime: '2025-08-01T00:00:00Z' },
  { id: '8', name: 'cdn-distribution', type: 'CloudFront', provider: 'AWS', region: 'global', status: 'running', cpu: 0, memory: 0, cost: 125.00, launchTime: '2025-06-01T00:00:00Z' },
];

const statusColors: Record<string, 'success' | 'default' | 'warning' | 'error'> = {
  running: 'success',
  stopped: 'default',
  pending: 'warning',
  error: 'error',
};

const typeIcons: Record<string, React.ReactNode> = {
  EC2: <CloudServerOutlined />,
  RDS: <DatabaseOutlined />,
  ElastiCache: <HddOutlined />,
  EKS: <CloudServerOutlined />,
  CloudFront: <GlobalOutlined />,
};

const CloudResourcesPage: React.FC = () => {
  const [resources, setResources] = useState<CloudResource[]>(initialResources);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [selectedResource, setSelectedResource] = useState<CloudResource | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const totalResources = resources.length;
  const runningResources = resources.filter(r => r.status === 'running').length;
  const totalCost = resources.reduce((sum, r) => sum + r.cost, 0);
  const avgCpu = resources.filter(r => r.status === 'running').reduce((sum, r) => sum + r.cpu, 0) / (runningResources || 1);

  const handleViewDetails = (resource: CloudResource) => {
    setSelectedResource(resource);
    setIsDetailModalOpen(true);
  };

  const handleStartResource = (resource: CloudResource) => {
    setActionLoading(resource.id);
    message.loading(`Starting ${resource.name}...`, 2);

    setTimeout(() => {
      setResources(resources.map(r =>
        r.id === resource.id ? { ...r, status: 'running', cpu: Math.floor(Math.random() * 30) + 20, memory: Math.floor(Math.random() * 30) + 30 } : r
      ));
      setActionLoading(null);
      message.success(`${resource.name} started successfully`);
    }, 2000);
  };

  const handleStopResource = (resource: CloudResource) => {
    setActionLoading(resource.id);
    message.loading(`Stopping ${resource.name}...`, 2);

    setTimeout(() => {
      setResources(resources.map(r =>
        r.id === resource.id ? { ...r, status: 'stopped', cpu: 0, memory: 0, cost: 0 } : r
      ));
      setActionLoading(null);
      message.success(`${resource.name} stopped`);
    }, 2000);
  };

  const handleRebootResource = (resource: CloudResource) => {
    setActionLoading(resource.id);
    message.loading(`Rebooting ${resource.name}...`, 3);

    setResources(resources.map(r =>
      r.id === resource.id ? { ...r, status: 'pending' } : r
    ));

    setTimeout(() => {
      setResources(resources.map(r =>
        r.id === resource.id ? { ...r, status: 'running', cpu: Math.floor(Math.random() * 30) + 20, memory: Math.floor(Math.random() * 30) + 30 } : r
      ));
      setActionLoading(null);
      message.success(`${resource.name} rebooted successfully`);
    }, 3000);
  };

  const columns: ColumnsType<CloudResource> = [
    {
      title: 'Resource',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          {typeIcons[record.type] || <CloudServerOutlined />}
          <div>
            <div style={{ fontWeight: 500 }}>{text}</div>
            <div style={{ fontSize: 12, color: '#888' }}>{record.type}</div>
          </div>
        </Space>
      ),
    },
    {
      title: 'Provider',
      dataIndex: 'provider',
      key: 'provider',
      render: (provider) => <Tag color="blue">{provider}</Tag>,
    },
    {
      title: 'Region',
      dataIndex: 'region',
      key: 'region',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Badge status={statusColors[status]} text={status.toUpperCase()} />
      ),
    },
    {
      title: 'CPU',
      dataIndex: 'cpu',
      key: 'cpu',
      render: (cpu) => <Progress percent={cpu} size="small" style={{ width: 80 }} />,
    },
    {
      title: 'Memory',
      dataIndex: 'memory',
      key: 'memory',
      render: (memory) => <Progress percent={memory} size="small" style={{ width: 80 }} />,
    },
    {
      title: 'Monthly Cost',
      dataIndex: 'cost',
      key: 'cost',
      render: (cost) => `$${cost.toFixed(2)}`,
      align: 'right',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetails(record)}
            title="View Details"
          />
          {record.status === 'stopped' && record.type === 'EC2' && (
            <Button
              type="text"
              icon={<PlayCircleOutlined />}
              onClick={() => handleStartResource(record)}
              loading={actionLoading === record.id}
              title="Start"
              style={{ color: '#52c41a' }}
            />
          )}
          {record.status === 'running' && record.type === 'EC2' && (
            <>
              <Popconfirm
                title="Stop Resource"
                description={`Are you sure you want to stop ${record.name}?`}
                onConfirm={() => handleStopResource(record)}
                okText="Yes"
                cancelText="No"
              >
                <Button
                  type="text"
                  icon={<PauseCircleOutlined />}
                  loading={actionLoading === record.id}
                  title="Stop"
                  style={{ color: '#faad14' }}
                />
              </Popconfirm>
              <Popconfirm
                title="Reboot Resource"
                description={`Are you sure you want to reboot ${record.name}?`}
                onConfirm={() => handleRebootResource(record)}
                okText="Yes"
                cancelText="No"
              >
                <Button
                  type="text"
                  icon={<ReloadOutlined />}
                  loading={actionLoading === record.id}
                  title="Reboot"
                />
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>Cloud Resources</Title>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic title="Total Resources" value={totalResources} />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic title="Running" value={runningResources} valueStyle={{ color: '#52c41a' }} />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic title="Avg CPU Usage" value={avgCpu.toFixed(1)} suffix="%" />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic title="Monthly Cost" value={totalCost} precision={2} prefix="$" />
          </Card>
        </Col>
      </Row>

      <Card>
        <Table
          columns={columns}
          dataSource={resources}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Details Modal */}
      <Modal
        title={`Resource Details: ${selectedResource?.name}`}
        open={isDetailModalOpen}
        onCancel={() => { setIsDetailModalOpen(false); setSelectedResource(null); }}
        footer={[
          <Button key="close" onClick={() => setIsDetailModalOpen(false)}>Close</Button>
        ]}
        width={600}
      >
        {selectedResource && (
          <Descriptions bordered column={2}>
            <Descriptions.Item label="Name" span={2}>{selectedResource.name}</Descriptions.Item>
            <Descriptions.Item label="Type">{selectedResource.type}</Descriptions.Item>
            <Descriptions.Item label="Provider">{selectedResource.provider}</Descriptions.Item>
            <Descriptions.Item label="Region">{selectedResource.region}</Descriptions.Item>
            <Descriptions.Item label="Status">
              <Badge status={statusColors[selectedResource.status]} text={selectedResource.status.toUpperCase()} />
            </Descriptions.Item>
            {selectedResource.instanceType && (
              <Descriptions.Item label="Instance Type">{selectedResource.instanceType}</Descriptions.Item>
            )}
            {selectedResource.privateIp && (
              <Descriptions.Item label="Private IP">{selectedResource.privateIp}</Descriptions.Item>
            )}
            {selectedResource.publicIp && (
              <Descriptions.Item label="Public IP">{selectedResource.publicIp}</Descriptions.Item>
            )}
            {selectedResource.launchTime && (
              <Descriptions.Item label="Launch Time" span={2}>{new Date(selectedResource.launchTime).toLocaleString()}</Descriptions.Item>
            )}
            <Descriptions.Item label="CPU Usage">
              <Progress percent={selectedResource.cpu} size="small" style={{ width: 120 }} />
            </Descriptions.Item>
            <Descriptions.Item label="Memory Usage">
              <Progress percent={selectedResource.memory} size="small" style={{ width: 120 }} />
            </Descriptions.Item>
            <Descriptions.Item label="Monthly Cost" span={2}>
              <Text strong style={{ fontSize: 18 }}>${selectedResource.cost.toFixed(2)}</Text>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default CloudResourcesPage;
