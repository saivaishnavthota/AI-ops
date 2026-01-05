import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';
import { Row, Col, Card, Statistic, Table, Tag, Space, Progress, Typography, Button } from 'antd';
import {
  WarningOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  PlusOutlined,
  PlayCircleOutlined,
  FileTextOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import { useDispatch } from 'react-redux';
import { useGetIncidentStatisticsQuery, useListIncidentsQuery, incidentsApi } from '../../store/api/incidentsApi';
import { useGetAlertStatisticsQuery } from '../../store/api/alertsApi';
import type { AppDispatch } from '../../app/store';
import type { Incident, IncidentStatus, IncidentPriority } from '../../types/models.types';

dayjs.extend(relativeTime);

const { Title } = Typography;

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

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  
  const { data: incidentStats, isLoading: loadingIncidents, refetch: refetchStats } = useGetIncidentStatisticsQuery();
  const { data: alertStats, isLoading: loadingAlerts } = useGetAlertStatisticsQuery();
  
  // State to force fresh fetch on every mount
  const [refreshKey, setRefreshKey] = React.useState(0);
  
  // Fetch recent incidents from API - always fetch fresh with cache busting
  const { data: incidentsData, isLoading: loadingRecentIncidents, refetch: refetchIncidents } = useListIncidentsQuery(
    {
      page: 1,
      page_size: 5,
      sort_by: 'created_at',
      sort_order: 'desc',
      _refresh: refreshKey, // Cache buster parameter (backend will ignore it)
    },
    {
      refetchOnMountOrArgChange: true,
      refetchOnFocus: true,
      refetchOnReconnect: true,
    }
  );

  // Force clear cache and refetch on mount
  useEffect(() => {
    // Clear all cached data
    dispatch(incidentsApi.util.invalidateTags([{ type: 'Incident', id: 'LIST' }]));
    dispatch(incidentsApi.util.invalidateTags([{ type: 'Incident' }]));
    
    // Force a new refresh key to trigger fresh fetch
    setRefreshKey(Date.now());
    
    // Immediately refetch
    refetchIncidents();
    refetchStats();
  }, []); // Only run once on mount

  const columns = [
    {
      title: 'Number',
      dataIndex: 'incident_number',
      key: 'incident_number',
      render: (text: string, record: Incident) => (
        <Link to={`/incidents/${record.id}`}>
          <strong>{text}</strong>
        </Link>
      ),
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (title: string, record: Incident) => (
        <Link to={`/incidents/${record.id}`}>{title}</Link>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
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
      render: (priority: IncidentPriority) => (
        <Tag color={priorityColors[priority]}>{priority.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).fromNow(),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>Dashboard</Title>

      {/* Stats Row */}
      <Row gutter={[24, 24]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Open Incidents"
              value={incidentStats?.open ?? 0}
              prefix={<WarningOutlined style={{ color: '#fa8c16' }} />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Alerts"
              value={alertStats?.firing ?? 0}
              prefix={<AlertOutlined style={{ color: '#f5222d' }} />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Resolved Today"
              value={incidentStats?.resolved ?? 0}
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="MTTR (Hours)"
              value={incidentStats?.mttr_hours ?? 2.5}
              precision={1}
              prefix={<ClockCircleOutlined style={{ color: '#1890ff' }} />}
              suffix={
                <span style={{ fontSize: 14, color: '#52c41a' }}>
                  <ArrowDownOutlined /> 12%
                </span>
              }
            />
          </Card>
        </Col>
      </Row>

      {/* Charts and Tables Row */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={16}>
          <Card 
            title="Recent Incidents" 
            extra={
              <Space>
                <Button 
                  type="text" 
                  size="small" 
                  icon={<ReloadOutlined />} 
                  onClick={() => {
                    // Clear cache
                    dispatch(incidentsApi.util.invalidateTags([{ type: 'Incident', id: 'LIST' }]));
                    dispatch(incidentsApi.util.invalidateTags([{ type: 'Incident' }]));
                    // Force new refresh key to trigger fresh fetch
                    setRefreshKey(Date.now());
                    // Refetch
                    refetchIncidents();
                    refetchStats();
                  }}
                >
                  Refresh
                </Button>
                <Link to="/incidents">View All</Link>
              </Space>
            }
          >
            <Table
              columns={columns}
              dataSource={
                !loadingRecentIncidents && incidentsData?.items && Array.isArray(incidentsData.items) && incidentsData.items.length > 0
                  ? incidentsData.items
                  : []
              }
              rowKey="id"
              pagination={false}
              size="small"
              loading={loadingRecentIncidents}
              locale={{
                emptyText: 'No incidents found'
              }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Alert Distribution">
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span>Critical</span>
                  <span style={{ color: '#f5222d' }}>{alertStats?.by_severity?.critical ?? 0}</span>
                </div>
                <Progress
                  percent={30}
                  showInfo={false}
                  strokeColor="#f5222d"
                  trailColor="#ffccc7"
                />
              </div>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span>Warning</span>
                  <span style={{ color: '#faad14' }}>{alertStats?.by_severity?.warning ?? 0}</span>
                </div>
                <Progress
                  percent={45}
                  showInfo={false}
                  strokeColor="#faad14"
                  trailColor="#fffbe6"
                />
              </div>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span>Info</span>
                  <span style={{ color: '#1890ff' }}>{alertStats?.by_severity?.info ?? 0}</span>
                </div>
                <Progress
                  percent={25}
                  showInfo={false}
                  strokeColor="#1890ff"
                  trailColor="#e6f7ff"
                />
              </div>
            </Space>
          </Card>

          <Card title="Quick Actions" style={{ marginTop: 24 }}>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Button
                type="link"
                icon={<PlusOutlined />}
                onClick={(e) => {
                  e.preventDefault();
                  console.log('Create new incident clicked');
                  navigate('/incidents?create=true', { replace: false });
                }}
                style={{ 
                  padding: '4px 0', 
                  height: 'auto', 
                  textAlign: 'left', 
                  justifyContent: 'flex-start',
                  display: 'flex',
                  alignItems: 'center',
                  width: '100%',
                  color: '#1890ff',
                  cursor: 'pointer'
                }}
                block
              >
                Create new incident
              </Button>
              <Button
                type="text"
                icon={<AlertOutlined />}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  navigate('/alerts');
                }}
                style={{ 
                  padding: '4px 0', 
                  height: 'auto', 
                  textAlign: 'left', 
                  justifyContent: 'flex-start',
                  display: 'flex',
                  alignItems: 'center',
                  width: '100%',
                  color: '#1890ff'
                }}
                block
              >
                View all alerts
              </Button>
              <Button
                type="text"
                icon={<PlayCircleOutlined />}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  navigate('/playbooks');
                }}
                style={{ 
                  padding: '4px 0', 
                  height: 'auto', 
                  textAlign: 'left', 
                  justifyContent: 'flex-start',
                  display: 'flex',
                  alignItems: 'center',
                  width: '100%',
                  color: '#1890ff'
                }}
                block
              >
                Run playbook
              </Button>
              <Button
                type="text"
                icon={<FileTextOutlined />}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  navigate('/analytics');
                }}
                style={{ 
                  padding: '4px 0', 
                  height: 'auto', 
                  textAlign: 'left', 
                  justifyContent: 'flex-start',
                  display: 'flex',
                  alignItems: 'center',
                  width: '100%',
                  color: '#1890ff'
                }}
                block
              >
                Generate report
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
