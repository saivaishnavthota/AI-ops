import React from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Spin,
  Typography,
  Timeline,
  Divider,
  Avatar,
  Input,
  List,
  Empty,
  message,
  Collapse,
  Progress,
  Alert,
  Tooltip,
} from 'antd';
import {
  ArrowLeftOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  MessageOutlined,
  RobotOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';

import {
  useGetIncidentQuery,
  useAcknowledgeIncidentMutation,
  useResolveIncidentMutation,
  useAddIncidentCommentMutation,
} from '../../../store/api/incidentsApi';
import {
  useAnalyzeIncidentMutation,
  useClassifyIncidentMutation,
  useSuggestResolutionMutation,
  useGetAIStatusQuery,
} from '../../../store/api/aiApi';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Panel } = Collapse;

const statusColors: Record<string, string> = {
  open: 'orange',
  acknowledged: 'blue',
  in_progress: 'purple',
  resolved: 'green',
  closed: 'default',
};

const priorityColors: Record<string, string> = {
  p1: 'red',
  p2: 'orange',
  p3: 'gold',
  p4: 'blue',
  p5: 'default',
};

const severityColors: Record<string, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'gold',
  low: 'blue',
  info: 'default',
};

const riskColors: Record<string, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'gold',
  low: 'green',
};

const IncidentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [commentText, setCommentText] = React.useState('');

  const { data: incident, isLoading, error, refetch } = useGetIncidentQuery(id!);
  const { data: aiStatus } = useGetAIStatusQuery();
  const [acknowledge, { isLoading: acknowledging }] = useAcknowledgeIncidentMutation();
  const [resolve, { isLoading: resolving }] = useResolveIncidentMutation();
  const [addComment, { isLoading: addingComment }] = useAddIncidentCommentMutation();

  // AI mutations
  const [analyzeIncident, { isLoading: analyzing }] = useAnalyzeIncidentMutation();
  const [classifyIncident, { isLoading: classifying }] = useClassifyIncidentMutation();
  const [suggestResolution, { isLoading: suggesting }] = useSuggestResolutionMutation();

  const handleAcknowledge = async () => {
    try {
      await acknowledge(id!).unwrap();
      message.success('Incident acknowledged');
    } catch {
      message.error('Failed to acknowledge incident');
    }
  };

  const handleResolve = async () => {
    try {
      await resolve({ id: id!, data: { resolution_notes: 'Issue resolved' } }).unwrap();
      message.success('Incident resolved');
    } catch {
      message.error('Failed to resolve incident');
    }
  };

  const handleAddComment = async () => {
    if (!commentText.trim()) return;

    try {
      await addComment({
        id: id!,
        data: { content: commentText, is_internal: false },
      }).unwrap();
      setCommentText('');
      message.success('Comment added');
    } catch {
      message.error('Failed to add comment');
    }
  };

  const handleAnalyze = async () => {
    try {
      const result = await analyzeIncident({ incidentId: id!, updateIncident: true }).unwrap();
      message.success(`AI analysis complete (${Math.round(result.classification.confidence * 100)}% confidence)`);
      refetch();
    } catch {
      message.error('AI analysis failed');
    }
  };

  const handleClassify = async () => {
    try {
      const result = await classifyIncident({ incidentId: id!, updateIncident: true }).unwrap();
      message.success(`Classified as ${result.classification.category} (${Math.round(result.classification.confidence * 100)}% confidence)`);
      refetch();
    } catch {
      message.error('Classification failed');
    }
  };

  const handleSuggest = async () => {
    try {
      await suggestResolution({ incidentId: id!, updateIncident: true }).unwrap();
      message.success('Resolution suggestions generated');
      refetch();
    } catch {
      message.error('Failed to generate suggestions');
    }
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error || !incident) {
    return (
      <Empty description="Incident not found">
        <Link to="/incidents">
          <Button type="primary">Back to Incidents</Button>
        </Link>
      </Empty>
    );
  }

  const aiClassification = incident.ai_classification as {
    category?: string;
    subcategory?: string;
    confidence?: number;
    reasoning?: string;
    keywords?: string[];
    affected_components?: string[];
    suggested_priority?: string;
    suggested_severity?: string;
  } | null;

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Link to="/incidents">
          <Button type="text" icon={<ArrowLeftOutlined />}>
            Back to Incidents
          </Button>
        </Link>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <Space>
            <Title level={3} style={{ margin: 0 }}>{incident.incident_number}</Title>
            <Tag color={statusColors[incident.status]}>
              {incident.status.replace('_', ' ').toUpperCase()}
            </Tag>
          </Space>
          <Title level={4} style={{ margin: '8px 0 0 0', fontWeight: 400 }}>{incident.title}</Title>
        </div>
        <Space>
          {aiStatus?.enabled && (
            <Tooltip title="Run full AI analysis">
              <Button
                icon={<RobotOutlined />}
                loading={analyzing}
                onClick={handleAnalyze}
              >
                AI Analyze
              </Button>
            </Tooltip>
          )}
          {incident.status === 'open' && (
            <Button
              type="primary"
              icon={<CheckCircleOutlined />}
              loading={acknowledging}
              onClick={handleAcknowledge}
            >
              Acknowledge
            </Button>
          )}
          {['open', 'acknowledged', 'in_progress'].includes(incident.status) && (
            <Button type="primary" ghost loading={resolving} onClick={handleResolve}>
              Resolve
            </Button>
          )}
        </Space>
      </div>

      {/* Main Content */}
      <div style={{ display: 'flex', gap: 24 }}>
        {/* Left Column */}
        <div style={{ flex: 2 }}>
          <Card title="Details" style={{ marginBottom: 24 }}>
            <Descriptions column={2}>
              <Descriptions.Item label="Priority">
                <Tag color={priorityColors[incident.priority]}>
                  {incident.priority.toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Severity">
                <Tag color={severityColors[incident.severity]}>{incident.severity.toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Category">{incident.category || '-'}</Descriptions.Item>
              <Descriptions.Item label="Subcategory">{incident.subcategory || '-'}</Descriptions.Item>
              <Descriptions.Item label="Assigned Team">{incident.assigned_team_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="Assigned To">{incident.assigned_user_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="Reported By">{incident.reported_by_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="Created">
                {dayjs(incident.created_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
            </Descriptions>

            {incident.description && (
              <>
                <Divider />
                <Title level={5}>Description</Title>
                <Paragraph>{incident.description}</Paragraph>
              </>
            )}
          </Card>

          {/* AI Classification Card */}
          {aiStatus?.enabled && (
            <Card
              title={
                <Space>
                  <ExperimentOutlined />
                  AI Classification
                </Space>
              }
              style={{ marginBottom: 24 }}
              extra={
                <Button
                  size="small"
                  icon={<ThunderboltOutlined />}
                  loading={classifying}
                  onClick={handleClassify}
                >
                  {aiClassification ? 'Re-classify' : 'Classify'}
                </Button>
              }
            >
              {aiClassification ? (
                <>
                  <div style={{ marginBottom: 16 }}>
                    <Text type="secondary">Confidence</Text>
                    <Progress
                      percent={Math.round((aiClassification.confidence || 0) * 100)}
                      status={aiClassification.confidence && aiClassification.confidence >= 0.7 ? 'success' : 'normal'}
                      size="small"
                    />
                  </div>
                  <Descriptions column={2} size="small">
                    <Descriptions.Item label="Category">
                      <Tag color="blue">{aiClassification.category}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Subcategory">
                      {aiClassification.subcategory}
                    </Descriptions.Item>
                    {aiClassification.suggested_priority && (
                      <Descriptions.Item label="Suggested Priority">
                        <Tag color={priorityColors[aiClassification.suggested_priority]}>
                          {aiClassification.suggested_priority.toUpperCase()}
                        </Tag>
                      </Descriptions.Item>
                    )}
                    {aiClassification.suggested_severity && (
                      <Descriptions.Item label="Suggested Severity">
                        <Tag color={severityColors[aiClassification.suggested_severity]}>
                          {aiClassification.suggested_severity.toUpperCase()}
                        </Tag>
                      </Descriptions.Item>
                    )}
                  </Descriptions>
                  {aiClassification.reasoning && (
                    <>
                      <Divider style={{ margin: '12px 0' }} />
                      <Text type="secondary">AI Reasoning: </Text>
                      <Text>{aiClassification.reasoning}</Text>
                    </>
                  )}
                  {aiClassification.keywords && aiClassification.keywords.length > 0 && (
                    <div style={{ marginTop: 12 }}>
                      <Text type="secondary">Keywords: </Text>
                      {aiClassification.keywords.map((kw) => (
                        <Tag key={kw}>{kw}</Tag>
                      ))}
                    </div>
                  )}
                  {aiClassification.affected_components && aiClassification.affected_components.length > 0 && (
                    <div style={{ marginTop: 8 }}>
                      <Text type="secondary">Affected Components: </Text>
                      {aiClassification.affected_components.map((comp) => (
                        <Tag key={comp} color="purple">{comp}</Tag>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <Empty
                  description="No AI classification yet"
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                >
                  <Button
                    type="primary"
                    size="small"
                    icon={<ThunderboltOutlined />}
                    loading={classifying}
                    onClick={handleClassify}
                  >
                    Run Classification
                  </Button>
                </Empty>
              )}
            </Card>
          )}

          {/* AI Resolution Suggestions Card */}
          {aiStatus?.enabled && (
            <Card
              title={
                <Space>
                  <BulbOutlined />
                  AI Resolution Suggestions
                </Space>
              }
              style={{ marginBottom: 24 }}
              extra={
                <Button
                  size="small"
                  icon={<BulbOutlined />}
                  loading={suggesting}
                  onClick={handleSuggest}
                >
                  {incident.ai_suggested_resolution ? 'Regenerate' : 'Generate'}
                </Button>
              }
            >
              {incident.ai_suggested_resolution ? (
                <div style={{ background: '#f6ffed', padding: 16, borderRadius: 8, border: '1px solid #b7eb8f' }}>
                  <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0 }}>
                    {incident.ai_suggested_resolution}
                  </pre>
                </div>
              ) : (
                <Empty
                  description="No AI suggestions yet"
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                >
                  <Button
                    type="primary"
                    size="small"
                    icon={<BulbOutlined />}
                    loading={suggesting}
                    onClick={handleSuggest}
                  >
                    Generate Suggestions
                  </Button>
                </Empty>
              )}
            </Card>
          )}

          {/* Comments */}
          <Card
            title={
              <Space>
                <MessageOutlined />
                Comments ({incident.comments?.length || 0})
              </Space>
            }
          >
            <List
              dataSource={incident.comments || []}
              locale={{ emptyText: 'No comments yet' }}
              renderItem={(comment) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <Avatar
                        icon={comment.is_ai_generated ? <RobotOutlined /> : <UserOutlined />}
                        style={comment.is_ai_generated ? { backgroundColor: '#1890ff' } : undefined}
                      />
                    }
                    title={
                      <Space>
                        <Text strong>{comment.user_name || (comment.is_ai_generated ? 'AI Assistant' : 'System')}</Text>
                        <Text type="secondary">
                          {dayjs(comment.created_at).fromNow()}
                        </Text>
                        {comment.is_internal && <Tag>Internal</Tag>}
                        {comment.is_ai_generated && <Tag color="blue">AI Generated</Tag>}
                      </Space>
                    }
                    description={comment.content}
                  />
                </List.Item>
              )}
            />

            <Divider />

            <Space.Compact style={{ width: '100%' }}>
              <TextArea
                placeholder="Add a comment..."
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                rows={2}
              />
            </Space.Compact>
            <Button
              type="primary"
              style={{ marginTop: 8 }}
              loading={addingComment}
              onClick={handleAddComment}
              disabled={!commentText.trim()}
            >
              Add Comment
            </Button>
          </Card>
        </div>

        {/* Right Column - Timeline & AI Status */}
        <div style={{ flex: 1 }}>
          {/* AI Status Card */}
          {aiStatus && (
            <Card
              title={
                <Space>
                  <RobotOutlined />
                  AI Status
                </Space>
              }
              size="small"
              style={{ marginBottom: 16 }}
            >
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">AI Enabled</Text>
                  <Tag color={aiStatus.enabled ? 'green' : 'red'}>
                    {aiStatus.enabled ? 'Yes' : 'No'}
                  </Tag>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">Model</Text>
                  <Text>{aiStatus.model}</Text>
                </div>
                {incident.ai_confidence_score && (
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text type="secondary">Confidence</Text>
                    <Text>{Math.round(Number(incident.ai_confidence_score) * 100)}%</Text>
                  </div>
                )}
              </Space>
            </Card>
          )}

          {/* Timeline */}
          <Card title="Timeline">
            <Timeline
              items={
                incident.timeline?.map((event) => ({
                  color: event.event_type === 'resolved' ? 'green' :
                         event.is_automated ? 'blue' : 'gray',
                  dot: event.is_automated ? <RobotOutlined style={{ fontSize: 16 }} /> : undefined,
                  children: (
                    <div>
                      <Text strong style={{ textTransform: 'capitalize' }}>
                        {event.event_type.replace('_', ' ')}
                      </Text>
                      {event.is_automated && (
                        <Tag color="blue" style={{ marginLeft: 8 }}>Auto</Tag>
                      )}
                      <br />
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {event.description}
                      </Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: 11 }}>
                        {dayjs(event.created_at).format('MMM D, HH:mm')}
                        {event.user_name && ` by ${event.user_name}`}
                      </Text>
                    </div>
                  ),
                })) || []
              }
            />
            {(!incident.timeline || incident.timeline.length === 0) && (
              <Empty description="No timeline events" />
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};

export default IncidentDetailPage;
