import React, { useState } from 'react';
import { Card, Table, Tag, Typography, Space, Button, Avatar, Input, Modal, Form, Select, message, Drawer, Descriptions, Timeline, Popconfirm } from 'antd';
import { PlusOutlined, UserOutlined, SearchOutlined, CheckCircleOutlined, CommentOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useGetTicketsQuery,
  useCreateTicketMutation,
  useUpdateTicketMutation,
  Ticket,
} from '../../../store/api/ticketsApi';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const statusColors: Record<string, string> = {
  open: 'blue',
  in_progress: 'orange',
  pending: 'gold',
  resolved: 'green',
  closed: 'default',
};

const priorityColors: Record<string, string> = {
  urgent: 'red',
  high: 'orange',
  normal: 'blue',
  low: 'default',
};

const categoryOptions = ['Access Issue', 'Service Request', 'Performance', 'Bug Report', 'Feature Request', 'Other'];
const assigneeOptions = ['Support Team', 'Mike Wilson', 'Emily Davis', 'Alex Chen', 'John Smith'];

const TicketsPage: React.FC = () => {
  const { data: ticketsData, isLoading } = useGetTicketsQuery({ skip: 0, limit: 100 });
  const [createTicket] = useCreateTicketMutation();
  const [updateTicket] = useUpdateTicketMutation();

  const [searchText, setSearchText] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [newComment, setNewComment] = useState('');
  const [form] = Form.useForm();

  const tickets = ticketsData?.items || [];

  const filteredTickets = tickets.filter(t =>
    t.subject.toLowerCase().includes(searchText.toLowerCase()) ||
    t.id.toLowerCase().includes(searchText.toLowerCase()) ||
    t.requester_name.toLowerCase().includes(searchText.toLowerCase())
  );

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await createTicket({
        subject: values.subject,
        description: values.description,
        priority: values.priority,
        category: values.category,
        assignee_name: values.assignee || undefined,
      }).unwrap();
      message.success('Ticket created successfully');
      setIsCreateModalOpen(false);
      form.resetFields();
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to create ticket');
    }
  };

  const handleViewDetails = (ticket: Ticket) => {
    setSelectedTicket(ticket);
    setIsDetailDrawerOpen(true);
  };

  const handleAssign = async (ticket: Ticket, assignee: string) => {
    try {
      await updateTicket({
        id: ticket.id,
        data: {
          assignee_name: assignee,
          status: ticket.status === 'open' ? 'in_progress' : ticket.status,
        },
      }).unwrap();
      message.success(`Ticket assigned to ${assignee}`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to assign ticket');
    }
  };

  const handleResolve = async (ticket: Ticket) => {
    try {
      await updateTicket({
        id: ticket.id,
        data: { status: 'resolved' },
      }).unwrap();
      message.success(`Ticket ${ticket.id} resolved`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to resolve ticket');
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim() || !selectedTicket) return;

    try {
      const comment = { user: 'Current User', text: newComment, time: new Date().toISOString() };
      const updatedComments = [...(selectedTicket.comments || []), comment];

      await updateTicket({
        id: selectedTicket.id,
        data: { comments: updatedComments },
      }).unwrap();

      setSelectedTicket({
        ...selectedTicket,
        comments: updatedComments,
      });
      setNewComment('');
      message.success('Comment added');
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to add comment');
    }
  };

  const columns: ColumnsType<Ticket> = [
    {
      title: 'Ticket',
      dataIndex: 'subject',
      key: 'subject',
      render: (text: string, record: Ticket) => (
        <div>
          <Space style={{ marginBottom: 4 }}>
            <Text strong>{record.id.substring(0, 8)}</Text>
            <Tag>{record.category}</Tag>
          </Space>
          <div style={{ fontWeight: 500 }}>{text}</div>
        </div>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => (
        <Tag color={statusColors[status]}>{status.replace('_', ' ').toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority: string) => (
        <Tag color={priorityColors[priority]}>{priority.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Requester',
      dataIndex: 'requester_name',
      key: 'requester_name',
      width: 140,
      render: (name: string) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          {name}
        </Space>
      ),
    },
    {
      title: 'Assignee',
      dataIndex: 'assignee_name',
      key: 'assignee_name',
      width: 140,
      render: (name: string | null, record: Ticket) => name ? (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          {name}
        </Space>
      ) : (
        <Select
          placeholder="Assign"
          size="small"
          style={{ width: 120 }}
          onChange={(value) => handleAssign(record, value)}
        >
          {assigneeOptions.map(a => <Select.Option key={a} value={a}>{a}</Select.Option>)}
        </Select>
      ),
    },
    {
      title: 'Updated',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 140,
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_: any, record: Ticket) => (
        <Space>
          <Button
            type="text"
            icon={<SearchOutlined />}
            onClick={() => handleViewDetails(record)}
            title="View Details"
          />
          {record.status === 'in_progress' && (
            <Popconfirm
              title="Resolve Ticket"
              description="Mark this ticket as resolved?"
              onConfirm={() => handleResolve(record)}
              okText="Resolve"
              cancelText="Cancel"
            >
              <Button size="small" type="primary" icon={<CheckCircleOutlined />}>
                Resolve
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Support Tickets</Title>
        <Space>
          <Input
            placeholder="Search tickets..."
            prefix={<SearchOutlined />}
            style={{ width: 250 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsCreateModalOpen(true)}>
            New Ticket
          </Button>
        </Space>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={filteredTickets}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Create Modal */}
      <Modal
        title="Create New Ticket"
        open={isCreateModalOpen}
        onOk={handleCreate}
        onCancel={() => { setIsCreateModalOpen(false); form.resetFields(); }}
        okText="Create"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="subject" label="Subject" rules={[{ required: true }]}>
            <Input placeholder="Brief description of the issue" />
          </Form.Item>
          <Form.Item name="description" label="Description" rules={[{ required: true }]}>
            <TextArea rows={4} placeholder="Detailed description of the issue" />
          </Form.Item>
          <Form.Item name="category" label="Category" rules={[{ required: true }]}>
            <Select placeholder="Select category">
              {categoryOptions.map(c => <Select.Option key={c} value={c}>{c}</Select.Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="priority" label="Priority" rules={[{ required: true }]}>
            <Select placeholder="Select priority">
              <Select.Option value="urgent">Urgent</Select.Option>
              <Select.Option value="high">High</Select.Option>
              <Select.Option value="normal">Normal</Select.Option>
              <Select.Option value="low">Low</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="assignee" label="Assignee">
            <Select placeholder="Assign to (optional)">
              {assigneeOptions.map(a => <Select.Option key={a} value={a}>{a}</Select.Option>)}
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Detail Drawer */}
      <Drawer
        title={`Ticket: ${selectedTicket?.id.substring(0, 8)}`}
        open={isDetailDrawerOpen}
        onClose={() => { setIsDetailDrawerOpen(false); setSelectedTicket(null); setNewComment(''); }}
        width={600}
        extra={
          selectedTicket?.status === 'in_progress' && (
            <Button type="primary" onClick={() => { handleResolve(selectedTicket); setIsDetailDrawerOpen(false); }}>
              Resolve Ticket
            </Button>
          )
        }
      >
        {selectedTicket && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Descriptions bordered column={1}>
              <Descriptions.Item label="Subject">{selectedTicket.subject}</Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={statusColors[selectedTicket.status]}>{selectedTicket.status.replace('_', ' ').toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Priority">
                <Tag color={priorityColors[selectedTicket.priority]}>{selectedTicket.priority.toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Category"><Tag>{selectedTicket.category}</Tag></Descriptions.Item>
              <Descriptions.Item label="Requester">
                <Space><Avatar size="small" icon={<UserOutlined />} />{selectedTicket.requester_name}</Space>
              </Descriptions.Item>
              <Descriptions.Item label="Assignee">
                {selectedTicket.assignee_name ? (
                  <Space><Avatar size="small" icon={<UserOutlined />} />{selectedTicket.assignee_name}</Space>
                ) : <Text type="secondary">Unassigned</Text>}
              </Descriptions.Item>
              <Descriptions.Item label="Created">{new Date(selectedTicket.created_at).toLocaleString()}</Descriptions.Item>
            </Descriptions>

            <Card title="Description" size="small">
              <Paragraph>{selectedTicket.description}</Paragraph>
            </Card>

            <Card title="Comments" size="small">
              {selectedTicket.comments && selectedTicket.comments.length > 0 ? (
                <Timeline
                  items={selectedTicket.comments.map((c: any) => ({
                    color: 'blue',
                    dot: <CommentOutlined />,
                    children: (
                      <div>
                        <Text strong>{c.user}</Text>
                        <Text type="secondary" style={{ marginLeft: 8 }}>{new Date(c.time).toLocaleString()}</Text>
                        <Paragraph style={{ margin: '4px 0 0 0' }}>{c.text}</Paragraph>
                      </div>
                    ),
                  }))}
                />
              ) : (
                <Text type="secondary">No comments yet</Text>
              )}
              <div style={{ marginTop: 16 }}>
                <TextArea
                  rows={2}
                  placeholder="Add a comment..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                />
                <Button type="primary" style={{ marginTop: 8 }} onClick={handleAddComment}>
                  Add Comment
                </Button>
              </div>
            </Card>
          </Space>
        )}
      </Drawer>
    </div>
  );
};

export default TicketsPage;
