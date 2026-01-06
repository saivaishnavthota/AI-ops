import React, { useState } from 'react';
import { Card, Table, Tag, Typography, Space, Button, Avatar, Progress, Modal, Form, Input, Select, message, Drawer, Timeline, Descriptions, Popconfirm } from 'antd';
import { PlusOutlined, UserOutlined, FileSearchOutlined, EditOutlined, CheckCircleOutlined, LinkOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useGetInvestigationsQuery,
  useCreateInvestigationMutation,
  useUpdateInvestigationMutation,
  Investigation,
} from '../../../store/api/investigationsApi';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

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
  const { data: investigationsData, isLoading } = useGetInvestigationsQuery({ skip: 0, limit: 100 });
  const [createInvestigation] = useCreateInvestigationMutation();
  const [updateInvestigation] = useUpdateInvestigationMutation();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedInvestigation, setSelectedInvestigation] = useState<Investigation | null>(null);
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();

  const investigations = investigationsData?.items || [];

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await createInvestigation({
        title: values.title,
        description: values.description,
        priority: values.priority,
        assignee_name: values.assignee,
      }).unwrap();
      message.success('Investigation created successfully');
      setIsCreateModalOpen(false);
      form.resetFields();
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to create investigation');
    }
  };

  const handleViewDetails = (investigation: Investigation) => {
    setSelectedInvestigation(investigation);
    setIsDetailDrawerOpen(true);
  };

  const handleStartInvestigation = async (investigation: Investigation) => {
    try {
      await updateInvestigation({
        id: investigation.id,
        data: {
          status: 'active',
          progress: Math.max(investigation.progress, 10),
        },
      }).unwrap();
      message.success(`Investigation ${investigation.id.substring(0, 8)} started`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to start investigation');
    }
  };

  const handleCloseInvestigation = async (investigation: Investigation) => {
    try {
      await updateInvestigation({
        id: investigation.id,
        data: {
          status: 'closed',
          progress: 100,
        },
      }).unwrap();
      message.success(`Investigation ${investigation.id.substring(0, 8)} closed`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to close investigation');
    }
  };

  const handleUpdateProgress = async (investigation: Investigation, newProgress: number) => {
    try {
      await updateInvestigation({
        id: investigation.id,
        data: { progress: newProgress },
      }).unwrap();
      message.success(`Progress updated to ${newProgress}%`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to update progress');
    }
  };

  const openEditModal = (investigation: Investigation) => {
    setSelectedInvestigation(investigation);
    editForm.setFieldsValue({
      title: investigation.title,
      description: investigation.description,
      priority: investigation.priority,
      assignee: investigation.assignee_name,
      progress: investigation.progress,
    });
    setIsEditModalOpen(true);
  };

  const handleEdit = async () => {
    if (!selectedInvestigation) return;
    try {
      const values = await editForm.validateFields();
      await updateInvestigation({
        id: selectedInvestigation.id,
        data: {
          title: values.title,
          description: values.description,
          priority: values.priority,
          assignee_name: values.assignee,
          progress: values.progress,
        },
      }).unwrap();
      message.success('Investigation updated successfully');
      setIsEditModalOpen(false);
      setSelectedInvestigation(null);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to update investigation');
    }
  };

  const columns: ColumnsType<Investigation> = [
    {
      title: 'Investigation',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: Investigation) => (
        <div>
          <Space style={{ marginBottom: 4 }}>
            <Text strong>{record.id.substring(0, 8)}</Text>
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
      render: (status: string) => (
        <Tag color={statusColors[status]}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Assignee',
      dataIndex: 'assignee_name',
      key: 'assignee_name',
      width: 150,
      render: (name: string) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          {name}
        </Space>
      ),
    },
    {
      title: 'Events',
      dataIndex: 'events_linked',
      key: 'events_linked',
      width: 80,
      align: 'center',
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      width: 150,
      render: (progress: number) => (
        <Progress
          percent={progress}
          size="small"
          status={progress === 100 ? 'success' : 'active'}
        />
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 140,
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 180,
      render: (_: any, record: Investigation) => (
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
          loading={isLoading}
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
        title={`Edit Investigation: ${selectedInvestigation?.id.substring(0, 8)}`}
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
        title={`Investigation: ${selectedInvestigation?.id.substring(0, 8)}`}
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
                <Space><Avatar size="small" icon={<UserOutlined />} />{selectedInvestigation.assignee_name}</Space>
              </Descriptions.Item>
              <Descriptions.Item label="Events Linked">
                <Button type="link" icon={<LinkOutlined />} style={{ padding: 0 }}>
                  {selectedInvestigation.events_linked} events
                </Button>
              </Descriptions.Item>
              <Descriptions.Item label="Progress">
                <Progress percent={selectedInvestigation.progress} />
              </Descriptions.Item>
            </Descriptions>

            <Card title="Description" size="small">
              <Paragraph>{selectedInvestigation.description}</Paragraph>
            </Card>

            {selectedInvestigation.findings && selectedInvestigation.findings.length > 0 && (
              <Card title="Findings" size="small">
                <ul style={{ paddingLeft: 20, margin: 0 }}>
                  {selectedInvestigation.findings.map((f, i) => (
                    <li key={i} style={{ marginBottom: 8 }}>{f}</li>
                  ))}
                </ul>
              </Card>
            )}

            {selectedInvestigation.timeline && selectedInvestigation.timeline.length > 0 && (
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
