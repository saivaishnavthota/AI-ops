import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Table, Tag, Button, Space, Input, Select, Card, Typography, Tooltip, Badge } from 'antd';
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

import { useListIncidentsQuery } from '../../../store/api/incidentsApi';
import type { Incident, IncidentStatus, IncidentPriority, IncidentSeverity } from '../../../types/models.types';

dayjs.extend(relativeTime);

const { Title } = Typography;
const { Option } = Select;

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
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string[]>([]);
  const [priorityFilter, setPriorityFilter] = useState<string[]>([]);

  const { data, isLoading, refetch } = useListIncidentsQuery({
    page,
    page_size: pageSize,
    search: search || undefined,
    status: statusFilter.length > 0 ? statusFilter : undefined,
    priority: priorityFilter.length > 0 ? priorityFilter : undefined,
    sort_by: 'created_at',
    sort_order: 'desc',
  });

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
        <Button type="primary" icon={<PlusOutlined />}>
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
    </div>
  );
};

export default IncidentListPage;
