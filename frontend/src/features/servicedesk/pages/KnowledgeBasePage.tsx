import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Typography, Input, Tag, Space, List, Avatar, Modal, message, Divider, Button } from 'antd';
import { SearchOutlined, FileTextOutlined, BookOutlined, QuestionCircleOutlined, FolderOutlined, LikeOutlined, EyeOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import {
  useGetKBArticlesQuery,
  useGetKBArticleQuery,
  useMarkKBArticleHelpfulMutation,
  KnowledgeBaseArticle,
} from '../../../store/api/ticketsApi';

const { Title, Text, Paragraph } = Typography;

interface Category {
  name: string;
  count: number;
  icon: JSX.Element;
}

const categories: Category[] = [
  { name: 'Getting Started', count: 0, icon: <BookOutlined /> },
  { name: 'Troubleshooting', count: 0, icon: <QuestionCircleOutlined /> },
  { name: 'API Documentation', count: 0, icon: <FileTextOutlined /> },
  { name: 'Best Practices', count: 0, icon: <FolderOutlined /> },
  { name: 'Security', count: 0, icon: <FolderOutlined /> },
  { name: 'Integrations', count: 0, icon: <FolderOutlined /> },
];

const KnowledgeBasePage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const articleIdFromUrl = searchParams.get('article');

  const [searchText, setSearchText] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<KnowledgeBaseArticle | null>(null);
  const [isArticleModalOpen, setIsArticleModalOpen] = useState(false);

  const { data: articlesData, isLoading } = useGetKBArticlesQuery({
    skip: 0,
    limit: 100,
    category: selectedCategory || undefined,
    search: searchText || undefined,
  });

  const { data: allArticlesData } = useGetKBArticlesQuery({ skip: 0, limit: 100 });
  const { data: articleFromUrl } = useGetKBArticleQuery(articleIdFromUrl || '', {
    skip: !articleIdFromUrl,
  });
  const [markHelpful] = useMarkKBArticleHelpfulMutation();

  // Auto-open article if URL parameter is present
  useEffect(() => {
    if (articleFromUrl && articleIdFromUrl) {
      setSelectedArticle(articleFromUrl);
      setIsArticleModalOpen(true);
      // Clear the URL parameter after opening
      setSearchParams({});
    }
  }, [articleFromUrl, articleIdFromUrl, setSearchParams]);

  const allArticles = allArticlesData?.items || [];
  const filteredArticles = articlesData?.items || [];

  // Calculate category counts
  const categoryCounts: Record<string, number> = {};
  allArticles.forEach(article => {
    categoryCounts[article.category] = (categoryCounts[article.category] || 0) + 1;
  });

  const categoriesWithCounts = categories.map(cat => ({
    ...cat,
    count: categoryCounts[cat.name] || 0,
  }));

  const popularArticles = [...allArticles].sort((a, b) => b.views - a.views).slice(0, 5);
  const recentArticles = [...allArticles].sort((a, b) =>
    new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  ).slice(0, 3);

  const handleViewArticle = (article: KnowledgeBaseArticle) => {
    setSelectedArticle(article);
    setIsArticleModalOpen(true);
  };

  const handleMarkHelpful = async () => {
    if (selectedArticle) {
      try {
        await markHelpful(selectedArticle.id).unwrap();
        message.success('Thank you for your feedback!');
      } catch (error: any) {
        message.error(error?.data?.detail || 'Failed to mark as helpful');
      }
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
          loading={isLoading}
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
            <Card title={`Search Results (${filteredArticles.length})`} loading={isLoading}>
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
                            <Text type="secondary"><LikeOutlined /> {article.helpful_count} found helpful</Text>
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
              <Card title="Popular Articles" style={{ marginBottom: 24 }} loading={isLoading}>
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
                              <Text type="secondary"><LikeOutlined /> {article.helpful_count} found helpful</Text>
                            </Space>
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              </Card>

              <Card title="Recently Updated" loading={isLoading}>
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
                            <Tag color="green">Updated {new Date(article.updated_at).toLocaleDateString()}</Tag>
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
              dataSource={categoriesWithCounts}
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
            <button
              type="button"
              style={{
                background: 'none',
                border: 'none',
                padding: '4px 8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                marginBottom: 16,
                color: '#1890ff',
              }}
              onClick={() => setIsArticleModalOpen(false)}
            >
              <ArrowLeftOutlined style={{ marginRight: 8 }} />
              Back to Knowledge Base
            </button>

            <Title level={3}>{selectedArticle.title}</Title>

            <Space style={{ marginBottom: 16 }}>
              <Tag color="blue">{selectedArticle.category}</Tag>
              <Text type="secondary">Updated: {new Date(selectedArticle.updated_at).toLocaleDateString()}</Text>
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
                <button
                  type="button"
                  style={{
                    background: '#1890ff',
                    color: 'white',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                  }}
                  onClick={handleMarkHelpful}
                >
                  <LikeOutlined style={{ marginRight: 8 }} />
                  Yes, it helped ({selectedArticle.helpful_count})
                </button>
                <button
                  type="button"
                  style={{
                    background: 'white',
                    color: '#000',
                    border: '1px solid #d9d9d9',
                    padding: '8px 16px',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  No, I need more help
                </button>
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
