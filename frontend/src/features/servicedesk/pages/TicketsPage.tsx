import React, { useState } from 'react';
import { Card, Table, Tag, Typography, Space, Button, Avatar, Input, Modal, Form, Select, message, Drawer, Descriptions, Timeline, Popconfirm, List, Divider } from 'antd';
import { PlusOutlined, UserOutlined, SearchOutlined, CheckCircleOutlined, CommentOutlined, BookOutlined, LinkOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import {
  useGetTicketsQuery,
  useCreateTicketMutation,
  useUpdateTicketMutation,
  useAssignTicketMutation,
  useResolveTicketWithFeedbackMutation,
  useGetRelatedKBArticlesQuery,
  Ticket,
} from '../../../store/api/ticketsApi';
import { useGetAssignableUsersQuery } from '../../../store/api/usersApi';

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

// Related KB Articles Component
interface RelatedKBArticlesSectionProps {
  ticketId: string;
  onViewArticle: (articleId: string) => void;
}

const RelatedKBArticlesSection: React.FC<RelatedKBArticlesSectionProps> = ({ ticketId, onViewArticle }) => {
  const { data: relatedArticles = [], isLoading } = useGetRelatedKBArticlesQuery(ticketId);

  if (isLoading) {
    return (
      <Card
        title={
          <Space>
            <BookOutlined />
            <span>Related Knowledge Base Articles</span>
            <Tag color="blue">AI Recommended</Tag>
          </Space>
        }
        size="small"
      >
        <Text type="secondary">Loading related articles...</Text>
      </Card>
    );
  }

  if (!relatedArticles || relatedArticles.length === 0) {
    return null; // Don't show the section if no articles found
  }

  return (
    <Card
      title={
        <Space>
          <BookOutlined />
          <span>Related Knowledge Base Articles</span>
          <Tag color="blue">AI Recommended</Tag>
        </Space>
      }
      size="small"
    >
      <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
        These articles might help resolve this ticket faster
      </Text>
      <List
        dataSource={relatedArticles}
        renderItem={(article) => (
          <List.Item
            key={article.id}
            style={{ cursor: 'pointer', padding: '12px 0' }}
            onClick={() => onViewArticle(article.id)}
          >
            <List.Item.Meta
              avatar={<BookOutlined style={{ fontSize: 20, color: '#1890ff' }} />}
              title={
                <Space>
                  <a onClick={(e) => { e.stopPropagation(); onViewArticle(article.id); }}>
                    {article.title}
                  </a>
                  <Tag color="green">{Math.round(article.relevance_score * 100)}% match</Tag>
                </Space>
              }
              description={
                <div>
                  <Paragraph
                    ellipsis={{ rows: 2 }}
                    style={{ margin: '4px 0', color: '#666' }}
                  >
                    {article.excerpt}
                  </Paragraph>
                  <Space size="small" style={{ marginTop: 4 }}>
                    <Tag>{article.category}</Tag>
                    {article.tags.slice(0, 3).map(tag => (
                      <Tag key={tag} color="default">{tag}</Tag>
                    ))}
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {article.views} views • {article.helpful_count} helpful
                    </Text>
                  </Space>
                </div>
              }
            />
            <LinkOutlined style={{ fontSize: 16, color: '#1890ff' }} />
          </List.Item>
        )}
      />
    </Card>
  );
};

const TicketsPage: React.FC = () => {
  const navigate = useNavigate();
  const { data: ticketsData, isLoading } = useGetTicketsQuery({ skip: 0, limit: 100 });
  const { data: assignableUsers = [] } = useGetAssignableUsersQuery();
  const [createTicket] = useCreateTicketMutation();
  const [updateTicket] = useUpdateTicketMutation();
  const [assignTicket] = useAssignTicketMutation();
  const [resolveTicketWithFeedback] = useResolveTicketWithFeedbackMutation();

  const [searchText, setSearchText] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [newComment, setNewComment] = useState('');
  const [form] = Form.useForm();
  const [feedbackForm] = Form.useForm();

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

  // Navigate to KB article
  const handleViewKBArticle = (articleId: string) => {
    setIsDetailDrawerOpen(false);
    navigate(`/knowledge-base?article=${articleId}`);
  };

  const handleAssign = async (ticket: Ticket, assigneeId: string) => {
    try {
      await assignTicket({
        id: ticket.id,
        data: { assignee_id: assigneeId },
      }).unwrap();
      const assignedUser = assignableUsers.find(u => u.id === assigneeId);
      message.success(`Ticket assigned to ${assignedUser?.name || 'user'}`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to assign ticket');
    }
  };

  const handleResolve = (ticket: Ticket) => {
    setSelectedTicket(ticket);
    setIsFeedbackModalOpen(true);
  };

  const handleResolveWithFeedback = async () => {
    if (!selectedTicket) return;

    try {
      const values = await feedbackForm.validateFields();
      await resolveTicketWithFeedback({
        id: selectedTicket.id,
        feedback: {
          title: values.title,
          content: values.content,
          tags: values.tags || [],
        },
      }).unwrap();
      message.success('Ticket resolved and knowledge shared!');
      setIsFeedbackModalOpen(false);
      setSelectedTicket(null);
      feedbackForm.resetFields();
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
          {assignableUsers.map(user => (
            <Select.Option key={user.id} value={user.id}>
              {user.name}
            </Select.Option>
          ))}
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
            <Button
              size="small"
              type="primary"
              icon={<CheckCircleOutlined />}
              onClick={() => handleResolve(record)}
            >
              Resolve
            </Button>
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
              {assignableUsers.map(user => (
                <Select.Option key={user.id} value={user.name}>
                  {user.display_name}
                </Select.Option>
              ))}
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
            <Button type="primary" onClick={() => {
              setIsDetailDrawerOpen(false);
              handleResolve(selectedTicket);
            }}>
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

            {/* Related KB Articles Section */}
            <RelatedKBArticlesSection
              ticketId={selectedTicket.id}
              onViewArticle={handleViewKBArticle}
            />
          </Space>
        )}
      </Drawer>

      {/* Feedback Modal for Resolve */}
      <Modal
        title="Resolve Ticket & Share Knowledge"
        open={isFeedbackModalOpen}
        onOk={handleResolveWithFeedback}
        onCancel={() => {
          setIsFeedbackModalOpen(false);
          setSelectedTicket(null);
          feedbackForm.resetFields();
        }}
        okText="Resolve & Share"
        width={600}
      >
        <div style={{ marginBottom: 16 }}>
          <Text type="secondary">
            Share your solution to help other team members resolve similar issues in the future.
            This will create a knowledge base article automatically.
          </Text>
        </div>
        <Form form={feedbackForm} layout="vertical">
          <Form.Item
            name="title"
            label="Solution Title"
            rules={[{ required: true, message: 'Please provide a title for the solution' }]}
          >
            <Input placeholder="Brief title describing the solution" />
          </Form.Item>
          <Form.Item
            name="content"
            label="Solution Details"
            rules={[{ required: true, message: 'Please describe how you solved this issue' }]}
          >
            <TextArea
              rows={6}
              placeholder="Describe the steps you took to resolve this issue, including any troubleshooting steps, root cause, and final solution..."
            />
          </Form.Item>
          <Form.Item name="tags" label="Tags (Optional)">
            <Select
              mode="tags"
              placeholder="Type to add tags (e.g., network, database, authentication)"
              style={{ width: '100%' }}
              tokenSeparators={[',']}
              options={[
                { value: 'network', label: 'network' },
                { value: 'database', label: 'database' },
                { value: 'authentication', label: 'authentication' },
                { value: 'performance', label: 'performance' },
                { value: 'security', label: 'security' },
                { value: 'api', label: 'api' },
                { value: 'configuration', label: 'configuration' },
                { value: 'deployment', label: 'deployment' },
                { value: 'monitoring', label: 'monitoring' },
                { value: 'troubleshooting', label: 'troubleshooting' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TicketsPage;
