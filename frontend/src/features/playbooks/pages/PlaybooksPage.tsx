import React, { useState } from 'react';
import { Card, Table, Button, Tag, Space, Typography, Progress, Modal, Form, Input, Select, message, Popconfirm, Drawer, Timeline } from 'antd';
import { PlusOutlined, PlayCircleOutlined, EditOutlined, DeleteOutlined, HistoryOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useGetPlaybooksQuery,
  useCreatePlaybookMutation,
  useUpdatePlaybookMutation,
  useDeletePlaybookMutation,
  useExecutePlaybookMutation,
  useGetPlaybookExecutionsQuery,
  Playbook,
  PlaybookExecution,
} from '../../../store/api/playbooksApi';

const { Title, Text } = Typography;
const { TextArea } = Input;

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
  const { data: playbooksData, isLoading } = useGetPlaybooksQuery({ skip: 0, limit: 100 });
  const [createPlaybook] = useCreatePlaybookMutation();
  const [updatePlaybook] = useUpdatePlaybookMutation();
  const [deletePlaybook] = useDeletePlaybookMutation();
  const [executePlaybook] = useExecutePlaybookMutation();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isHistoryDrawerOpen, setIsHistoryDrawerOpen] = useState(false);
  const [selectedPlaybook, setSelectedPlaybook] = useState<Playbook | null>(null);
  const [runningPlaybooks, setRunningPlaybooks] = useState<Set<string>>(new Set());
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();

  const { data: executionsData } = useGetPlaybookExecutionsQuery(
    { id: selectedPlaybook?.id || '', skip: 0, limit: 50 },
    { skip: !selectedPlaybook?.id }
  );

  const playbooks = playbooksData?.items || [];

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await createPlaybook({
        name: values.name,
        description: values.description,
        trigger_conditions: { trigger: values.trigger },
        steps: [{ type: 'script', name: 'Default step', config: {} }],
        requires_approval: false,
        tags: [],
      }).unwrap();
      message.success(`Playbook "${values.name}" created successfully`);
      setIsCreateModalOpen(false);
      form.resetFields();
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to create playbook');
    }
  };

  const handleEdit = async () => {
    if (!selectedPlaybook) return;
    try {
      const values = await editForm.validateFields();
      await updatePlaybook({
        id: selectedPlaybook.id,
        data: {
          name: values.name,
          description: values.description,
          trigger_conditions: { trigger: values.trigger },
          is_active: values.status === 'active',
        },
      }).unwrap();
      message.success(`Playbook "${values.name}" updated successfully`);
      setIsEditModalOpen(false);
      setSelectedPlaybook(null);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to update playbook');
    }
  };

  const handleDelete = async (playbook: Playbook) => {
    try {
      await deletePlaybook(playbook.id).unwrap();
      message.success(`Playbook "${playbook.name}" deleted`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to delete playbook');
    }
  };

  const handleRun = async (playbook: Playbook) => {
    setRunningPlaybooks(prev => new Set(prev).add(playbook.id));
    message.loading(`Running playbook "${playbook.name}"...`, 2);

    try {
      await executePlaybook({
        id: playbook.id,
        data: {},
      }).unwrap();
      message.success(`Playbook "${playbook.name}" executed successfully`);
    } catch (error: any) {
      message.error(error?.data?.detail || `Playbook "${playbook.name}" execution failed`);
    } finally {
      setRunningPlaybooks(prev => {
        const next = new Set(prev);
        next.delete(playbook.id);
        return next;
      });
    }
  };

  const openEditModal = (playbook: Playbook) => {
    setSelectedPlaybook(playbook);
    editForm.setFieldsValue({
      name: playbook.name,
      description: playbook.description,
      trigger: playbook.trigger_conditions?.trigger || '',
      status: playbook.is_active ? 'active' : 'inactive',
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
      render: (text: string, record: Playbook) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: 12, color: '#888' }}>{record.description}</div>
        </div>
      ),
    },
    {
      title: 'Trigger',
      dataIndex: 'trigger_conditions',
      key: 'trigger',
      render: (trigger_conditions: any) => <Tag>{trigger_conditions?.trigger || 'Manual'}</Tag>,
    },
    {
      title: 'Status',
      key: 'status',
      render: (_: any, record: Playbook) => {
        const status = record.is_active ? 'active' : 'inactive';
        return <Tag color={statusColors[status]}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Executions',
      dataIndex: 'execution_count',
      key: 'execution_count',
      align: 'center',
    },
    {
      title: 'Success Rate',
      dataIndex: 'success_rate',
      key: 'success_rate',
      render: (rate: number) => (
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
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Playbook) => (
        <Space>
          <Button
            type="text"
            icon={<PlayCircleOutlined />}
            disabled={!record.is_active || runningPlaybooks.has(record.id)}
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

  const executions = executionsData?.items || [];

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
          loading={isLoading}
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
        {executions.length > 0 ? (
          <Timeline
            items={executions.map((h: PlaybookExecution) => ({
              color: h.status === 'completed' ? 'green' : h.status === 'failed' ? 'red' : 'blue',
              dot: h.status === 'completed' ? <CheckCircleOutlined /> : h.status === 'failed' ? <CloseCircleOutlined /> : undefined,
              children: (
                <div>
                  <div><Text strong>{h.status.toUpperCase()}</Text></div>
                  <div><Text type="secondary">{new Date(h.created_at).toLocaleString()}</Text></div>
                  <div><Text type="secondary">Duration: {h.duration_seconds}s</Text></div>
                  <div><Text type="secondary">Triggered by: {h.triggered_by || 'Manual'}</Text></div>
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
