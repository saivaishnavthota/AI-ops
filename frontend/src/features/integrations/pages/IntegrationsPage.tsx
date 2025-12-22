import React, { useState } from 'react';
import { Card, Row, Col, Typography, Button, Tag, Switch, Space, Modal, Form, Input, Select, message, Spin } from 'antd';
import {
  CloudOutlined,
  SlackOutlined,
  GithubOutlined,
  ApiOutlined,
  CheckCircleOutlined,
  SettingOutlined,
  SyncOutlined,
  DisconnectOutlined,
  PlusOutlined,
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

interface Integration {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  category: string;
  status: 'connected' | 'disconnected' | 'error';
  enabled: boolean;
  lastSync: string | null;
  config?: Record<string, string>;
}

const initialIntegrations: Integration[] = [
  {
    id: 'prometheus',
    name: 'Prometheus',
    description: 'Metrics collection and alerting',
    icon: <ApiOutlined style={{ fontSize: 32, color: '#e6522c' }} />,
    category: 'Monitoring',
    status: 'connected',
    enabled: true,
    lastSync: '2025-12-22T10:30:00Z',
    config: { url: 'http://prometheus:9090', scrapeInterval: '15s' },
  },
  {
    id: 'grafana',
    name: 'Grafana',
    description: 'Visualization and dashboards',
    icon: <ApiOutlined style={{ fontSize: 32, color: '#f46800' }} />,
    category: 'Monitoring',
    status: 'connected',
    enabled: true,
    lastSync: '2025-12-22T10:28:00Z',
    config: { url: 'http://grafana:3000', apiKey: '***hidden***' },
  },
  {
    id: 'slack',
    name: 'Slack',
    description: 'Team notifications and alerts',
    icon: <SlackOutlined style={{ fontSize: 32, color: '#4a154b' }} />,
    category: 'Communication',
    status: 'connected',
    enabled: true,
    lastSync: '2025-12-22T10:25:00Z',
    config: { channel: '#alerts', webhook: '***hidden***' },
  },
  {
    id: 'pagerduty',
    name: 'PagerDuty',
    description: 'On-call management and escalations',
    icon: <ApiOutlined style={{ fontSize: 32, color: '#06ac38' }} />,
    category: 'Incident Management',
    status: 'connected',
    enabled: true,
    lastSync: '2025-12-22T10:20:00Z',
    config: { serviceKey: '***hidden***', escalationPolicy: 'default' },
  },
  {
    id: 'github',
    name: 'GitHub',
    description: 'Repository and deployment tracking',
    icon: <GithubOutlined style={{ fontSize: 32 }} />,
    category: 'DevOps',
    status: 'connected',
    enabled: true,
    lastSync: '2025-12-22T10:15:00Z',
    config: { org: 'my-org', token: '***hidden***' },
  },
  {
    id: 'aws',
    name: 'AWS',
    description: 'Cloud infrastructure monitoring',
    icon: <CloudOutlined style={{ fontSize: 32, color: '#ff9900' }} />,
    category: 'Cloud',
    status: 'connected',
    enabled: true,
    lastSync: '2025-12-22T10:10:00Z',
    config: { region: 'us-east-1', accessKey: '***hidden***' },
  },
  {
    id: 'datadog',
    name: 'Datadog',
    description: 'APM and log management',
    icon: <ApiOutlined style={{ fontSize: 32, color: '#632ca6' }} />,
    category: 'Monitoring',
    status: 'disconnected',
    enabled: false,
    lastSync: null,
  },
  {
    id: 'jira',
    name: 'Jira',
    description: 'Issue tracking and project management',
    icon: <ApiOutlined style={{ fontSize: 32, color: '#0052cc' }} />,
    category: 'Service Desk',
    status: 'error',
    enabled: true,
    lastSync: '2025-12-21T15:00:00Z',
    config: { url: 'https://company.atlassian.net', project: 'OPS' },
  },
];

const statusColors: Record<string, string> = {
  connected: 'green',
  disconnected: 'default',
  error: 'red',
};

const categoryOptions = ['Monitoring', 'Communication', 'Incident Management', 'DevOps', 'Cloud', 'Service Desk'];

const IntegrationsPage: React.FC = () => {
  const [integrations, setIntegrations] = useState<Integration[]>(initialIntegrations);
  const [isConfigureModalOpen, setIsConfigureModalOpen] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState<Integration | null>(null);
  const [testingConnection, setTestingConnection] = useState<string | null>(null);
  const [syncingIntegration, setSyncingIntegration] = useState<string | null>(null);
  const [form] = Form.useForm();
  const [addForm] = Form.useForm();

  const handleToggleEnabled = (integrationId: string, enabled: boolean) => {
    setIntegrations(integrations.map(i =>
      i.id === integrationId
        ? { ...i, enabled, status: enabled ? (i.status === 'disconnected' ? 'disconnected' : i.status) : 'disconnected' }
        : i
    ));
    const integration = integrations.find(i => i.id === integrationId);
    message.success(`${integration?.name} ${enabled ? 'enabled' : 'disabled'}`);
  };

  const handleTestConnection = (integrationId: string) => {
    setTestingConnection(integrationId);
    const integration = integrations.find(i => i.id === integrationId);

    setTimeout(() => {
      const success = Math.random() > 0.2; // 80% success rate
      setTestingConnection(null);

      if (success) {
        setIntegrations(integrations.map(i =>
          i.id === integrationId ? { ...i, status: 'connected' } : i
        ));
        message.success(`Connection to ${integration?.name} successful!`);
      } else {
        setIntegrations(integrations.map(i =>
          i.id === integrationId ? { ...i, status: 'error' } : i
        ));
        message.error(`Failed to connect to ${integration?.name}`);
      }
    }, 1500);
  };

  const handleSync = (integrationId: string) => {
    setSyncingIntegration(integrationId);
    const integration = integrations.find(i => i.id === integrationId);

    setTimeout(() => {
      setSyncingIntegration(null);
      setIntegrations(integrations.map(i =>
        i.id === integrationId ? { ...i, lastSync: new Date().toISOString() } : i
      ));
      message.success(`${integration?.name} synced successfully`);
    }, 2000);
  };

  const openConfigureModal = (integration: Integration) => {
    setSelectedIntegration(integration);
    form.setFieldsValue(integration.config || {});
    setIsConfigureModalOpen(true);
  };

  const handleSaveConfig = () => {
    form.validateFields().then((values) => {
      setIntegrations(integrations.map(i =>
        i.id === selectedIntegration?.id ? { ...i, config: values } : i
      ));
      message.success(`${selectedIntegration?.name} configuration saved`);
      setIsConfigureModalOpen(false);
      setSelectedIntegration(null);
    });
  };

  const handleAddIntegration = () => {
    addForm.validateFields().then((values) => {
      const newIntegration: Integration = {
        id: String(Date.now()),
        name: values.name,
        description: values.description,
        icon: <ApiOutlined style={{ fontSize: 32, color: '#1890ff' }} />,
        category: values.category,
        status: 'disconnected',
        enabled: false,
        lastSync: null,
      };
      setIntegrations([...integrations, newIntegration]);
      message.success(`Integration "${values.name}" added`);
      setIsAddModalOpen(false);
      addForm.resetFields();
    });
  };

  const handleDisconnect = (integrationId: string) => {
    const integration = integrations.find(i => i.id === integrationId);
    setIntegrations(integrations.map(i =>
      i.id === integrationId ? { ...i, status: 'disconnected', enabled: false } : i
    ));
    message.success(`${integration?.name} disconnected`);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Integrations</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsAddModalOpen(true)}>
          Add Integration
        </Button>
      </div>

      <Row gutter={[16, 16]}>
        {integrations.map((integration) => (
          <Col xs={24} sm={12} lg={8} xl={6} key={integration.id}>
            <Card
              hoverable
              style={{ height: '100%' }}
              actions={[
                <Button
                  type="text"
                  icon={<SettingOutlined />}
                  key="settings"
                  onClick={() => openConfigureModal(integration)}
                >
                  Configure
                </Button>,
                integration.status === 'connected' ? (
                  <Button
                    type="text"
                    icon={syncingIntegration === integration.id ? <SyncOutlined spin /> : <SyncOutlined />}
                    key="sync"
                    onClick={() => handleSync(integration.id)}
                    disabled={syncingIntegration === integration.id}
                  >
                    Sync
                  </Button>
                ) : (
                  <Button
                    type="text"
                    icon={testingConnection === integration.id ? <Spin size="small" /> : <ApiOutlined />}
                    key="test"
                    onClick={() => handleTestConnection(integration.id)}
                    disabled={testingConnection === integration.id}
                  >
                    Test
                  </Button>
                ),
              ]}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
                <div>{integration.icon}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text strong style={{ fontSize: 16 }}>{integration.name}</Text>
                    <Switch
                      checked={integration.enabled}
                      size="small"
                      onChange={(checked) => handleToggleEnabled(integration.id, checked)}
                    />
                  </div>
                  <Tag style={{ marginTop: 4 }}>{integration.category}</Tag>
                  <Paragraph type="secondary" style={{ marginTop: 8, marginBottom: 8, fontSize: 13 }}>
                    {integration.description}
                  </Paragraph>
                  <Space>
                    <Tag color={statusColors[integration.status]} icon={integration.status === 'connected' ? <CheckCircleOutlined /> : null}>
                      {integration.status.toUpperCase()}
                    </Tag>
                    {integration.status === 'connected' && (
                      <Button
                        type="link"
                        size="small"
                        danger
                        icon={<DisconnectOutlined />}
                        onClick={() => handleDisconnect(integration.id)}
                        style={{ padding: 0 }}
                      >
                        Disconnect
                      </Button>
                    )}
                  </Space>
                  {integration.lastSync && (
                    <Text type="secondary" style={{ display: 'block', fontSize: 11, marginTop: 8 }}>
                      Last sync: {new Date(integration.lastSync).toLocaleString()}
                    </Text>
                  )}
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Configure Modal */}
      <Modal
        title={`Configure ${selectedIntegration?.name}`}
        open={isConfigureModalOpen}
        onOk={handleSaveConfig}
        onCancel={() => { setIsConfigureModalOpen(false); setSelectedIntegration(null); }}
        okText="Save"
      >
        <Form form={form} layout="vertical">
          {selectedIntegration?.id === 'prometheus' && (
            <>
              <Form.Item name="url" label="Prometheus URL" rules={[{ required: true }]}>
                <Input placeholder="http://prometheus:9090" />
              </Form.Item>
              <Form.Item name="scrapeInterval" label="Scrape Interval">
                <Input placeholder="15s" />
              </Form.Item>
            </>
          )}
          {selectedIntegration?.id === 'slack' && (
            <>
              <Form.Item name="channel" label="Default Channel" rules={[{ required: true }]}>
                <Input placeholder="#alerts" />
              </Form.Item>
              <Form.Item name="webhook" label="Webhook URL" rules={[{ required: true }]}>
                <Input.Password placeholder="https://hooks.slack.com/..." />
              </Form.Item>
            </>
          )}
          {selectedIntegration?.id === 'aws' && (
            <>
              <Form.Item name="region" label="Region" rules={[{ required: true }]}>
                <Select placeholder="Select region">
                  <Select.Option value="us-east-1">US East (N. Virginia)</Select.Option>
                  <Select.Option value="us-west-2">US West (Oregon)</Select.Option>
                  <Select.Option value="eu-west-1">EU (Ireland)</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item name="accessKey" label="Access Key" rules={[{ required: true }]}>
                <Input.Password placeholder="Access Key ID" />
              </Form.Item>
            </>
          )}
          {!['prometheus', 'slack', 'aws'].includes(selectedIntegration?.id || '') && (
            <>
              <Form.Item name="url" label="API URL">
                <Input placeholder="https://api.example.com" />
              </Form.Item>
              <Form.Item name="apiKey" label="API Key">
                <Input.Password placeholder="Enter API key" />
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>

      {/* Add Integration Modal */}
      <Modal
        title="Add New Integration"
        open={isAddModalOpen}
        onOk={handleAddIntegration}
        onCancel={() => { setIsAddModalOpen(false); addForm.resetFields(); }}
        okText="Add"
      >
        <Form form={addForm} layout="vertical">
          <Form.Item name="name" label="Integration Name" rules={[{ required: true }]}>
            <Input placeholder="Enter integration name" />
          </Form.Item>
          <Form.Item name="description" label="Description" rules={[{ required: true }]}>
            <Input.TextArea rows={2} placeholder="Describe the integration" />
          </Form.Item>
          <Form.Item name="category" label="Category" rules={[{ required: true }]}>
            <Select placeholder="Select category">
              {categoryOptions.map(c => <Select.Option key={c} value={c}>{c}</Select.Option>)}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default IntegrationsPage;
