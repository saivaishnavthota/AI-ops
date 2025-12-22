import React, { useState } from 'react';
import { Card, Row, Col, Typography, Input, Tag, Space, List, Avatar, Modal, message, Button, Divider, Rate } from 'antd';
import { SearchOutlined, FileTextOutlined, BookOutlined, QuestionCircleOutlined, FolderOutlined, LikeOutlined, EyeOutlined, ArrowLeftOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

interface Article {
  id: string;
  title: string;
  excerpt: string;
  content: string;
  category: string;
  views: number;
  helpful: number;
  updatedAt: string;
  tags: string[];
}

const categories = [
  { name: 'Getting Started', count: 12, icon: <BookOutlined /> },
  { name: 'Troubleshooting', count: 28, icon: <QuestionCircleOutlined /> },
  { name: 'API Documentation', count: 15, icon: <FileTextOutlined /> },
  { name: 'Best Practices', count: 8, icon: <FolderOutlined /> },
  { name: 'Security', count: 10, icon: <FolderOutlined /> },
  { name: 'Integrations', count: 18, icon: <FolderOutlined /> },
];

const allArticles: Article[] = [
  {
    id: '1',
    title: 'How to set up monitoring alerts',
    excerpt: 'Learn how to configure alerts for your infrastructure and applications...',
    content: `# How to Set Up Monitoring Alerts

This guide will walk you through the process of setting up monitoring alerts for your infrastructure.

## Prerequisites
- Access to the AI-Ops dashboard
- Admin or Operator role

## Steps

### 1. Navigate to Alert Settings
Go to Settings > Alerts in the main navigation.

### 2. Create a New Alert Rule
Click "Create Alert Rule" and configure:
- **Name**: Give your alert a descriptive name
- **Condition**: Set the metric and threshold
- **Severity**: Choose from Critical, High, Medium, Low
- **Notification**: Select notification channels

### 3. Configure Notification Channels
Set up where alerts should be sent:
- Email notifications
- Slack integration
- PagerDuty escalation

### 4. Test Your Alert
Use the "Test" button to verify your alert configuration works correctly.

## Best Practices
- Start with higher thresholds and tune down
- Use different severities appropriately
- Set up escalation policies for critical alerts`,
    category: 'Getting Started',
    views: 1250,
    helpful: 89,
    updatedAt: '2025-12-20',
    tags: ['alerts', 'monitoring', 'setup'],
  },
  {
    id: '2',
    title: 'Troubleshooting API connection issues',
    excerpt: 'Common causes and solutions for API connectivity problems...',
    content: `# Troubleshooting API Connection Issues

This article covers common API connectivity problems and their solutions.

## Common Issues

### 1. Authentication Errors (401)
**Cause**: Invalid or expired API key
**Solution**:
- Verify your API key is correct
- Check if the key has expired
- Regenerate the key if needed

### 2. Forbidden Errors (403)
**Cause**: Insufficient permissions
**Solution**:
- Check your user role permissions
- Verify IP whitelist settings
- Contact admin for access

### 3. Timeout Errors
**Cause**: Network issues or overloaded servers
**Solution**:
- Check your network connection
- Increase timeout settings
- Verify server status

## Debugging Steps
1. Check the API status page
2. Verify network connectivity
3. Review request headers
4. Check rate limits`,
    category: 'Troubleshooting',
    views: 980,
    helpful: 76,
    updatedAt: '2025-12-18',
    tags: ['api', 'troubleshooting', 'errors'],
  },
  {
    id: '3',
    title: 'Integrating with Slack for notifications',
    excerpt: 'Step-by-step guide to connect your workspace with Slack...',
    content: `# Integrating with Slack for Notifications

Connect AI-Ops with Slack to receive real-time notifications.

## Setup Process

### 1. Create a Slack App
1. Go to api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Name it "AI-Ops Notifications"

### 2. Configure Permissions
Add these OAuth scopes:
- chat:write
- channels:read

### 3. Install to Workspace
Click "Install to Workspace" and authorize.

### 4. Copy the Webhook URL
Navigate to Incoming Webhooks and copy the URL.

### 5. Add to AI-Ops
Go to Integrations > Slack and paste the webhook URL.

## Customizing Notifications
You can customize which alerts go to which channels.`,
    category: 'Integrations',
    views: 856,
    helpful: 92,
    updatedAt: '2025-12-15',
    tags: ['slack', 'integration', 'notifications'],
  },
  {
    id: '4',
    title: 'Understanding incident priority levels',
    excerpt: 'Learn about P1-P5 priority classifications and response times...',
    content: `# Understanding Incident Priority Levels

## Priority Classifications

### P1 - Critical
- Complete service outage
- Response time: 15 minutes
- All hands on deck

### P2 - High
- Major functionality impaired
- Response time: 1 hour
- On-call team response

### P3 - Medium
- Partial impact
- Response time: 4 hours
- Normal business hours

### P4 - Low
- Minor issue
- Response time: 24 hours

### P5 - Planning
- Enhancement request
- Response time: As scheduled`,
    category: 'Best Practices',
    views: 720,
    helpful: 85,
    updatedAt: '2025-12-12',
    tags: ['incidents', 'priority', 'sla'],
  },
  {
    id: '5',
    title: 'Setting up SSO authentication',
    excerpt: 'Configure single sign-on with your identity provider...',
    content: `# Setting up SSO Authentication

Enable Single Sign-On for your organization.

## Supported Providers
- Okta
- Azure AD
- Google Workspace
- OneLogin

## Configuration Steps
1. Go to Settings > Security > SSO
2. Select your identity provider
3. Enter your SSO metadata
4. Configure attribute mapping
5. Test the connection`,
    category: 'Security',
    views: 650,
    helpful: 78,
    updatedAt: '2025-12-10',
    tags: ['sso', 'authentication', 'security'],
  },
  {
    id: '6',
    title: 'New: AI-powered incident classification',
    excerpt: 'How to use AI features for automatic incident categorization...',
    content: `# AI-Powered Incident Classification

Our AI automatically classifies and prioritizes incidents.

## How It Works
The AI analyzes:
- Incident description
- Historical patterns
- Related alerts
- System metrics

## Benefits
- Faster triage
- Consistent classification
- Reduced human error
- Better routing`,
    category: 'Getting Started',
    views: 320,
    helpful: 45,
    updatedAt: '2025-12-22',
    tags: ['ai', 'incidents', 'classification'],
  },
  {
    id: '7',
    title: 'Cloud cost optimization tips',
    excerpt: 'Best practices for reducing your cloud infrastructure costs...',
    content: `# Cloud Cost Optimization Tips

Reduce your cloud spend with these strategies.

## Quick Wins
1. Right-size underutilized instances
2. Use reserved instances for steady workloads
3. Delete unused resources
4. Use spot instances for non-critical work

## Long-term Strategies
- Implement auto-scaling
- Use serverless where appropriate
- Optimize data transfer costs`,
    category: 'Best Practices',
    views: 180,
    helpful: 28,
    updatedAt: '2025-12-21',
    tags: ['cloud', 'cost', 'optimization'],
  },
  {
    id: '8',
    title: 'Playbook automation guide',
    excerpt: 'Create and manage automated runbooks for incident response...',
    content: `# Playbook Automation Guide

Automate your incident response with playbooks.

## Creating a Playbook
1. Navigate to Playbooks
2. Click "Create Playbook"
3. Define trigger conditions
4. Add automation steps
5. Set approval requirements

## Step Types
- Run script
- Send notification
- Create ticket
- Scale resources
- Restart service`,
    category: 'Getting Started',
    views: 210,
    helpful: 35,
    updatedAt: '2025-12-20',
    tags: ['playbooks', 'automation', 'runbooks'],
  },
];

const KnowledgeBasePage: React.FC = () => {
  const [searchText, setSearchText] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [isArticleModalOpen, setIsArticleModalOpen] = useState(false);

  const filteredArticles = allArticles.filter(article => {
    const matchesSearch = !searchText ||
      article.title.toLowerCase().includes(searchText.toLowerCase()) ||
      article.excerpt.toLowerCase().includes(searchText.toLowerCase()) ||
      article.tags.some(t => t.toLowerCase().includes(searchText.toLowerCase()));
    const matchesCategory = !selectedCategory || article.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const popularArticles = [...allArticles].sort((a, b) => b.views - a.views).slice(0, 5);
  const recentArticles = [...allArticles].sort((a, b) =>
    new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  ).slice(0, 3);

  const handleViewArticle = (article: Article) => {
    setSelectedArticle({ ...article, views: article.views + 1 });
    setIsArticleModalOpen(true);
  };

  const handleMarkHelpful = () => {
    if (selectedArticle) {
      setSelectedArticle({ ...selectedArticle, helpful: selectedArticle.helpful + 1 });
      message.success('Thank you for your feedback!');
    }
  };

  const handleCategoryClick = (categoryName: string) => {
    setSelectedCategory(selectedCategory === categoryName ? null : categoryName);
  };

  const handleSearch = (value: string) => {
    setSearchText(value);
    if (value) {
      message.info(`Found ${filteredArticles.length} articles matching "${value}"`);
    }
  };

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <Title level={2}>Knowledge Base</Title>
        <Paragraph type="secondary">
          Find answers, guides, and documentation for the AI-Ops Platform
        </Paragraph>
        <Input.Search
          placeholder="Search articles..."
          prefix={<SearchOutlined />}
          size="large"
          style={{ maxWidth: 500, marginTop: 16 }}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          onSearch={handleSearch}
          enterButton
        />
        {selectedCategory && (
          <div style={{ marginTop: 16 }}>
            <Tag closable onClose={() => setSelectedCategory(null)} color="blue">
              Category: {selectedCategory}
            </Tag>
          </div>
        )}
      </div>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={16}>
          {searchText || selectedCategory ? (
            <Card title={`Search Results (${filteredArticles.length})`}>
              <List
                itemLayout="horizontal"
                dataSource={filteredArticles}
                renderItem={(article) => (
                  <List.Item
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleViewArticle(article)}
                  >
                    <List.Item.Meta
                      avatar={<Avatar icon={<FileTextOutlined />} style={{ backgroundColor: '#1890ff' }} />}
                      title={
                        <Space>
                          <Text strong style={{ color: '#1890ff' }}>{article.title}</Text>
                          <Tag>{article.category}</Tag>
                        </Space>
                      }
                      description={
                        <div>
                          <div>{article.excerpt}</div>
                          <Space style={{ marginTop: 8 }}>
                            <Text type="secondary"><EyeOutlined /> {article.views} views</Text>
                            <Text type="secondary"><LikeOutlined /> {article.helpful}% found helpful</Text>
                          </Space>
                        </div>
                      }
                    />
                  </List.Item>
                )}
                locale={{ emptyText: 'No articles found' }}
              />
            </Card>
          ) : (
            <>
              <Card title="Popular Articles" style={{ marginBottom: 24 }}>
                <List
                  itemLayout="horizontal"
                  dataSource={popularArticles}
                  renderItem={(article) => (
                    <List.Item
                      style={{ cursor: 'pointer' }}
                      onClick={() => handleViewArticle(article)}
                    >
                      <List.Item.Meta
                        avatar={<Avatar icon={<FileTextOutlined />} style={{ backgroundColor: '#1890ff' }} />}
                        title={
                          <Space>
                            <Text strong style={{ color: '#1890ff' }}>{article.title}</Text>
                            <Tag>{article.category}</Tag>
                          </Space>
                        }
                        description={
                          <div>
                            <div>{article.excerpt}</div>
                            <Space style={{ marginTop: 8 }}>
                              <Text type="secondary"><EyeOutlined /> {article.views} views</Text>
                              <Text type="secondary"><LikeOutlined /> {article.helpful}% found helpful</Text>
                            </Space>
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              </Card>

              <Card title="Recently Updated">
                <List
                  itemLayout="horizontal"
                  dataSource={recentArticles}
                  renderItem={(article) => (
                    <List.Item
                      style={{ cursor: 'pointer' }}
                      onClick={() => handleViewArticle(article)}
                    >
                      <List.Item.Meta
                        avatar={<Avatar icon={<FileTextOutlined />} style={{ backgroundColor: '#52c41a' }} />}
                        title={
                          <Space>
                            <Text strong style={{ color: '#1890ff' }}>{article.title}</Text>
                            <Tag color="green">Updated {article.updatedAt}</Tag>
                          </Space>
                        }
                        description={article.excerpt}
                      />
                    </List.Item>
                  )}
                />
              </Card>
            </>
          )}
        </Col>

        <Col xs={24} lg={8}>
          <Card title="Categories">
            <List
              dataSource={categories}
              renderItem={(category) => (
                <List.Item
                  style={{
                    cursor: 'pointer',
                    backgroundColor: selectedCategory === category.name ? '#e6f7ff' : 'transparent',
                    padding: '12px',
                    borderRadius: '4px',
                  }}
                  onClick={() => handleCategoryClick(category.name)}
                >
                  <Space>
                    {category.icon}
                    <Text>{category.name}</Text>
                  </Space>
                  <Tag>{category.count} articles</Tag>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {/* Article Modal */}
      <Modal
        title={null}
        open={isArticleModalOpen}
        onCancel={() => { setIsArticleModalOpen(false); setSelectedArticle(null); }}
        footer={null}
        width={800}
      >
        {selectedArticle && (
          <div>
            <Button
              type="text"
              icon={<ArrowLeftOutlined />}
              onClick={() => setIsArticleModalOpen(false)}
              style={{ marginBottom: 16 }}
            >
              Back to Knowledge Base
            </Button>

            <Title level={3}>{selectedArticle.title}</Title>

            <Space style={{ marginBottom: 16 }}>
              <Tag color="blue">{selectedArticle.category}</Tag>
              <Text type="secondary">Updated: {selectedArticle.updatedAt}</Text>
              <Text type="secondary"><EyeOutlined /> {selectedArticle.views} views</Text>
            </Space>

            <Divider />

            <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
              {selectedArticle.content}
            </div>

            <Divider />

            <Space direction="vertical" style={{ width: '100%' }}>
              <Text>Was this article helpful?</Text>
              <Space>
                <Button type="primary" icon={<LikeOutlined />} onClick={handleMarkHelpful}>
                  Yes, it helped ({selectedArticle.helpful}%)
                </Button>
                <Button>No, I need more help</Button>
              </Space>
              <div style={{ marginTop: 16 }}>
                <Text type="secondary">Tags: </Text>
                {selectedArticle.tags.map(tag => (
                  <Tag key={tag} style={{ cursor: 'pointer' }} onClick={() => { setSearchText(tag); setIsArticleModalOpen(false); }}>
                    {tag}
                  </Tag>
                ))}
              </div>
            </Space>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default KnowledgeBasePage;
