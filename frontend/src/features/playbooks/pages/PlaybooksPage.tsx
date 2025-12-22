import React, { useState } from 'react';
import { Card, Table, Button, Tag, Space, Typography, Progress, Modal, Form, Input, Select, message, Popconfirm, Drawer, Timeline } from 'antd';
import { PlusOutlined, PlayCircleOutlined, EditOutlined, DeleteOutlined, HistoryOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { TextArea } = Input;

interface Playbook {
  id: string;
  name: string;
  description: string;
  trigger: string;
  status: 'active' | 'inactive' | 'draft';
  executionCount: number;
  successRate: number;
  lastRun: string | null;
}

interface ExecutionHistory {
  id: string;
  timestamp: string;
  status: 'success' | 'failed';
  duration: string;
  triggeredBy: string;
}

const initialPlaybooks: Playbook[] = [
  {
    id: '1',
    name: 'Auto-Restart Failed Services',
    description: 'Automatically restart services when they fail health checks',
    trigger: 'Alert: Service Down',
    status: 'active',
    executionCount: 156,
    successRate: 94.2,
    lastRun: '2025-12-22T10:30:00Z',
  },
  {
    id: '2',
    name: 'Database Failover',
    description: 'Initiate database failover when primary becomes unavailable',
    trigger: 'Alert: DB Connection Timeout',
    status: 'active',
    executionCount: 12,
    successRate: 100,
    lastRun: '2025-12-21T15:45:00Z',
  },
  {
    id: '3',
    name: 'Scale Up on High Load',
    description: 'Auto-scale application instances when CPU exceeds 80%',
    trigger: 'Metric: CPU > 80%',
    status: 'active',
    executionCount: 89,
    successRate: 98.9,
    lastRun: '2025-12-22T08:15:00Z',
  },
  {
    id: '4',
    name: 'Security Incident Response',
    description: 'Isolate affected systems and notify security team',
    trigger: 'Alert: Security Breach',
    status: 'inactive',
    executionCount: 3,
    successRate: 100,
    lastRun: '2025-12-15T22:00:00Z',
  },
  {
    id: '5',
    name: 'Disk Cleanup Automation',
    description: 'Clean up old logs and temp files when disk usage exceeds 90%',
    trigger: 'Metric: Disk > 90%',
    status: 'draft',
    executionCount: 0,
    successRate: 0,
    lastRun: null,
  },
];

const executionHistories: Record<string, ExecutionHistory[]> = {
  '1': [
    { id: '1', timestamp: '2025-12-22T10:30:00Z', status: 'success', duration: '2.3s', triggeredBy: 'Alert #1234' },
    { id: '2', timestamp: '2025-12-22T09:15:00Z', status: 'success', duration: '1.8s', triggeredBy: 'Alert #1230' },
    { id: '3', timestamp: '2025-12-22T08:00:00Z', status: 'failed', duration: '5.1s', triggeredBy: 'Alert #1228' },
    { id: '4', timestamp: '2025-12-21T23:45:00Z', status: 'success', duration: '2.1s', triggeredBy: 'Alert #1220' },
  ],
  '2': [
    { id: '1', timestamp: '2025-12-21T15:45:00Z', status: 'success', duration: '8.5s', triggeredBy: 'Alert #1215' },
    { id: '2', timestamp: '2025-12-20T10:30:00Z', status: 'success', duration: '7.2s', triggeredBy: 'Manual' },
  ],
  '3': [
    { id: '1', timestamp: '2025-12-22T08:15:00Z', status: 'success', duration: '45.2s', triggeredBy: 'Metric Threshold' },
    { id: '2', timestamp: '2025-12-22T06:00:00Z', status: 'success', duration: '42.1s', triggeredBy: 'Metric Threshold' },
  ],
};

const statusColors: Record<string, string> = {
  active: 'green',
  inactive: 'default',
  draft: 'orange',
};

const triggerOptions = [
  'Alert: Service Down',
  'Alert: DB Connection Timeout',
  'Alert: Security Breach',
  'Metric: CPU > 80%',
  'Metric: Memory > 90%',
  'Metric: Disk > 90%',
  'Schedule: Daily',
  'Schedule: Hourly',
  'Manual',
];

const PlaybooksPage: React.FC = () => {
  const [playbooks, setPlaybooks] = useState<Playbook[]>(initialPlaybooks);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isHistoryDrawerOpen, setIsHistoryDrawerOpen] = useState(false);
  const [selectedPlaybook, setSelectedPlaybook] = useState<Playbook | null>(null);
  const [runningPlaybooks, setRunningPlaybooks] = useState<Set<string>>(new Set());
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();

  const handleCreate = () => {
    form.validateFields().then((values) => {
      const newPlaybook: Playbook = {
        id: String(Date.now()),
        name: values.name,
        description: values.description,
        trigger: values.trigger,
        status: 'draft',
        executionCount: 0,
        successRate: 0,
        lastRun: null,
      };
      setPlaybooks([...playbooks, newPlaybook]);
      message.success(`Playbook "${values.name}" created successfully`);
      setIsCreateModalOpen(false);
      form.resetFields();
    });
  };

  const handleEdit = () => {
    editForm.validateFields().then((values) => {
      setPlaybooks(playbooks.map(p =>
        p.id === selectedPlaybook?.id
          ? { ...p, name: values.name, description: values.description, trigger: values.trigger, status: values.status }
          : p
      ));
      message.success(`Playbook "${values.name}" updated successfully`);
      setIsEditModalOpen(false);
      setSelectedPlaybook(null);
    });
  };

  const handleDelete = (playbook: Playbook) => {
    setPlaybooks(playbooks.filter(p => p.id !== playbook.id));
    message.success(`Playbook "${playbook.name}" deleted`);
  };

  const handleRun = (playbook: Playbook) => {
    setRunningPlaybooks(prev => new Set(prev).add(playbook.id));
    message.loading(`Running playbook "${playbook.name}"...`, 2);

    setTimeout(() => {
      const success = Math.random() > 0.1; // 90% success rate
      setRunningPlaybooks(prev => {
        const next = new Set(prev);
        next.delete(playbook.id);
        return next;
      });

      setPlaybooks(playbooks.map(p =>
        p.id === playbook.id
          ? {
              ...p,
              executionCount: p.executionCount + 1,
              lastRun: new Date().toISOString(),
              successRate: success
                ? Math.min(100, p.successRate + 0.5)
                : Math.max(0, p.successRate - 2)
            }
          : p
      ));

      if (success) {
        message.success(`Playbook "${playbook.name}" executed successfully`);
      } else {
        message.error(`Playbook "${playbook.name}" execution failed`);
      }
    }, 2000);
  };

  const openEditModal = (playbook: Playbook) => {
    setSelectedPlaybook(playbook);
    editForm.setFieldsValue({
      name: playbook.name,
      description: playbook.description,
      trigger: playbook.trigger,
      status: playbook.status,
    });
    setIsEditModalOpen(true);
  };

  const openHistoryDrawer = (playbook: Playbook) => {
    setSelectedPlaybook(playbook);
    setIsHistoryDrawerOpen(true);
  };

  const columns: ColumnsType<Playbook> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: 12, color: '#888' }}>{record.description}</div>
        </div>
      ),
    },
    {
      title: 'Trigger',
      dataIndex: 'trigger',
      key: 'trigger',
      render: (text) => <Tag>{text}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={statusColors[status]}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Executions',
      dataIndex: 'executionCount',
      key: 'executionCount',
      align: 'center',
    },
    {
      title: 'Success Rate',
      dataIndex: 'successRate',
      key: 'successRate',
      render: (rate) => (
        <Progress
          percent={Number(rate.toFixed(1))}
          size="small"
          status={rate >= 90 ? 'success' : rate >= 70 ? 'normal' : 'exception'}
          style={{ width: 100 }}
        />
      ),
    },
    {
      title: 'Last Run',
      dataIndex: 'lastRun',
      key: 'lastRun',
      render: (date) => date ? new Date(date).toLocaleString() : '-',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<PlayCircleOutlined />}
            disabled={record.status !== 'active' || runningPlaybooks.has(record.id)}
            loading={runningPlaybooks.has(record.id)}
            onClick={() => handleRun(record)}
            title="Run Playbook"
          />
          <Button
            type="text"
            icon={<HistoryOutlined />}
            onClick={() => openHistoryDrawer(record)}
            title="View History"
          />
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => openEditModal(record)}
            title="Edit Playbook"
          />
          <Popconfirm
            title="Delete Playbook"
            description={`Are you sure you want to delete "${record.name}"?`}
            onConfirm={() => handleDelete(record)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="text" danger icon={<DeleteOutlined />} title="Delete Playbook" />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const history = selectedPlaybook ? executionHistories[selectedPlaybook.id] || [] : [];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Playbooks</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsCreateModalOpen(true)}>
          Create Playbook
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={playbooks}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Create Modal */}
      <Modal
        title="Create New Playbook"
        open={isCreateModalOpen}
        onOk={handleCreate}
        onCancel={() => { setIsCreateModalOpen(false); form.resetFields(); }}
        okText="Create"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Please enter a name' }]}>
            <Input placeholder="Enter playbook name" />
          </Form.Item>
          <Form.Item name="description" label="Description" rules={[{ required: true, message: 'Please enter a description' }]}>
            <TextArea rows={3} placeholder="Describe what this playbook does" />
          </Form.Item>
          <Form.Item name="trigger" label="Trigger" rules={[{ required: true, message: 'Please select a trigger' }]}>
            <Select placeholder="Select trigger condition">
              {triggerOptions.map(t => <Select.Option key={t} value={t}>{t}</Select.Option>)}
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Edit Modal */}
      <Modal
        title="Edit Playbook"
        open={isEditModalOpen}
        onOk={handleEdit}
        onCancel={() => { setIsEditModalOpen(false); setSelectedPlaybook(null); }}
        okText="Save"
      >
        <Form form={editForm} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Please enter a name' }]}>
            <Input placeholder="Enter playbook name" />
          </Form.Item>
          <Form.Item name="description" label="Description" rules={[{ required: true, message: 'Please enter a description' }]}>
            <TextArea rows={3} placeholder="Describe what this playbook does" />
          </Form.Item>
          <Form.Item name="trigger" label="Trigger" rules={[{ required: true, message: 'Please select a trigger' }]}>
            <Select placeholder="Select trigger condition">
              {triggerOptions.map(t => <Select.Option key={t} value={t}>{t}</Select.Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="status" label="Status" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="active">Active</Select.Option>
              <Select.Option value="inactive">Inactive</Select.Option>
              <Select.Option value="draft">Draft</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* History Drawer */}
      <Drawer
        title={`Execution History: ${selectedPlaybook?.name}`}
        open={isHistoryDrawerOpen}
        onClose={() => { setIsHistoryDrawerOpen(false); setSelectedPlaybook(null); }}
        width={500}
      >
        {history.length > 0 ? (
          <Timeline
            items={history.map(h => ({
              color: h.status === 'success' ? 'green' : 'red',
              dot: h.status === 'success' ? <CheckCircleOutlined /> : <CloseCircleOutlined />,
              children: (
                <div>
                  <div><Text strong>{h.status === 'success' ? 'Success' : 'Failed'}</Text></div>
                  <div><Text type="secondary">{new Date(h.timestamp).toLocaleString()}</Text></div>
                  <div><Text type="secondary">Duration: {h.duration}</Text></div>
                  <div><Text type="secondary">Triggered by: {h.triggeredBy}</Text></div>
                </div>
              ),
            }))}
          />
        ) : (
          <Text type="secondary">No execution history available</Text>
        )}
      </Drawer>
    </div>
  );
};

export default PlaybooksPage;
