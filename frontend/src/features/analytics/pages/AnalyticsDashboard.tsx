import React, { useState } from 'react';
import { Card, Row, Col, Typography, Statistic, Space, Select, DatePicker, Table, Progress, Tag, Tabs, List, Avatar, Spin } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  SafetyOutlined,
  CloudOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useGetAnalyticsOverviewQuery,
  useGetIncidentTrendsQuery,
  useGetAlertsBySeverityQuery,
  useGetTopIncidentCategoriesQuery,
  useGetTeamPerformanceQuery,
  useGetTopPerformersQuery,
  useGetAIMetricsQuery,
  useGetPlaybookStatsQuery,
} from '../../../store/api/analyticsApi';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

const AnalyticsDashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const days = timeRange === '7d' ? 7 : timeRange === '90d' ? 90 : 30;

  // Fetch all analytics data
  const { data: overview, isLoading: loadingOverview } = useGetAnalyticsOverviewQuery(days);
  const { data: incidentTrends, isLoading: loadingTrends } = useGetIncidentTrendsQuery(6);
  const { data: alertsBySeverity, isLoading: loadingAlerts } = useGetAlertsBySeverityQuery(days);
  const { data: topCategories, isLoading: loadingCategories } = useGetTopIncidentCategoriesQuery({ limit: 5, days });
  const { data: teamPerformance, isLoading: loadingTeam } = useGetTeamPerformanceQuery(days);
  const { data: topPerformers, isLoading: loadingPerformers } = useGetTopPerformersQuery({ limit: 5, days });
  const { data: aiMetrics, isLoading: loadingAI } = useGetAIMetricsQuery(days);
  const { data: playbookStats, isLoading: loadingPlaybooks } = useGetPlaybookStatsQuery({ limit: 5, days });

  const responseTimeColumns: ColumnsType<any> = [
    { title: 'Team', dataIndex: 'team', key: 'team' },
    { title: 'Avg Response', dataIndex: 'avgResponse', key: 'avgResponse' },
    { title: 'Avg Resolution', dataIndex: 'avgResolution', key: 'avgResolution' },
    {
      title: 'SLA Compliance',
      dataIndex: 'slaCompliance',
      key: 'slaCompliance',
      render: (val: number) => (
        <Progress
          percent={val}
          size="small"
          status={val >= 90 ? 'success' : val >= 80 ? 'normal' : 'exception'}
          style={{ width: 120 }}
        />
      ),
    },
  ];

  const playbookColumns: ColumnsType<any> = [
    { title: 'Playbook', dataIndex: 'name', key: 'name' },
    { title: 'Executions', dataIndex: 'executions', key: 'executions' },
    {
      title: 'Success Rate',
      dataIndex: 'successRate',
      key: 'successRate',
      render: (val: number) => (
        <Tag color={val >= 98 ? 'green' : val >= 95 ? 'blue' : 'orange'}>{val}%</Tag>
      ),
    },
    { title: 'Avg Duration', dataIndex: 'avgDuration', key: 'avgDuration' },
  ];

  if (loadingOverview) {
    return <div style={{ textAlign: 'center', padding: '50px' }}><Spin size="large" /></div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Analytics Dashboard</Title>
        <Space>
          <Select value={timeRange} onChange={setTimeRange} style={{ width: 120 }}>
            <Select.Option value="7d">Last 7 days</Select.Option>
            <Select.Option value="30d">Last 30 days</Select.Option>
            <Select.Option value="90d">Last 90 days</Select.Option>
            <Select.Option value="custom">Custom</Select.Option>
          </Select>
          {timeRange === 'custom' && <RangePicker />}
        </Space>
      </div>

      {/* Key Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Incidents"
              value={overview?.total_incidents ?? 0}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Resolved"
              value={overview?.resolved ?? 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                {overview && overview.total_incidents > 0
                  ? `${((overview.resolved / overview.total_incidents) * 100).toFixed(1)}% resolution rate`
                  : 'N/A'}
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Avg Resolution Time"
              value={overview?.avg_resolution_time_minutes ?? 0}
              suffix="min"
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="SLA Compliance"
              value={overview?.sla_compliance_percentage ?? 0}
              suffix="%"
              prefix={<SafetyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Tabs defaultActiveKey="overview" items={[
        {
          key: 'overview',
          label: 'Overview',
          children: (
            <Row gutter={[16, 16]}>
              {/* Incident Trends */}
              <Col xs={24} lg={16}>
                <Card title="Incident Trends" loading={loadingTrends}>
                  {incidentTrends && incidentTrends.length > 0 && (
                    <>
                      <div style={{ display: 'flex', justifyContent: 'space-around', padding: '20px 0' }}>
                        {incidentTrends.map((item, index) => (
                          <div key={index} style={{ textAlign: 'center' }}>
                            <div style={{ marginBottom: 8 }}>
                              <div style={{
                                height: Math.max(item.created, item.resolved) * 2,
                                display: 'flex',
                                alignItems: 'flex-end',
                                justifyContent: 'center',
                                gap: 4,
                              }}>
                                <div style={{
                                  width: 20,
                                  height: item.created * 2,
                                  backgroundColor: '#1890ff',
                                  borderRadius: 4,
                                }} />
                                <div style={{
                                  width: 20,
                                  height: item.resolved * 2,
                                  backgroundColor: '#52c41a',
                                  borderRadius: 4,
                                }} />
                              </div>
                            </div>
                            <Text>{item.month}</Text>
                          </div>
                        ))}
                      </div>
                      <div style={{ textAlign: 'center', marginTop: 8 }}>
                        <Space>
                          <Tag color="blue">Created</Tag>
                          <Tag color="green">Resolved</Tag>
                        </Space>
                      </div>
                    </>
                  )}
                </Card>
              </Col>

              {/* Alerts by Severity */}
              <Col xs={24} lg={8}>
                <Card title="Alerts by Severity" loading={loadingAlerts}>
                  {alertsBySeverity && (
                    <List
                      dataSource={alertsBySeverity}
                      renderItem={(item) => (
                        <List.Item>
                          <div style={{ width: '100%' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                              <Text>{item.severity}</Text>
                              <Text strong>{item.count}</Text>
                            </div>
                            <Progress
                              percent={item.percentage}
                              showInfo={false}
                              strokeColor={
                                item.severity === 'Critical' ? '#ff4d4f' :
                                  item.severity === 'High' ? '#fa8c16' :
                                    item.severity === 'Medium' ? '#faad14' : '#1890ff'
                              }
                            />
                          </div>
                        </List.Item>
                      )}
                    />
                  )}
                </Card>
              </Col>

              {/* Top Incident Categories */}
              <Col xs={24} lg={12}>
                <Card title="Top Incident Categories" loading={loadingCategories}>
                  {topCategories && (
                    <List
                      dataSource={topCategories}
                      renderItem={(item) => (
                        <List.Item>
                          <List.Item.Meta
                            title={item.category}
                            description={`${item.count} incidents`}
                          />
                          <Space>
                            {item.trend < 0 ? (
                              <Tag color="green" icon={<ArrowDownOutlined />}>{Math.abs(item.trend)}%</Tag>
                            ) : item.trend > 0 ? (
                              <Tag color="red" icon={<ArrowUpOutlined />}>{item.trend}%</Tag>
                            ) : (
                              <Tag>No change</Tag>
                            )}
                          </Space>
                        </List.Item>
                      )}
                    />
                  )}
                </Card>
              </Col>

              {/* Response Time by Team */}
              <Col xs={24} lg={12}>
                <Card title="Response Time by Team" loading={loadingTeam}>
                  <Table
                    columns={responseTimeColumns}
                    dataSource={teamPerformance}
                    rowKey="team"
                    pagination={false}
                    size="small"
                  />
                </Card>
              </Col>
            </Row>
          ),
        },
        {
          key: 'ai',
          label: (
            <Space>
              <RobotOutlined />
              AI Analytics
            </Space>
          ),
          children: (
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={8}>
                <Card loading={loadingAI}>
                  <Statistic
                    title="Incidents Classified"
                    value={aiMetrics?.incidentsClassified ?? 0}
                    prefix={<RobotOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Card loading={loadingAI}>
                  <Statistic
                    title="Suggestions Accepted"
                    value={aiMetrics?.suggestionsAccepted ?? 0}
                    suffix={aiMetrics ? `/ ${aiMetrics.incidentsClassified}` : ''}
                    prefix={<CheckCircleOutlined />}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Card loading={loadingAI}>
                  <Statistic
                    title="AI Accuracy Rate"
                    value={aiMetrics?.accuracyRate ?? 0}
                    suffix="%"
                    precision={1}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Card loading={loadingAI}>
                  <Statistic
                    title="Predictions Made"
                    value={aiMetrics?.predictionsMade ?? 0}
                    prefix={<ThunderboltOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Card loading={loadingAI}>
                  <Statistic
                    title="Incidents Prevented"
                    value={aiMetrics?.preventedIncidents ?? 0}
                    prefix={<SafetyOutlined />}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Card loading={loadingAI}>
                  <Statistic
                    title="Time Saved"
                    value={aiMetrics?.timeSaved ?? '0 hours'}
                    prefix={<ClockCircleOutlined />}
                    valueStyle={{ color: '#722ed1' }}
                  />
                </Card>
              </Col>
              <Col xs={24}>
                <Card title="AI Performance Breakdown" loading={loadingAI}>
                  <Row gutter={[16, 16]}>
                    <Col xs={24} md={8}>
                      <div style={{ textAlign: 'center' }}>
                        <Progress type="circle" percent={94} format={() => '94%'} />
                        <div style={{ marginTop: 8 }}>
                          <Text strong>Classification Accuracy</Text>
                        </div>
                      </div>
                    </Col>
                    <Col xs={24} md={8}>
                      <div style={{ textAlign: 'center' }}>
                        <Progress type="circle" percent={87} format={() => '87%'} strokeColor="#52c41a" />
                        <div style={{ marginTop: 8 }}>
                          <Text strong>Prediction Accuracy</Text>
                        </div>
                      </div>
                    </Col>
                    <Col xs={24} md={8}>
                      <div style={{ textAlign: 'center' }}>
                        <Progress type="circle" percent={72} format={() => '72%'} strokeColor="#722ed1" />
                        <div style={{ marginTop: 8 }}>
                          <Text strong>Resolution Suggestion Rate</Text>
                        </div>
                      </div>
                    </Col>
                  </Row>
                </Card>
              </Col>
            </Row>
          ),
        },
        {
          key: 'automation',
          label: (
            <Space>
              <ThunderboltOutlined />
              Automation
            </Space>
          ),
          children: (
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={6}>
                <Card loading={loadingPlaybooks}>
                  <Statistic
                    title="Playbook Executions"
                    value={playbookStats?.reduce((sum, p) => sum + p.executions, 0) ?? 0}
                    prefix={<ThunderboltOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card loading={loadingPlaybooks}>
                  <Statistic
                    title="Success Rate"
                    value={playbookStats && playbookStats.length > 0
                      ? (playbookStats.reduce((sum, p) => sum + p.successRate, 0) / playbookStats.length).toFixed(1)
                      : 0}
                    suffix="%"
                    precision={1}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="Hours Saved"
                    value={85}
                    prefix={<ClockCircleOutlined />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card loading={loadingPlaybooks}>
                  <Statistic
                    title="Active Playbooks"
                    value={playbookStats?.length ?? 0}
                    prefix={<SafetyOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24}>
                <Card title="Top Playbooks by Execution" loading={loadingPlaybooks}>
                  <Table
                    columns={playbookColumns}
                    dataSource={playbookStats}
                    rowKey="name"
                    pagination={false}
                  />
                </Card>
              </Col>
            </Row>
          ),
        },
        {
          key: 'team',
          label: (
            <Space>
              <UserOutlined />
              Team Performance
            </Space>
          ),
          children: (
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={12}>
                <Card title="Top Performers This Month" loading={loadingPerformers}>
                  {topPerformers && (
                    <List
                      dataSource={topPerformers}
                      renderItem={(item, index) => (
                        <List.Item>
                          <List.Item.Meta
                            avatar={
                              <Avatar style={{ backgroundColor: index < 3 ? '#faad14' : '#1890ff' }}>
                                {index + 1}
                              </Avatar>
                            }
                            title={item.name}
                            description={`${item.resolved} incidents resolved • Avg: ${item.avgTime}`}
                          />
                          <Tag color="gold">{item.rating} / 5</Tag>
                        </List.Item>
                      )}
                    />
                  )}
                </Card>
              </Col>
              <Col xs={24} lg={12}>
                <Card title="Team Metrics" loading={loadingTeam}>
                  <Table
                    columns={responseTimeColumns}
                    dataSource={teamPerformance}
                    rowKey="team"
                    pagination={false}
                  />
                </Card>
              </Col>
            </Row>
          ),
        },
        {
          key: 'cloud',
          label: (
            <Space>
              <CloudOutlined />
              Cloud Metrics
            </Space>
          ),
          children: (
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="Cloud Resources"
                    value={156}
                    prefix={<CloudOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="Monthly Cost"
                    value={45680}
                    prefix="$"
                    precision={0}
                  />
                  <div style={{ marginTop: 8 }}>
                    <Text type="secondary">
                      <ArrowDownOutlined style={{ color: '#52c41a' }} /> 8% vs last month
                    </Text>
                  </div>
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="Cost Savings"
                    value={8450}
                    prefix="$"
                    precision={0}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="Optimization Score"
                    value={78}
                    suffix="%"
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              <Col xs={24}>
                <Card title="Cost by Service">
                  <div style={{ display: 'flex', justifyContent: 'space-around', padding: '20px 0' }}>
                    {[
                      { name: 'Compute', cost: 18500, pct: 40 },
                      { name: 'Storage', cost: 8200, pct: 18 },
                      { name: 'Database', cost: 9800, pct: 21 },
                      { name: 'Network', cost: 5400, pct: 12 },
                      { name: 'Other', cost: 3780, pct: 9 },
                    ].map((item) => (
                      <div key={item.name} style={{ textAlign: 'center' }}>
                        <Progress
                          type="circle"
                          percent={item.pct}
                          width={80}
                          format={() => `${(item.cost / 1000).toFixed(1)}k`}
                        />
                        <div style={{ marginTop: 8 }}>
                          <Text>{item.name}</Text>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </Col>
            </Row>
          ),
        },
      ]} />
    </div>
  );
};

export default AnalyticsDashboard;
