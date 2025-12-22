import React, { useState } from 'react';
import { Card, Table, Tag, Typography, Space, Button, Avatar, Progress, Modal, Form, Input, Select, message, Drawer, Timeline, Descriptions, Popconfirm } from 'antd';
import { PlusOutlined, UserOutlined, FileSearchOutlined, EditOutlined, CheckCircleOutlined, LinkOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

interface Investigation {
  id: string;
  title: string;
  description: string;
  status: 'active' | 'pending' | 'closed';
  priority: 'critical' | 'high' | 'medium' | 'low';
  assignee: string;
  createdAt: string;
  eventsLinked: number;
  progress: number;
  findings?: string[];
  timeline?: { date: string; action: string; user: string }[];
}

const initialInvestigations: Investigation[] = [
  {
    id: 'INV-001',
    title: 'Suspicious API Access Pattern Investigation',
    description: 'Investigating unusual API call patterns from multiple user accounts',
    status: 'active',
    priority: 'high',
    assignee: 'Alex Chen',
    createdAt: '2025-12-22T08:00:00Z',
    eventsLinked: 15,
    progress: 65,
    findings: [
      'Identified 3 user accounts with unusual activity',
      'API calls originating from unexpected geographic locations',
      'Pattern suggests automated script usage',
    ],
    timeline: [
      { date: '2025-12-22T08:00:00Z', action: 'Investigation created', user: 'System' },
      { date: '2025-12-22T09:30:00Z', action: 'Assigned to Alex Chen', user: 'Admin' },
      { date: '2025-12-22T10:15:00Z', action: 'Initial analysis completed', user: 'Alex Chen' },
    ],
  },
  {
    id: 'INV-002',
    title: 'Container Image Vulnerability Assessment',
    description: 'Analysis of critical CVE detected in production images',
    status: 'active',
    priority: 'critical',
    assignee: 'Sarah Johnson',
    createdAt: '2025-12-22T09:30:00Z',
    eventsLinked: 8,
    progress: 30,
    findings: [
      'CVE-2025-1234 confirmed in base image',
      'Affects 5 production containers',
    ],
    timeline: [
      { date: '2025-12-22T09:30:00Z', action: 'Investigation created', user: 'Security Scanner' },
      { date: '2025-12-22T10:00:00Z', action: 'Assigned to Sarah Johnson', user: 'Admin' },
    ],
  },
  {
    id: 'INV-003',
    title: 'Failed Login Attempts Analysis',
    description: 'Reviewing pattern of failed authentication attempts',
    status: 'pending',
    priority: 'medium',
    assignee: 'Mike Wilson',
    createdAt: '2025-12-21T14:00:00Z',
    eventsLinked: 23,
    progress: 10,
  },
  {
    id: 'INV-004',
    title: 'Firewall Rule Change Audit',
    description: 'Audit of recent security group modifications',
    status: 'closed',
    priority: 'low',
    assignee: 'Emily Davis',
    createdAt: '2025-12-20T10:00:00Z',
    eventsLinked: 5,
    progress: 100,
    findings: [
      'All changes were authorized',
      'Documentation verified',
      'No security concerns identified',
    ],
  },
];

const statusColors: Record<string, string> = {
  active: 'blue',
  pending: 'orange',
  closed: 'default',
};

const priorityColors: Record<string, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'gold',
  low: 'default',
};

const assigneeOptions = ['Alex Chen', 'Sarah Johnson', 'Mike Wilson', 'Emily Davis', 'John Smith'];

