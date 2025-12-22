import React, { useState } from 'react';
import { Card, Row, Col, Typography, Statistic, Space, Select, DatePicker, Table, Progress, Tag, Tabs, List, Avatar } from 'antd';
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

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

// Mock data for analytics
const incidentTrends = [
  { month: 'Jul', created: 45, resolved: 42 },
  { month: 'Aug', created: 52, resolved: 48 },
  { month: 'Sep', created: 38, resolved: 40 },
  { month: 'Oct', created: 65, resolved: 58 },
  { month: 'Nov', created: 48, resolved: 52 },
  { month: 'Dec', created: 35, resolved: 38 },
];

const alertsBySeverity = [
  { severity: 'Critical', count: 12, percentage: 8 },
  { severity: 'High', count: 45, percentage: 30 },
  { severity: 'Medium', count: 68, percentage: 45 },
  { severity: 'Low', count: 25, percentage: 17 },
];

const topIncidentCategories = [
  { category: 'Infrastructure', count: 85, trend: -12 },
  { category: 'Application', count: 72, trend: 8 },
  { category: 'Security', count: 45, trend: -5 },
  { category: 'Network', count: 38, trend: 15 },
  { category: 'Database', count: 30, trend: -3 },
];

const responseTimeData = [
  { team: 'Infrastructure', avgResponse: '8 min', avgResolution: '45 min', slaCompliance: 95 },
  { team: 'Application', avgResponse: '12 min', avgResolution: '1.2 hr', slaCompliance: 88 },
  { team: 'Security', avgResponse: '5 min', avgResolution: '2.5 hr', slaCompliance: 92 },
  { team: 'Network', avgResponse: '15 min', avgResolution: '35 min', slaCompliance: 85 },
];

const topPerformers = [
  { name: 'Alex Chen', resolved: 45, avgTime: '28 min', rating: 4.9 },
  { name: 'Sarah Johnson', resolved: 42, avgTime: '32 min', rating: 4.8 },
  { name: 'Mike Wilson', resolved: 38, avgTime: '25 min', rating: 4.7 },
  { name: 'Emily Davis', resolved: 35, avgTime: '35 min', rating: 4.6 },
  { name: 'John Smith', resolved: 30, avgTime: '40 min', rating: 4.5 },
];

const aiMetrics = {
  incidentsClassified: 156,
  suggestionsAccepted: 89,
  predictionsMade: 45,
  preventedIncidents: 12,
  accuracyRate: 94.5,
  timeSaved: '120 hours',
};

const playbookStats = [
  { name: 'Auto-Scale Cluster', executions: 45, successRate: 98, avgDuration: '2.5 min' },
  { name: 'Restart Service', executions: 38, successRate: 100, avgDuration: '1.2 min' },
  { name: 'Clear Cache', executions: 32, successRate: 97, avgDuration: '45 sec' },
  { name: 'Database Backup', executions: 28, successRate: 95, avgDuration: '8 min' },
  { name: 'SSL Renewal', executions: 15, successRate: 100, avgDuration: '3 min' },
];

const AnalyticsDashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState('30d');

  const responseTimeColumns: ColumnsType<typeof responseTimeData[0]> = [
    { title: 'Team', dataIndex: 'team', key: 'team' },
    { title: 'Avg Response', dataIndex: 'avgResponse', key: 'avgResponse' },
    { title: 'Avg Resolution', dataIndex: 'avgResolution', key: 'avgResolution' },
    {
      title: 'SLA Compliance',
      dataIndex: 'slaCompliance',
      key: 'slaCompliance',
      render: (val) => (
        <Progress
          percent={val}
          size="small"
          status={val >= 90 ? 'success' : val >= 80 ? 'normal' : 'exception'}
          style={{ width: 120 }}
        />
      ),
    },
  ];

  const playbookColumns: ColumnsType<typeof playbookStats[0]> = [
    { title: 'Playbook', dataIndex: 'name', key: 'name' },
    { title: 'Executions', dataIndex: 'executions', key: 'executions' },
    {
      title: 'Success Rate',
      dataIndex: 'successRate',
      key: 'successRate',
      render: (val) => (
        <Tag color={val >= 98 ? 'green' : val >= 95 ? 'blue' : 'orange'}>{val}%</Tag>
      ),
    },
    { title: 'Avg Duration', dataIndex: 'avgDuration', key: 'avgDuration' },
  ];

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
              value={283}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                <ArrowDownOutlined style={{ color: '#52c41a' }} /> 12% vs last period
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Resolved"
              value={278}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">98.2% resolution rate</Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Avg Resolution Time"
              value="45"
              suffix="min"
              prefix={<ClockCircleOutlined />}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                <ArrowDownOutlined style={{ color: '#52c41a' }} /> 18% improvement
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="SLA Compliance"
              value={92.5}
              suffix="%"
              prefix={<SafetyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ marginTop: 8 }}>
              <Text type="secondary">
                <ArrowUpOutlined style={{ color: '#52c41a' }} /> 3% vs last period
              </Text>
            </div>
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
                <Card title="Incident Trends">
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
                </Card>
              </Col>

              {/* Alerts by Severity */}
              <Col xs={24} lg={8}>
                <Card title="Alerts by Severity">
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
                </Card>
              </Col>

              {/* Top Incident Categories */}
              <Col xs={24} lg={12}>
                <Card title="Top Incident Categories">
                  <List
                    dataSource={topIncidentCategories}
                    renderItem={(item) => (
                      <List.Item>
                        <List.Item.Meta
                          title={item.category}
                          description={`${item.count} incidents`}
                        />
                        <Space>
                          {item.trend < 0 ? (
                            <Tag color="green" icon={<ArrowDownOutlined />}>{Math.abs(item.trend)}%</Tag>
                          ) : (
                            <Tag color="red" icon={<ArrowUpOutlined />}>{item.trend}%</Tag>
                          )}
                        </Space>
                      </List.Item>
                    )}
                  />
                </Card>
              </Col>

              {/* Response Time by Team */}
              <Col xs={24} lg={12}>
                <Card title="Response Time by Team">
                  <Table
                    columns={responseTimeColumns}
                    dataSource={responseTimeData}
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
                <Card>
                  <Statistic
                    title="Incidents Classified"
                    value={aiMetrics.incidentsClassified}
                    prefix={<RobotOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Card>
                  <Statistic
                    title="Suggestions Accepted"
                    value={aiMetrics.suggestionsAccepted}
                    suffix={`/ ${aiMetrics.incidentsClassified}`}
                    prefix={<CheckCircleOutlined />}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Card>
                  <Statistic
                    title="AI Accuracy Rate"
                    value={aiMetrics.accuracyRate}
                    suffix="%"
                    precision={1}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Card>
                  <Statistic
                    title="Predictions Made"
                    value={aiMetrics.predictionsMade}
                    prefix={<ThunderboltOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Card>
                  <Statistic
                    title="Incidents Prevented"
                    value={aiMetrics.preventedIncidents}
                    prefix={<SafetyOutlined />}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={8}>
                <Card>
                  <Statistic
                    title="Time Saved"
                    value={aiMetrics.timeSaved}
                    prefix={<ClockCircleOutlined />}
                    valueStyle={{ color: '#722ed1' }}
                  />
                </Card>
              </Col>
              <Col xs={24}>
                <Card title="AI Performance Breakdown">
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
                <Card>
                  <Statistic
                    title="Playbook Executions"
                    value={158}
                    prefix={<ThunderboltOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Card>
                  <Statistic
                    title="Success Rate"
                    value={97.5}
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
                <Card>
                  <Statistic
                    title="Active Playbooks"
                    value={12}
                    prefix={<SafetyOutlined />}
                  />
                </Card>
              </Col>
              <Col xs={24}>
                <Card title="Top Playbooks by Execution">
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
                <Card title="Top Performers This Month">
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
                </Card>
              </Col>
              <Col xs={24} lg={12}>
                <Card title="Team Metrics">
                  <Table
                    columns={responseTimeColumns}
                    dataSource={responseTimeData}
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
                          format={() => `$${(item.cost / 1000).toFixed(1)}k`}
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
