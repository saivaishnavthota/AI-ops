import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Table, Tag, Button, Space, Input, Select, Card, Typography, Tooltip, Badge, Modal, Form, message } from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  FilterOutlined,
  ReloadOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

import { useListIncidentsQuery, useCreateIncidentMutation } from '../../../store/api/incidentsApi';
import type { Incident, IncidentStatus, IncidentPriority, IncidentSeverity } from '../../../types/models.types';

dayjs.extend(relativeTime);

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const statusColors: Record<IncidentStatus, string> = {
  open: 'orange',
  acknowledged: 'blue',
  in_progress: 'purple',
  resolved: 'green',
  closed: 'default',
};

const priorityColors: Record<IncidentPriority, string> = {
  p1: 'red',
  p2: 'orange',
  p3: 'gold',
  p4: 'cyan',
  p5: 'default',
};

const severityColors: Record<IncidentSeverity, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'gold',
  low: 'cyan',
  info: 'blue',
};

const IncidentListPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string[]>([]);
  const [priorityFilter, setPriorityFilter] = useState<string[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [form] = Form.useForm();

  // Check if we should open the create modal from query parameter
  useEffect(() => {
    const shouldCreate = searchParams.get('create');
    console.log('IncidentListPage - create parameter:', shouldCreate, 'isCreateModalOpen:', isCreateModalOpen);
    if (shouldCreate === 'true') {
      console.log('Opening create modal');
      // Open modal after a small delay to ensure component is fully mounted
      const timer = setTimeout(() => {
        setIsCreateModalOpen(true);
        // Remove the query parameter from URL
        const newSearchParams = new URLSearchParams(searchParams);
        newSearchParams.delete('create');
        setSearchParams(newSearchParams, { replace: true });
      }, 150);
      return () => clearTimeout(timer);
    }
  }, [searchParams, setSearchParams]);

  const { data, isLoading, refetch } = useListIncidentsQuery({
    page,
    page_size: pageSize,
    search: search || undefined,
    status: statusFilter.length > 0 ? statusFilter : undefined,
    priority: priorityFilter.length > 0 ? priorityFilter : undefined,
    sort_by: 'created_at',
    sort_order: 'desc',
  });

  const [createIncident, { isLoading: isCreating }] = useCreateIncidentMutation();

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await createIncident(values).unwrap();
      message.success('Incident created successfully');
      setIsCreateModalOpen(false);
      form.resetFields();
      refetch();
    } catch (error) {
      message.error('Failed to create incident');
    }
  };

  const columns: ColumnsType<Incident> = [
    {
      title: 'Incident',
      dataIndex: 'incident_number',
      key: 'incident_number',
      width: 120,
      render: (number: string, record: Incident) => (
        <Link to={`/incidents/${record.id}`}>
          <strong>{number}</strong>
        </Link>
      ),
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (title: string, record: Incident) => (
        <Tooltip title={title}>
          <Link to={`/incidents/${record.id}`}>{title}</Link>
        </Tooltip>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: IncidentStatus) => (
        <Tag color={statusColors[status]}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority: IncidentPriority) => (
        <Tag color={priorityColors[priority]}>{priority.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity: IncidentSeverity) => (
        <Tag color={severityColors[severity]}>{severity.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Assigned To',
      dataIndex: 'assigned_user_name',
      key: 'assigned_user_name',
      width: 150,
      render: (name: string | null) => name || '-',
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 140,
      render: (date: string) => (
        <Tooltip title={dayjs(date).format('YYYY-MM-DD HH:mm:ss')}>
          {dayjs(date).fromNow()}
        </Tooltip>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 80,
      render: (_: unknown, record: Incident) => (
        <Link to={`/incidents/${record.id}`}>
          <Button type="text" icon={<EyeOutlined />} />
        </Link>
      ),
    },
  ];

  const handleTableChange = (pagination: TablePaginationConfig) => {
    setPage(pagination.current || 1);
    setPageSize(pagination.pageSize || 20);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ margin: 0 }}>Incidents</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsCreateModalOpen(true)}>
          Create Incident
        </Button>
      </div>

      <Card>
        {/* Filters */}
        <Space style={{ marginBottom: 16 }} wrap>
          <Input
            placeholder="Search incidents..."
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 250 }}
            allowClear
          />
          <Select
            mode="multiple"
            placeholder="Status"
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ minWidth: 150 }}
            allowClear
          >
            <Option value="open">Open</Option>
            <Option value="acknowledged">Acknowledged</Option>
            <Option value="in_progress">In Progress</Option>
            <Option value="resolved">Resolved</Option>
            <Option value="closed">Closed</Option>
          </Select>
          <Select
            mode="multiple"
            placeholder="Priority"
            value={priorityFilter}
            onChange={setPriorityFilter}
            style={{ minWidth: 120 }}
            allowClear
          >
            <Option value="p1">P1</Option>
            <Option value="p2">P2</Option>
            <Option value="p3">P3</Option>
            <Option value="p4">P4</Option>
            <Option value="p5">P5</Option>
          </Select>
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            Refresh
          </Button>
        </Space>

        {/* Table */}
        <Table
          columns={columns}
          dataSource={data?.items}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: page,
            pageSize,
            total: data?.total || 0,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} incidents`,
          }}
          onChange={handleTableChange}
          scroll={{ x: 1000 }}
        />
      </Card>

      {/* Create Incident Modal */}
      <Modal
        title="Create New Incident"
        open={isCreateModalOpen}
        onOk={handleCreate}
        onCancel={() => {
          setIsCreateModalOpen(false);
          form.resetFields();
        }}
        okText="Create"
        cancelText="Cancel"
        confirmLoading={isCreating}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="title"
            label="Title"
            rules={[{ required: true, message: 'Please enter incident title' }]}
          >
            <Input placeholder="Enter incident title" />
          </Form.Item>
          <Form.Item
            name="description"
            label="Description"
          >
            <TextArea rows={4} placeholder="Describe the incident in detail" />
          </Form.Item>
          <Form.Item
            name="priority"
            label="Priority"
            rules={[{ required: true, message: 'Please select priority' }]}
          >
            <Select placeholder="Select priority">
              <Option value="p1">P1 - Critical</Option>
              <Option value="p2">P2 - High</Option>
              <Option value="p3">P3 - Medium</Option>
              <Option value="p4">P4 - Low</Option>
              <Option value="p5">P5 - Planning</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="severity"
            label="Severity"
            rules={[{ required: true, message: 'Please select severity' }]}
          >
            <Select placeholder="Select severity">
              <Option value="critical">Critical</Option>
              <Option value="high">High</Option>
              <Option value="medium">Medium</Option>
              <Option value="low">Low</Option>
              <Option value="info">Info</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="category"
            label="Category"
          >
            <Input placeholder="Enter category (optional)" />
          </Form.Item>
          <Form.Item
            name="affected_services"
            label="Affected Services"
          >
            <Select
              mode="tags"
              placeholder="Enter affected services (press Enter to add)"
              style={{ width: '100%' }}
            />
          </Form.Item>
          <Form.Item
            name="tags"
            label="Tags"
          >
            <Select
              mode="tags"
              placeholder="Enter tags (press Enter to add)"
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default IncidentListPage;