const SecurityInvestigationsPage: React.FC = () => {
  const [investigations, setInvestigations] = useState<Investigation[]>(initialInvestigations);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedInvestigation, setSelectedInvestigation] = useState<Investigation | null>(null);
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();

  const handleCreate = () => {
    form.validateFields().then((values) => {
      const newInvestigation: Investigation = {
        id: `INV-${String(Date.now()).slice(-3)}`,
        title: values.title,
        description: values.description,
        status: 'pending',
        priority: values.priority,
        assignee: values.assignee,
        createdAt: new Date().toISOString(),
        eventsLinked: 0,
        progress: 0,
        timeline: [
          { date: new Date().toISOString(), action: 'Investigation created', user: 'Current User' },
        ],
      };
      setInvestigations([newInvestigation, ...investigations]);
      message.success(`Investigation ${newInvestigation.id} created`);
      setIsCreateModalOpen(false);
      form.resetFields();
    });
  };

  const handleViewDetails = (investigation: Investigation) => {
    setSelectedInvestigation(investigation);
    setIsDetailDrawerOpen(true);
  };

  const handleStartInvestigation = (investigation: Investigation) => {
    setInvestigations(investigations.map(i =>
      i.id === investigation.id ? { ...i, status: 'active', progress: Math.max(i.progress, 10) } : i
    ));
    message.success(`Investigation ${investigation.id} started`);
  };

  const handleCloseInvestigation = (investigation: Investigation) => {
    setInvestigations(investigations.map(i =>
      i.id === investigation.id ? { ...i, status: 'closed', progress: 100 } : i
    ));
    message.success(`Investigation ${investigation.id} closed`);
  };

  const handleUpdateProgress = (investigation: Investigation, newProgress: number) => {
    setInvestigations(investigations.map(i =>
      i.id === investigation.id ? { ...i, progress: newProgress } : i
    ));
    message.success(`Progress updated to ${newProgress}%`);
  };

  const openEditModal = (investigation: Investigation) => {
    setSelectedInvestigation(investigation);
    editForm.setFieldsValue({
      title: investigation.title,
      description: investigation.description,
      priority: investigation.priority,
      assignee: investigation.assignee,
      progress: investigation.progress,
    });
    setIsEditModalOpen(true);
  };

  const handleEdit = () => {
    editForm.validateFields().then((values) => {
      setInvestigations(investigations.map(i =>
        i.id === selectedInvestigation?.id
          ? { ...i, ...values }
          : i
      ));
      message.success(`Investigation ${selectedInvestigation?.id} updated`);
      setIsEditModalOpen(false);
      setSelectedInvestigation(null);
    });
  };

  const columns: ColumnsType<Investigation> = [
    {
      title: 'Investigation',
      dataIndex: 'title',
      key: 'title',
      render: (text, record) => (
        <div>
          <Space style={{ marginBottom: 4 }}>
            <Text strong>{record.id}</Text>
            <Tag color={priorityColors[record.priority]}>{record.priority.toUpperCase()}</Tag>
          </Space>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: 12, color: '#666' }}>{record.description}</div>
        </div>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={statusColors[status]}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Assignee',
      dataIndex: 'assignee',
      key: 'assignee',
      width: 150,
      render: (name) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          {name}
        </Space>
      ),
    },
    {
      title: 'Events',
      dataIndex: 'eventsLinked',
      key: 'eventsLinked',
      width: 80,
      align: 'center',
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      width: 150,
      render: (progress) => (
        <Progress
          percent={progress}
          size="small"
          status={progress === 100 ? 'success' : 'active'}
        />
      ),
    },
    {
      title: 'Created',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 140,
      render: (date) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 180,
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<FileSearchOutlined />}
            onClick={() => handleViewDetails(record)}
            title="View Details"
          />
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => openEditModal(record)}
            title="Edit"
          />
          {record.status === 'pending' && (
            <Button
              type="primary"
              size="small"
              onClick={() => handleStartInvestigation(record)}
            >
              Start
            </Button>
          )}
          {record.status === 'active' && (
            <Popconfirm
              title="Close Investigation"
              description="Mark this investigation as closed?"
              onConfirm={() => handleCloseInvestigation(record)}
              okText="Close"
              cancelText="Cancel"
            >
              <Button size="small" icon={<CheckCircleOutlined />}>Close</Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Security Investigations</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsCreateModalOpen(true)}>
          New Investigation
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={investigations}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Create Modal */}
      <Modal
        title="Create New Investigation"
        open={isCreateModalOpen}
        onOk={handleCreate}
        onCancel={() => { setIsCreateModalOpen(false); form.resetFields(); }}
        okText="Create"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="Title" rules={[{ required: true }]}>
            <Input placeholder="Investigation title" />
          </Form.Item>
          <Form.Item name="description" label="Description" rules={[{ required: true }]}>
            <TextArea rows={3} placeholder="Describe the investigation scope" />
          </Form.Item>
          <Form.Item name="priority" label="Priority" rules={[{ required: true }]}>
            <Select placeholder="Select priority">
              <Select.Option value="critical">Critical</Select.Option>
              <Select.Option value="high">High</Select.Option>
              <Select.Option value="medium">Medium</Select.Option>
              <Select.Option value="low">Low</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="assignee" label="Assignee" rules={[{ required: true }]}>
            <Select placeholder="Select assignee">
              {assigneeOptions.map(a => <Select.Option key={a} value={a}>{a}</Select.Option>)}
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Edit Modal */}
      <Modal
        title={`Edit Investigation: ${selectedInvestigation?.id}`}
        open={isEditModalOpen}
        onOk={handleEdit}
        onCancel={() => { setIsEditModalOpen(false); setSelectedInvestigation(null); }}
        okText="Save"
      >
        <Form form={editForm} layout="vertical">
          <Form.Item name="title" label="Title" rules={[{ required: true }]}>
            <Input placeholder="Investigation title" />
          </Form.Item>
          <Form.Item name="description" label="Description" rules={[{ required: true }]}>
            <TextArea rows={3} placeholder="Describe the investigation scope" />
          </Form.Item>
          <Form.Item name="priority" label="Priority" rules={[{ required: true }]}>
            <Select placeholder="Select priority">
              <Select.Option value="critical">Critical</Select.Option>
              <Select.Option value="high">High</Select.Option>
              <Select.Option value="medium">Medium</Select.Option>
              <Select.Option value="low">Low</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="assignee" label="Assignee" rules={[{ required: true }]}>
            <Select placeholder="Select assignee">
              {assigneeOptions.map(a => <Select.Option key={a} value={a}>{a}</Select.Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="progress" label="Progress (%)">
            <Input type="number" min={0} max={100} />
          </Form.Item>
        </Form>
      </Modal>

      {/* Detail Drawer */}
      <Drawer
        title={`Investigation: ${selectedInvestigation?.id}`}
        open={isDetailDrawerOpen}
        onClose={() => { setIsDetailDrawerOpen(false); setSelectedInvestigation(null); }}
        width={600}
        extra={
          selectedInvestigation?.status === 'active' && (
            <Space>
              <Button onClick={() => handleUpdateProgress(selectedInvestigation, Math.min(100, selectedInvestigation.progress + 10))}>
                +10% Progress
              </Button>
              <Button type="primary" onClick={() => { handleCloseInvestigation(selectedInvestigation); setIsDetailDrawerOpen(false); }}>
                Close Investigation
              </Button>
            </Space>
          )
        }
      >
        {selectedInvestigation && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Descriptions bordered column={1}>
              <Descriptions.Item label="Title">{selectedInvestigation.title}</Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={statusColors[selectedInvestigation.status]}>{selectedInvestigation.status.toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Priority">
                <Tag color={priorityColors[selectedInvestigation.priority]}>{selectedInvestigation.priority.toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Assignee">
                <Space><Avatar size="small" icon={<UserOutlined />} />{selectedInvestigation.assignee}</Space>
              </Descriptions.Item>
              <Descriptions.Item label="Events Linked">
                <Button type="link" icon={<LinkOutlined />} style={{ padding: 0 }}>
                  {selectedInvestigation.eventsLinked} events
                </Button>
              </Descriptions.Item>
              <Descriptions.Item label="Progress">
                <Progress percent={selectedInvestigation.progress} />
              </Descriptions.Item>
            </Descriptions>

            <Card title="Description" size="small">
              <Paragraph>{selectedInvestigation.description}</Paragraph>
            </Card>

            {selectedInvestigation.findings && (
              <Card title="Findings" size="small">
                <ul style={{ paddingLeft: 20, margin: 0 }}>
                  {selectedInvestigation.findings.map((f, i) => (
                    <li key={i} style={{ marginBottom: 8 }}>{f}</li>
                  ))}
                </ul>
              </Card>
            )}

            {selectedInvestigation.timeline && (
              <Card title="Investigation Timeline" size="small">
                <Timeline
                  items={selectedInvestigation.timeline.map(t => ({
                    color: 'blue',
                    children: (
                      <div>
                        <Text strong>{t.action}</Text>
                        <div><Text type="secondary">{new Date(t.date).toLocaleString()} - {t.user}</Text></div>
                      </div>
                    ),
                  }))}
                />
              </Card>
            )}
          </Space>
        )}
      </Drawer>
    </div>
  );
};

export default SecurityInvestigationsPage;
