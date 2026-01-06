import React, { useState } from 'react';
import { Card, Table, Typography, Tag, Button, Space, Alert, Progress, Statistic, Row, Col, Modal, message, Popconfirm, Spin } from 'antd';
import { CheckOutlined, DollarOutlined, RobotOutlined, CloseOutlined, InfoCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useListOptimizationRecommendationsQuery,
  useApplyOptimizationRecommendationMutation,
  useDismissOptimizationRecommendationMutation,
  type OptimizationRecommendation,
} from '../../../store/api/cloudApi';

const { Title, Text, Paragraph } = Typography;

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
  const { data: recommendations, isLoading, refetch } = useListOptimizationRecommendationsQuery();
  const [applyRecommendation] = useApplyOptimizationRecommendationMutation();
  const [dismissRecommendation] = useDismissOptimizationRecommendationMutation();

  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [selectedRecommendation, setSelectedRecommendation] = useState<OptimizationRecommendation | null>(null);
  const [applyingId, setApplyingId] = useState<string | null>(null);

  const pendingRecommendations = recommendations?.filter(r => r.status === 'pending') || [];
  const totalSavings = pendingRecommendations.reduce((sum, r) => sum + r.savings, 0);
  const appliedSavings = recommendations?.filter(r => r.status === 'applied').reduce((sum, r) => sum + r.savings, 0) || 0;

  const handleApply = async (recommendation: OptimizationRecommendation) => {
    setApplyingId(recommendation.id);
    try {
      const result = await applyRecommendation(recommendation.id).unwrap();
      message.success(`${recommendation.type} optimization applied successfully! Saving $${result.savings}/mo`);
      refetch();
    } catch (error) {
      message.error('Failed to apply optimization');
    } finally {
      setApplyingId(null);
    }
  };

  const handleDismiss = async (recommendation: OptimizationRecommendation) => {
    try {
      await dismissRecommendation(recommendation.id).unwrap();
      message.info(`Recommendation dismissed: ${recommendation.type}`);
      refetch();
    } catch (error) {
      message.error('Failed to dismiss recommendation');
    }
  };

  const handleViewDetails = (recommendation: OptimizationRecommendation) => {
    setSelectedRecommendation(recommendation);
    setIsDetailModalOpen(true);
  };

  const columns: ColumnsType<OptimizationRecommendation> = [
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

  if (isLoading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}><Spin size="large" /></div>;
  }

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
