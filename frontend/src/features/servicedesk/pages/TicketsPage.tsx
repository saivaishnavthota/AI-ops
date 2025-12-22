import React, { useState } from 'react';
import { Card, Table, Tag, Typography, Space, Button, Avatar, Input, Modal, Form, Select, message, Drawer, Descriptions, Timeline, Popconfirm } from 'antd';
import { PlusOutlined, UserOutlined, SearchOutlined, EditOutlined, CheckCircleOutlined, CommentOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

interface Ticket {
  id: string;
  subject: string;
  description: string;
  status: 'open' | 'in_progress' | 'pending' | 'resolved' | 'closed';
  priority: 'urgent' | 'high' | 'normal' | 'low';
  requester: string;
  assignee: string | null;
  category: string;
  createdAt: string;
  updatedAt: string;
  comments?: { user: string; text: string; time: string }[];
}

const initialTickets: Ticket[] = [
  {
    id: 'TKT-001',
    subject: 'Cannot access production dashboard',
    description: 'Getting 403 error when trying to access the main dashboard. This started happening after the recent deployment.',
    status: 'open',
    priority: 'high',
    requester: 'John Smith',
    assignee: 'Support Team',
    category: 'Access Issue',
    createdAt: '2025-12-22T10:00:00Z',
    updatedAt: '2025-12-22T10:00:00Z',
    comments: [
      { user: 'John Smith', text: 'This is blocking my work', time: '2025-12-22T10:05:00Z' },
    ],
  },
  {
    id: 'TKT-002',
    subject: 'Request for new API key',
    description: 'Need a new API key for the reporting integration. The old one expired.',
    status: 'in_progress',
    priority: 'normal',
    requester: 'Sarah Johnson',
    assignee: 'Mike Wilson',
    category: 'Service Request',
    createdAt: '2025-12-22T09:30:00Z',
    updatedAt: '2025-12-22T10:15:00Z',
    comments: [
      { user: 'Mike Wilson', text: 'Generating new API key now', time: '2025-12-22T10:15:00Z' },
    ],
  },
  {
    id: 'TKT-003',
    subject: 'Slow response times on API',
    description: 'API response times have increased significantly since yesterday. P95 latency is now over 2 seconds.',
    status: 'in_progress',
    priority: 'urgent',
    requester: 'Alex Chen',
    assignee: 'Emily Davis',
    category: 'Performance',
    createdAt: '2025-12-22T08:00:00Z',
    updatedAt: '2025-12-22T10:30:00Z',
    comments: [
      { user: 'Emily Davis', text: 'Investigating database connection pool', time: '2025-12-22T09:00:00Z' },
      { user: 'Emily Davis', text: 'Found the issue - scaling up the database', time: '2025-12-22T10:30:00Z' },
    ],
  },
  {
    id: 'TKT-004',
    subject: 'Update user permissions',
    description: 'Please add admin access for the new team member Tom Anderson.',
    status: 'pending',
    priority: 'low',
    requester: 'Lisa Brown',
    assignee: null,
    category: 'Access Issue',
    createdAt: '2025-12-21T16:00:00Z',
    updatedAt: '2025-12-21T16:00:00Z',
  },
  {
    id: 'TKT-005',
    subject: 'Monthly report generation failed',
    description: 'The scheduled monthly report did not generate this morning. Error: Timeout exceeded.',
    status: 'resolved',
    priority: 'normal',
    requester: 'Tom Anderson',
    assignee: 'Support Team',
    category: 'Bug Report',
    createdAt: '2025-12-21T09:00:00Z',
    updatedAt: '2025-12-21T14:00:00Z',
    comments: [
      { user: 'Support Team', text: 'Increased timeout and reran the report successfully', time: '2025-12-21T14:00:00Z' },
    ],
  },
];

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
  const [tickets, setTickets] = useState<Ticket[]>(initialTickets);
  const [searchText, setSearchText] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [newComment, setNewComment] = useState('');
  const [form] = Form.useForm();

  const filteredTickets = tickets.filter(t =>
    t.subject.toLowerCase().includes(searchText.toLowerCase()) ||
    t.id.toLowerCase().includes(searchText.toLowerCase()) ||
    t.requester.toLowerCase().includes(searchText.toLowerCase())
  );

  const handleCreate = () => {
    form.validateFields().then((values) => {
      const newTicket: Ticket = {
        id: `TKT-${String(Date.now()).slice(-3)}`,
        subject: values.subject,
        description: values.description,
        status: 'open',
        priority: values.priority,
        requester: 'Current User',
        assignee: values.assignee || null,
        category: values.category,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        comments: [],
      };
      setTickets([newTicket, ...tickets]);
      message.success(`Ticket ${newTicket.id} created`);
      setIsCreateModalOpen(false);
      form.resetFields();
    });
  };

  const handleViewDetails = (ticket: Ticket) => {
    setSelectedTicket(ticket);
    setIsDetailDrawerOpen(true);
  };

  const handleAssign = (ticket: Ticket, assignee: string) => {
    setTickets(tickets.map(t =>
      t.id === ticket.id
        ? { ...t, assignee, status: t.status === 'open' ? 'in_progress' : t.status, updatedAt: new Date().toISOString() }
        : t
    ));
    message.success(`Ticket assigned to ${assignee}`);
  };

  const handleResolve = (ticket: Ticket) => {
    setTickets(tickets.map(t =>
      t.id === ticket.id ? { ...t, status: 'resolved', updatedAt: new Date().toISOString() } : t
    ));
    message.success(`Ticket ${ticket.id} resolved`);
  };

  const handleAddComment = () => {
    if (!newComment.trim() || !selectedTicket) return;
    const comment = { user: 'Current User', text: newComment, time: new Date().toISOString() };
    setTickets(tickets.map(t =>
      t.id === selectedTicket.id
        ? { ...t, comments: [...(t.comments || []), comment], updatedAt: new Date().toISOString() }
        : t
    ));
    setSelectedTicket({
      ...selectedTicket,
      comments: [...(selectedTicket.comments || []), comment],
    });
    setNewComment('');
    message.success('Comment added');
  };

  const columns: ColumnsType<Ticket> = [
    {
      title: 'Ticket',
      dataIndex: 'subject',
      key: 'subject',
      render: (text, record) => (
        <div>
          <Space style={{ marginBottom: 4 }}>
            <Text strong>{record.id}</Text>
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
      render: (status) => (
        <Tag color={statusColors[status]}>{status.replace('_', ' ').toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority) => (
        <Tag color={priorityColors[priority]}>{priority.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Requester',
      dataIndex: 'requester',
      key: 'requester',
      width: 140,
      render: (name) => (
        <Space>
          <Avatar size="small" icon={<UserOutlined />} />
          {name}
        </Space>
      ),
    },
    {
      title: 'Assignee',
      dataIndex: 'assignee',
      key: 'assignee',
      width: 140,
      render: (name, record) => name ? (
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
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      width: 140,
      render: (date) => new Date(date).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_, record) => (
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
        title={`Ticket: ${selectedTicket?.id}`}
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
                <Space><Avatar size="small" icon={<UserOutlined />} />{selectedTicket.requester}</Space>
              </Descriptions.Item>
              <Descriptions.Item label="Assignee">
                {selectedTicket.assignee ? (
                  <Space><Avatar size="small" icon={<UserOutlined />} />{selectedTicket.assignee}</Space>
                ) : <Text type="secondary">Unassigned</Text>}
              </Descriptions.Item>
              <Descriptions.Item label="Created">{new Date(selectedTicket.createdAt).toLocaleString()}</Descriptions.Item>
            </Descriptions>

            <Card title="Description" size="small">
              <Paragraph>{selectedTicket.description}</Paragraph>
            </Card>

            <Card title="Comments" size="small">
              {selectedTicket.comments && selectedTicket.comments.length > 0 ? (
                <Timeline
                  items={selectedTicket.comments.map(c => ({
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
