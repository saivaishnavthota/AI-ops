import React from 'react';
import { Row, Col, Card, Statistic, Table, Tag, Space, Progress, Typography } from 'antd';
import {
  WarningOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons';
import { useGetIncidentStatisticsQuery } from '../../store/api/incidentsApi';
import { useGetAlertStatisticsQuery } from '../../store/api/alertsApi';

const { Title } = Typography;

const DashboardPage: React.FC = () => {
  const { data: incidentStats, isLoading: loadingIncidents } = useGetIncidentStatisticsQuery();
  const { data: alertStats, isLoading: loadingAlerts } = useGetAlertStatisticsQuery();

  // Recent incidents mock data for demo
  const recentIncidents = [
    {
      key: '1',
      number: 'INC-000042',
      title: 'Database connection timeout',
      status: 'open',
      priority: 'p1',
      created: '10 mins ago',
    },
    {
      key: '2',
      number: 'INC-000041',
      title: 'API latency spike',
      status: 'acknowledged',
      priority: 'p2',
      created: '25 mins ago',
    },
    {
      key: '3',
      number: 'INC-000040',
      title: 'Memory usage warning',
      status: 'in_progress',
      priority: 'p3',
      created: '1 hour ago',
    },
    {
      key: '4',
      number: 'INC-000039',
      title: 'Certificate expiration warning',
      status: 'resolved',
      priority: 'p4',
      created: '2 hours ago',
    },
  ];

  const columns = [
    {
      title: 'Number',
      dataIndex: 'number',
      key: 'number',
      render: (text: string) => <a>{text}</a>,
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors: Record<string, string> = {
          open: 'orange',
          acknowledged: 'blue',
          in_progress: 'purple',
          resolved: 'green',
          closed: 'default',
        };
        return <Tag color={colors[status]}>{status.replace('_', ' ').toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority: string) => {
        const colors: Record<string, string> = {
          p1: 'red',
          p2: 'orange',
          p3: 'yellow',
          p4: 'cyan',
          p5: 'default',
        };
        return <Tag color={colors[priority]}>{priority.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Created',
      dataIndex: 'created',
      key: 'created',
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
          <Card title="Recent Incidents" extra={<a href="/incidents">View All</a>}>
            <Table
              columns={columns}
              dataSource={recentIncidents}
              pagination={false}
              size="small"
              loading={loadingIncidents}
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
            <Space direction="vertical" style={{ width: '100%' }}>
              <a>Create new incident</a>
              <a>View all alerts</a>
              <a>Run playbook</a>
              <a>Generate report</a>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
