import React, { useState } from 'react';
import { Card, Table, Tag, Typography, Space, Progress, Statistic, Row, Col, Alert, Button, Modal, message, Popconfirm, Drawer, Timeline, Descriptions } from 'antd';
import { RobotOutlined, WarningOutlined, CheckCircleOutlined, ThunderboltOutlined, EyeOutlined, CloseOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text, Paragraph } = Typography;

interface Prediction {
  id: string;
  type: string;
  resource: string;
  prediction: string;
  likelihood: number;
  impact: 'critical' | 'high' | 'medium' | 'low';
  timeframe: string;
  status: 'active' | 'prevented' | 'occurred' | 'expired';
  recommendedAction: string;
  details?: string;
  preventionSteps?: string[];
}

const initialPredictions: Prediction[] = [
  {
    id: '1',
    type: 'Capacity',
    resource: 'prod-db-primary',
    prediction: 'Database storage will reach 90% capacity',
    likelihood: 0.87,
    impact: 'high',
    timeframe: '3-5 days',
    status: 'active',
    recommendedAction: 'Increase storage allocation or archive old data',
    details: 'Based on current growth rate of 2.5GB/day, the database will reach 90% capacity within 3-5 days. Current usage is at 78%.',
    preventionSteps: [
      'Archive data older than 90 days to cold storage',
      'Increase RDS storage from 500GB to 750GB',
      'Review and optimize large tables',
      'Set up storage usage alerts at 80% and 85%',
    ],
  },
  {
    id: '2',
    type: 'Performance',
    resource: 'api-gateway',
    prediction: 'API latency will exceed SLA threshold during peak hours',
    likelihood: 0.72,
    impact: 'medium',
    timeframe: '1-2 days',
    status: 'active',
    recommendedAction: 'Scale up API instances before peak period',
    details: 'Historical traffic patterns show a 40% increase in requests during the upcoming promotion. Current capacity may not handle the load.',
    preventionSteps: [
      'Pre-scale API instances from 3 to 5',
      'Enable auto-scaling with aggressive thresholds',
      'Warm up the cache before peak period',
      'Set up latency alerts at 500ms P95',
    ],
  },
  {
    id: '3',
    type: 'Failure',
    resource: 'cache-cluster-node-3',
    prediction: 'Memory exhaustion risk based on current growth pattern',
    likelihood: 0.65,
    impact: 'high',
    timeframe: '7-10 days',
    status: 'active',
    recommendedAction: 'Review cache eviction policy and memory allocation',
    details: 'Node memory usage has been growing at 1% per day. At current rate, it will reach critical levels in 7-10 days.',
    preventionSteps: [
      'Review cache TTL settings',
      'Implement LRU eviction policy',
      'Add another cache node to distribute load',
      'Monitor memory usage trends',
    ],
  },
  {
    id: '4',
    type: 'Security',
    resource: 'SSL Certificate',
    prediction: 'Certificate for app.example.com will expire',
    likelihood: 1.0,
    impact: 'critical',
    timeframe: '14 days',
    status: 'active',
    recommendedAction: 'Renew SSL certificate before expiration',
    details: 'The SSL certificate for app.example.com expires on January 5, 2025. Certificate must be renewed and deployed before this date.',
    preventionSteps: [
      'Request new certificate from Let\'s Encrypt',
      'Deploy new certificate to load balancer',
      'Verify certificate chain is complete',
      'Set up automated certificate renewal',
    ],
  },
  {
    id: '5',
    type: 'Capacity',
    resource: 'prod-logs-bucket',
    prediction: 'Log storage exceeded threshold',
    likelihood: 0.95,
    impact: 'medium',
    timeframe: 'Occurred',
    status: 'prevented',
    recommendedAction: 'Implemented log rotation policy',
    details: 'AI predicted storage issue 5 days ago. Log rotation was implemented, preventing the issue.',
  },
  {
    id: '6',
    type: 'Performance',
    resource: 'worker-queue',
    prediction: 'Queue backlog predicted to cause delays',
    likelihood: 0.78,
    impact: 'medium',
    timeframe: 'Expired',
    status: 'expired',
    recommendedAction: 'Prediction window passed without occurrence',
    details: 'The predicted backlog did not occur. Queue processing remained within normal parameters.',
  },
];

const impactColors: Record<string, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'gold',
  low: 'blue',
};

const statusColors: Record<string, string> = {
  active: 'blue',
  prevented: 'green',
  occurred: 'red',
  expired: 'default',
};

