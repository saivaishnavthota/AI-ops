import React, { useState } from 'react';
import { Card, Table, Typography, Tag, Button, Space, Alert, Progress, Statistic, Row, Col, Modal, message, Popconfirm } from 'antd';
import { CheckOutlined, DollarOutlined, RobotOutlined, CloseOutlined, InfoCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text, Paragraph } = Typography;

interface Recommendation {
  id: string;
  type: string;
  resource: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  savings: number;
  effort: string;
  status: 'pending' | 'applied' | 'dismissed';
  aiConfidence: number;
  steps?: string[];
}

const initialRecommendations: Recommendation[] = [
  {
    id: '1',
    type: 'Right-sizing',
    resource: 'prod-api-server-2',
    description: 'Instance is consistently underutilized (avg CPU 15%). Consider downsizing from m5.xlarge to m5.large.',
    impact: 'high',
    savings: 52.50,
    effort: 'Low',
    status: 'pending',
    aiConfidence: 0.92,
    steps: [
      'Create a snapshot of the current instance',
      'Launch a new m5.large instance with the same configuration',
      'Migrate traffic to the new instance',
      'Verify application performance',
      'Terminate the old m5.xlarge instance',
    ],
  },
  {
    id: '2',
    type: 'Reserved Instance',
    resource: 'prod-db-primary',
    description: 'This instance has been running continuously for 6 months. Reserved Instance would save 40%.',
    impact: 'high',
    savings: 180.00,
    effort: 'Low',
    status: 'pending',
    aiConfidence: 0.95,
    steps: [
      'Review current RDS instance usage patterns',
      'Calculate 1-year vs 3-year reserved instance pricing',
      'Purchase reserved instance through AWS Console',
      'Savings will be applied automatically',
    ],
  },
  {
    id: '3',
    type: 'Unused Resource',
    resource: 'staging-api-server',
    description: 'Instance has been stopped for 30+ days. Consider terminating or archiving.',
    impact: 'low',
    savings: 15.00,
    effort: 'Low',
    status: 'pending',
    aiConfidence: 0.88,
    steps: [
      'Confirm instance is no longer needed',
      'Create AMI backup if preservation is required',
      'Terminate the stopped instance',
      'Delete associated EBS volumes',
    ],
  },
  {
    id: '4',
    type: 'Storage Optimization',
    resource: 'prod-logs-bucket',
    description: 'Move infrequently accessed logs (>90 days) to S3 Glacier for 80% cost reduction.',
    impact: 'medium',
    savings: 85.00,
    effort: 'Medium',
    status: 'applied',
    aiConfidence: 0.91,
  },
  {
    id: '5',
    type: 'Network Optimization',
    resource: 'NAT Gateway',
    description: 'High data transfer costs detected. Consider VPC endpoints for S3 and DynamoDB.',
    impact: 'medium',
    savings: 120.00,
    effort: 'Medium',
    status: 'pending',
    aiConfidence: 0.85,
    steps: [
      'Create VPC endpoint for S3',
      'Create VPC endpoint for DynamoDB',
      'Update route tables to use VPC endpoints',
      'Monitor NAT Gateway data transfer reduction',
    ],
  },
];

const impactColors: Record<string, string> = {
  high: 'red',
  medium: 'orange',
  low: 'blue',
};

const statusColors: Record<string, string> = {
  pending: 'gold',
  applied: 'green',
  dismissed: 'default',
};

const CloudOptimizationPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>(initialRecommendations);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);
  const [applyingId, setApplyingId] = useState<string | null>(null);

  const pendingRecommendations = recommendations.filter(r => r.status === 'pending');
  const totalSavings = pendingRecommendations.reduce((sum, r) => sum + r.savings, 0);
  const appliedSavings = recommendations.filter(r => r.status === 'applied').reduce((sum, r) => sum + r.savings, 0);

  const handleApply = (recommendation: Recommendation) => {
    setApplyingId(recommendation.id);
    message.loading(`Applying optimization: ${recommendation.type}...`, 2);

    setTimeout(() => {
      setRecommendations(recommendations.map(r =>
        r.id === recommendation.id ? { ...r, status: 'applied' } : r
      ));
      setApplyingId(null);
      message.success(`${recommendation.type} optimization applied successfully! Saving $${recommendation.savings}/mo`);
    }, 2000);
  };

  const handleDismiss = (recommendation: Recommendation) => {
    setRecommendations(recommendations.map(r =>
      r.id === recommendation.id ? { ...r, status: 'dismissed' } : r
    ));
    message.info(`Recommendation dismissed: ${recommendation.type}`);
  };

  const handleViewDetails = (recommendation: Recommendation) => {
    setSelectedRecommendation(recommendation);
    setIsDetailModalOpen(true);
  };

  const columns: ColumnsType<Recommendation> = [
    {
      title: 'Recommendation',
      dataIndex: 'description',
      key: 'description',
      render: (text, record) => (
        <div>
          <Space style={{ marginBottom: 4 }}>
            <Tag color="blue">{record.type}</Tag>
            <Text code>{record.resource}</Text>
          </Space>
          <div style={{ fontSize: 13 }}>{text}</div>
        </div>
      ),
    },
    {
      title: 'AI Confidence',
      dataIndex: 'aiConfidence',
      key: 'aiConfidence',
      width: 120,
      render: (confidence) => (
        <Space>
          <RobotOutlined />
          <Progress percent={Math.round(confidence * 100)} size="small" style={{ width: 60 }} />
        </Space>
      ),
    },
    {
      title: 'Impact',
      dataIndex: 'impact',
      key: 'impact',
      width: 100,
      render: (impact) => (
        <Tag color={impactColors[impact]}>{impact.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Monthly Savings',
      dataIndex: 'savings',
      key: 'savings',
      width: 120,
      render: (savings) => (
        <Text strong style={{ color: '#52c41a' }}>${savings.toFixed(2)}/mo</Text>
      ),
    },
    {
      title: 'Effort',
      dataIndex: 'effort',
      key: 'effort',
      width: 80,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={statusColors[status]}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (_, record) => record.status === 'pending' && (
        <Space>
          <Button
            type="text"
            icon={<InfoCircleOutlined />}
            onClick={() => handleViewDetails(record)}
            title="View Details"
          />
          <Popconfirm
            title="Apply Optimization"
            description={`Apply this optimization to save $${record.savings}/mo?`}
            onConfirm={() => handleApply(record)}
            okText="Apply"
            cancelText="Cancel"
          >
            <Button
              type="primary"
              size="small"
              icon={<CheckOutlined />}
              loading={applyingId === record.id}
            >
              Apply
            </Button>
          </Popconfirm>
          <Popconfirm
            title="Dismiss Recommendation"
            description="Are you sure you want to dismiss this recommendation?"
            onConfirm={() => handleDismiss(record)}
            okText="Dismiss"
            cancelText="Cancel"
          >
            <Button size="small" icon={<CloseOutlined />}>Dismiss</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>Cost Optimization</Title>

      <Alert
        message="AI-Powered Recommendations"
        description="Our AI has analyzed your cloud usage patterns and identified optimization opportunities. These recommendations are updated daily."
        type="info"
        icon={<RobotOutlined />}
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Potential Monthly Savings"
              value={totalSavings}
              precision={2}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Realized Savings"
              value={appliedSavings}
              precision={2}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Pending Recommendations"
              value={pendingRecommendations.length}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Optimization Recommendations">
        <Table
          columns={columns}
          dataSource={recommendations}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Detail Modal */}
      <Modal
        title={`Optimization Details: ${selectedRecommendation?.type}`}
        open={isDetailModalOpen}
        onCancel={() => { setIsDetailModalOpen(false); setSelectedRecommendation(null); }}
        footer={
          selectedRecommendation?.status === 'pending' ? [
            <Button key="dismiss" onClick={() => { handleDismiss(selectedRecommendation!); setIsDetailModalOpen(false); }}>
              Dismiss
            </Button>,
            <Button key="apply" type="primary" onClick={() => { handleApply(selectedRecommendation!); setIsDetailModalOpen(false); }}>
              Apply Optimization
            </Button>,
          ] : [
            <Button key="close" onClick={() => setIsDetailModalOpen(false)}>Close</Button>
          ]
        }
        width={600}
      >
        {selectedRecommendation && (
          <>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Text type="secondary">Resource</Text>
                <Paragraph><Text code>{selectedRecommendation.resource}</Text></Paragraph>
              </div>
              <div>
                <Text type="secondary">Description</Text>
                <Paragraph>{selectedRecommendation.description}</Paragraph>
              </div>
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title="Monthly Savings"
                    value={selectedRecommendation.savings}
                    prefix="$"
                    precision={2}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic title="Effort" value={selectedRecommendation.effort} />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="AI Confidence"
                    value={Math.round(selectedRecommendation.aiConfidence * 100)}
                    suffix="%"
                  />
                </Col>
              </Row>
              {selectedRecommendation.steps && (
                <div>
                  <Text type="secondary">Implementation Steps</Text>
                  <ol style={{ paddingLeft: 20, marginTop: 8 }}>
                    {selectedRecommendation.steps.map((step, i) => (
                      <li key={i} style={{ marginBottom: 8 }}>{step}</li>
                    ))}
                  </ol>
                </div>
              )}
            </Space>
          </>
        )}
      </Modal>
    </div>
  );
};

export default CloudOptimizationPage;
