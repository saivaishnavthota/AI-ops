import React, { useState } from 'react';
import { Card, Table, Typography, Statistic, Row, Col, Tag, Progress, Button, Modal, Drawer, Space, DatePicker, Select, message, Spin } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, DownloadOutlined, EyeOutlined, FilterOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useListCloudCostsQuery, type CloudCostItem } from '../../../store/api/cloudApi';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

const CloudCostsPage: React.FC = () => {
  const { data: costs, isLoading } = useListCloudCostsQuery();
  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [isFilterModalOpen, setIsFilterModalOpen] = useState(false);
  const [selectedCost, setSelectedCost] = useState<CloudCostItem | null>(null);
  const [exporting, setExporting] = useState(false);

  const totalCurrent = costs?.reduce((sum, c) => sum + c.currentMonth, 0) || 0;
  const totalLast = costs?.reduce((sum, c) => sum + c.lastMonth, 0) || 0;
  const totalBudget = costs?.reduce((sum, c) => sum + c.budget, 0) || 0;
  const overallChange = totalLast > 0 ? ((totalCurrent - totalLast) / totalLast) * 100 : 0;

  const handleViewDetails = (cost: CloudCostItem) => {
    setSelectedCost(cost);
    setIsDetailDrawerOpen(true);
  };

  const handleExport = (format: string) => {
    setExporting(true);
    message.loading(`Exporting cost data as ${format}...`, 2);

    setTimeout(() => {
      setExporting(false);
      setIsExportModalOpen(false);
      message.success(`Cost report exported successfully as ${format}`);
    }, 2000);
  };

  const columns: ColumnsType<CloudCostItem> = [
    {
      title: 'Service',
      dataIndex: 'service',
      key: 'service',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <Tag>{record.category}</Tag>
        </div>
      ),
    },
    {
      title: 'Current Month',
      dataIndex: 'currentMonth',
      key: 'currentMonth',
      render: (cost) => `$${cost.toFixed(2)}`,
      align: 'right',
    },
    {
      title: 'Last Month',
      dataIndex: 'lastMonth',
      key: 'lastMonth',
      render: (cost) => `$${cost.toFixed(2)}`,
      align: 'right',
    },
    {
      title: 'Change',
      dataIndex: 'change',
      key: 'change',
      render: (change) => (
        <span style={{ color: change > 0 ? '#cf1322' : change < 0 ? '#3f8600' : 'inherit' }}>
          {change > 0 ? <ArrowUpOutlined /> : change < 0 ? <ArrowDownOutlined /> : null}
          {Math.abs(change).toFixed(1)}%
        </span>
      ),
      align: 'center',
    },
    {
      title: 'Budget Usage',
      dataIndex: 'budget',
      key: 'budget',
      render: (budget, record) => {
        const usage = (record.currentMonth / budget) * 100;
        return (
          <div style={{ width: 120 }}>
            <Progress
              percent={Math.round(usage)}
              size="small"
              status={usage > 100 ? 'exception' : usage > 80 ? 'normal' : 'success'}
            />
          </div>
        );
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_, record) => (
        <Button
          type="text"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetails(record)}
        >
          Details
        </Button>
      ),
    },
  ];

  if (isLoading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}><Spin size="large" /></div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Cost Analysis</Title>
        <Space>
          <Button icon={<FilterOutlined />} onClick={() => setIsFilterModalOpen(true)}>
            Filter
          </Button>
          <Button type="primary" icon={<DownloadOutlined />} onClick={() => setIsExportModalOpen(true)}>
            Export Report
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Current Month"
              value={totalCurrent}
              precision={2}
              prefix="$"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Last Month"
              value={totalLast}
              precision={2}
              prefix="$"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Change"
              value={overallChange}
              precision={1}
              valueStyle={{ color: overallChange > 0 ? '#cf1322' : '#3f8600' }}
              prefix={overallChange > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              suffix="%"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Budget Remaining"
              value={totalBudget - totalCurrent}
              precision={2}
              prefix="$"
              valueStyle={{ color: totalBudget > totalCurrent ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Cost Breakdown by Service">
        <Table
          columns={columns}
          dataSource={costs}
          rowKey="id"
          pagination={false}
          summary={() => (
            <Table.Summary fixed>
              <Table.Summary.Row style={{ fontWeight: 'bold', background: '#fafafa' }}>
                <Table.Summary.Cell index={0}>Total</Table.Summary.Cell>
                <Table.Summary.Cell index={1} align="right">${totalCurrent.toFixed(2)}</Table.Summary.Cell>
                <Table.Summary.Cell index={2} align="right">${totalLast.toFixed(2)}</Table.Summary.Cell>
                <Table.Summary.Cell index={3} align="center">
                  <span style={{ color: overallChange > 0 ? '#cf1322' : '#3f8600' }}>
                    {overallChange > 0 ? '+' : ''}{overallChange.toFixed(1)}%
                  </span>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={4}>
                  <Progress percent={Math.round((totalCurrent / totalBudget) * 100)} size="small" />
                </Table.Summary.Cell>
                <Table.Summary.Cell index={5} />
              </Table.Summary.Row>
            </Table.Summary>
          )}
        />
      </Card>

      {/* Detail Drawer */}
      <Drawer
        title={`Cost Details: ${selectedCost?.service}`}
        open={isDetailDrawerOpen}
        onClose={() => { setIsDetailDrawerOpen(false); setSelectedCost(null); }}
        width={500}
      >
        {selectedCost && (
          <>
            <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
              <Col span={12}>
                <Statistic title="Current Month" value={selectedCost.currentMonth} prefix="$" precision={2} />
              </Col>
              <Col span={12}>
                <Statistic title="Budget" value={selectedCost.budget} prefix="$" precision={2} />
              </Col>
            </Row>
            <Progress
              percent={Math.round((selectedCost.currentMonth / selectedCost.budget) * 100)}
              status={(selectedCost.currentMonth / selectedCost.budget) > 1 ? 'exception' : 'success'}
              style={{ marginBottom: 24 }}
            />
            {selectedCost.details ? (
              <Card title="Resource Breakdown" size="small">
                <Table
                  dataSource={selectedCost.details}
                  columns={[
                    { title: 'Resource', dataIndex: 'resource', key: 'resource' },
                    { title: 'Cost', dataIndex: 'cost', key: 'cost', render: (v) => `$${v.toFixed(2)}` },
                    { title: 'Usage', dataIndex: 'usage', key: 'usage' },
                  ]}
                  rowKey="resource"
                  pagination={false}
                  size="small"
                />
              </Card>
            ) : (
              <Text type="secondary">No detailed breakdown available for this service.</Text>
            )}
          </>
        )}
      </Drawer>

      {/* Export Modal */}
      <Modal
        title="Export Cost Report"
        open={isExportModalOpen}
        onCancel={() => setIsExportModalOpen(false)}
        footer={null}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <Text>Select date range:</Text>
            <RangePicker style={{ width: '100%', marginTop: 8 }} />
          </div>
          <Text>Choose export format:</Text>
          <Space>
            <Button onClick={() => handleExport('CSV')} loading={exporting}>CSV</Button>
            <Button onClick={() => handleExport('PDF')} loading={exporting}>PDF</Button>
            <Button onClick={() => handleExport('Excel')} loading={exporting}>Excel</Button>
          </Space>
        </Space>
      </Modal>

      {/* Filter Modal */}
      <Modal
        title="Filter Costs"
        open={isFilterModalOpen}
        onOk={() => { setIsFilterModalOpen(false); message.success('Filters applied'); }}
        onCancel={() => setIsFilterModalOpen(false)}
        okText="Apply Filters"
      >
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <div>
            <Text>Category:</Text>
            <Select
              mode="multiple"
              placeholder="Select categories"
              style={{ width: '100%', marginTop: 8 }}
              defaultValue={['Compute', 'Database', 'Storage', 'Network', 'Monitoring']}
              options={[
                { value: 'Compute', label: 'Compute' },
                { value: 'Database', label: 'Database' },
                { value: 'Storage', label: 'Storage' },
                { value: 'Network', label: 'Network' },
                { value: 'Monitoring', label: 'Monitoring' },
              ]}
            />
          </div>
          <div>
            <Text>Date Range:</Text>
            <RangePicker style={{ width: '100%', marginTop: 8 }} />
          </div>
        </Space>
      </Modal>
    </div>
  );
};

export default CloudCostsPage;