const PredictionsPage: React.FC = () => {
  const [predictions, setPredictions] = useState<Prediction[]>(initialPredictions);
  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const activePredictions = predictions.filter(p => p.status === 'active');
  const preventedCount = predictions.filter(p => p.status === 'prevented').length;
  const avgLikelihood = activePredictions.length > 0
    ? activePredictions.reduce((sum, p) => sum + p.likelihood, 0) / activePredictions.length
    : 0;

  const handleTakeAction = (prediction: Prediction) => {
    setActionLoading(prediction.id);
    message.loading(`Applying preventive measures for ${prediction.type}...`, 2);

    setTimeout(() => {
      setPredictions(predictions.map(p =>
        p.id === prediction.id ? { ...p, status: 'prevented' } : p
      ));
      setActionLoading(null);
      message.success(`Preventive action completed! ${prediction.type} issue has been addressed.`);
    }, 2500);
  };

  const handleDismiss = (prediction: Prediction) => {
    setPredictions(predictions.map(p =>
      p.id === prediction.id ? { ...p, status: 'expired' } : p
    ));
    message.info(`Prediction dismissed: ${prediction.type}`);
  };

  const handleViewDetails = (prediction: Prediction) => {
    setSelectedPrediction(prediction);
    setIsDetailDrawerOpen(true);
  };

  const columns: ColumnsType<Prediction> = [
    {
      title: 'Prediction',
      dataIndex: 'prediction',
      key: 'prediction',
      render: (text, record) => (
        <div>
          <Space style={{ marginBottom: 4 }}>
            <Tag color="purple">{record.type}</Tag>
            <Text code>{record.resource}</Text>
          </Space>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
            <ThunderboltOutlined /> {record.recommendedAction}
          </div>
        </div>
      ),
    },
    {
      title: 'Likelihood',
      dataIndex: 'likelihood',
      key: 'likelihood',
      width: 140,
      render: (likelihood) => (
        <Space direction="vertical" size={0}>
          <Progress
            percent={Math.round(likelihood * 100)}
            size="small"
            status={likelihood >= 0.8 ? 'exception' : 'normal'}
            style={{ width: 100 }}
          />
          <Text type="secondary" style={{ fontSize: 11 }}>AI Confidence</Text>
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
      title: 'Timeframe',
      dataIndex: 'timeframe',
      key: 'timeframe',
      width: 120,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => (
        <Tag
          color={statusColors[status]}
          icon={status === 'prevented' ? <CheckCircleOutlined /> : status === 'active' ? <WarningOutlined /> : null}
        >
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetails(record)}
            title="View Details"
          />
          {record.status === 'active' && (
            <>
              <Popconfirm
                title="Take Preventive Action"
                description="Apply the recommended action to prevent this issue?"
                onConfirm={() => handleTakeAction(record)}
                okText="Apply"
                cancelText="Cancel"
              >
                <Button
                  type="primary"
                  size="small"
                  loading={actionLoading === record.id}
                >
                  Take Action
                </Button>
              </Popconfirm>
              <Popconfirm
                title="Dismiss Prediction"
                description="Are you sure you want to dismiss this prediction?"
                onConfirm={() => handleDismiss(record)}
                okText="Dismiss"
                cancelText="Cancel"
              >
                <Button size="small" icon={<CloseOutlined />}>Dismiss</Button>
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>AI Predictions</Title>

      <Alert
        message="Predictive Analytics"
        description="Our AI analyzes patterns in your infrastructure and operations to predict potential issues before they occur. Taking action on these predictions can prevent incidents."
        type="info"
        icon={<RobotOutlined />}
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Active Predictions"
              value={activePredictions.length}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Issues Prevented"
              value={preventedCount}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Avg. AI Confidence"
              value={Math.round(avgLikelihood * 100)}
              suffix="%"
              prefix={<RobotOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Predicted Issues">
        <Table
          columns={columns}
          dataSource={predictions}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Detail Drawer */}
      <Drawer
        title={`Prediction Details: ${selectedPrediction?.type}`}
        open={isDetailDrawerOpen}
        onClose={() => { setIsDetailDrawerOpen(false); setSelectedPrediction(null); }}
        width={600}
        extra={
          selectedPrediction?.status === 'active' && (
            <Button type="primary" onClick={() => { handleTakeAction(selectedPrediction); setIsDetailDrawerOpen(false); }}>
              Take Action
            </Button>
          )
        }
      >
        {selectedPrediction && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Descriptions bordered column={1}>
              <Descriptions.Item label="Prediction">{selectedPrediction.prediction}</Descriptions.Item>
              <Descriptions.Item label="Resource"><Text code>{selectedPrediction.resource}</Text></Descriptions.Item>
              <Descriptions.Item label="Type"><Tag color="purple">{selectedPrediction.type}</Tag></Descriptions.Item>
              <Descriptions.Item label="Impact">
                <Tag color={impactColors[selectedPrediction.impact]}>{selectedPrediction.impact.toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={statusColors[selectedPrediction.status]}>{selectedPrediction.status.toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Timeframe">{selectedPrediction.timeframe}</Descriptions.Item>
              <Descriptions.Item label="AI Confidence">
                <Progress percent={Math.round(selectedPrediction.likelihood * 100)} style={{ width: 200 }} />
              </Descriptions.Item>
            </Descriptions>

            {selectedPrediction.details && (
              <Card title="Analysis Details" size="small">
                <Paragraph>{selectedPrediction.details}</Paragraph>
              </Card>
            )}

            <Card title="Recommended Action" size="small">
              <Alert
                message={selectedPrediction.recommendedAction}
                type="warning"
                icon={<ThunderboltOutlined />}
                showIcon
              />
            </Card>

            {selectedPrediction.preventionSteps && (
              <Card title="Prevention Steps" size="small">
                <Timeline
                  items={selectedPrediction.preventionSteps.map((step, i) => ({
                    color: 'blue',
                    children: (
                      <div>
                        <Text strong>Step {i + 1}</Text>
                        <div>{step}</div>
                      </div>
                    ),
                  }))}
                />
              </Card>
            )}
          </Space>
        )}
      </Drawer>
    </div>
  );
};

export default PredictionsPage;
