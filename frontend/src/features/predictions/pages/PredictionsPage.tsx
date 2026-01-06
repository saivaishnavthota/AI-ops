import React, { useState } from 'react';
import { Card, Table, Tag, Typography, Space, Progress, Statistic, Row, Col, Alert, Button, Popconfirm, Drawer, Timeline, Descriptions } from 'antd';
import { RobotOutlined, WarningOutlined, CheckCircleOutlined, ThunderboltOutlined, EyeOutlined, CloseOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useGetPredictionsQuery,
  useGetPredictionStatsQuery,
  useTakeActionOnPredictionMutation,
  useDismissPredictionMutation,
  Prediction,
} from '../../../store/api/predictionsApi';
import { message } from 'antd';

const { Title, Text, Paragraph } = Typography;

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
  const { data: predictionsData, isLoading } = useGetPredictionsQuery({ skip: 0, limit: 100 });
  const { data: stats } = useGetPredictionStatsQuery();
  const [takeAction] = useTakeActionOnPredictionMutation();
  const [dismissPrediction] = useDismissPredictionMutation();

  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const predictions = predictionsData?.items || [];

  const handleTakeAction = async (prediction: Prediction) => {
    setActionLoading(prediction.id);
    message.loading(`Applying preventive measures for ${prediction.type}...`, 2);

    try {
      await takeAction({
        id: prediction.id,
        data: { action_taken: prediction.recommended_action },
      }).unwrap();
      message.success(`Preventive action completed! ${prediction.type} issue has been addressed.`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to take action');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDismiss = async (prediction: Prediction) => {
    try {
      await dismissPrediction(prediction.id).unwrap();
      message.info(`Prediction dismissed: ${prediction.type}`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to dismiss prediction');
    }
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
      render: (text: string, record: Prediction) => (
        <div>
          <Space style={{ marginBottom: 4 }}>
            <Tag color="purple">{record.type}</Tag>
            <Text code>{record.resource}</Text>
          </Space>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
            <ThunderboltOutlined /> {record.recommended_action}
          </div>
        </div>
      ),
    },
    {
      title: 'Likelihood',
      dataIndex: 'likelihood',
      key: 'likelihood',
      width: 140,
      render: (likelihood: number) => (
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
      render: (impact: string) => (
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
      render: (status: string) => (
        <Tag
          color={statusColors[status]}
          icon={status === 'prevented' ? <CheckCircleOutlined /> : status === 'active' ? <WarningOutlined /> : undefined}
        >
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (_: any, record: Prediction) => (
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
              value={stats?.active_predictions || 0}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Issues Prevented"
              value={stats?.prevented_count || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Avg. AI Confidence"
              value={Math.round((stats?.avg_likelihood || 0) * 100)}
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
          loading={isLoading}
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
                message={selectedPrediction.recommended_action}
                type="warning"
                icon={<ThunderboltOutlined />}
                showIcon
              />
            </Card>

            {selectedPrediction.prevention_steps && selectedPrediction.prevention_steps.length > 0 && (
              <Card title="Prevention Steps" size="small">
                <Timeline
                  items={selectedPrediction.prevention_steps.map((step: string, i: number) => ({
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
