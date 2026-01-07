import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { Card, Menu, Typography, Row, Col, Form, Input, Button, Switch, Select, Divider, message } from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  SettingOutlined,
  BellOutlined,
  SafetyOutlined,
  ApiOutlined,
} from '@ant-design/icons';

import { useAuth } from '../../hooks/useAuth';

const { Title } = Typography;

const GeneralSettings: React.FC = () => {
  const { user } = useAuth();
  const [form] = Form.useForm();

  const handleSave = () => {
    message.success('Settings saved successfully');
  };

  return (
    <div>
      <Title level={4}>General Settings</Title>
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          organization_name: 'My Organization',
          timezone: 'UTC',
          date_format: 'YYYY-MM-DD',
        }}
        onFinish={handleSave}
      >
        <Form.Item label="Organization Name" name="organization_name">
          <Input />
        </Form.Item>
        <Form.Item label="Timezone" name="timezone">
          <Select>
            <Select.Option value="UTC">UTC</Select.Option>
            <Select.Option value="America/New_York">Eastern Time</Select.Option>
            <Select.Option value="America/Los_Angeles">Pacific Time</Select.Option>
            <Select.Option value="Europe/London">London</Select.Option>
            <Select.Option value="Asia/Tokyo">Tokyo</Select.Option>
          </Select>
        </Form.Item>
        <Form.Item label="Date Format" name="date_format">
          <Select>
            <Select.Option value="YYYY-MM-DD">YYYY-MM-DD</Select.Option>
            <Select.Option value="DD/MM/YYYY">DD/MM/YYYY</Select.Option>
            <Select.Option value="MM/DD/YYYY">MM/DD/YYYY</Select.Option>
          </Select>
        </Form.Item>
        <Divider />
        <Title level={5}>AI Features</Title>
        <Form.Item label="Enable AI Suggestions" name="ai_enabled" valuePropName="checked">
          <Switch defaultChecked />
        </Form.Item>
        <Form.Item label="Enable Auto-Remediation" name="auto_remediation" valuePropName="checked">
          <Switch />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">
            Save Settings
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

const ProfileSettings: React.FC = () => {
  const { user } = useAuth();
  const [form] = Form.useForm();

  return (
    <div>
      <Title level={4}>Profile Settings</Title>
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          email: user?.email,
          first_name: user?.first_name,
          last_name: user?.last_name,
          phone: user?.phone,
          job_title: user?.job_title,
        }}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item label="First Name" name="first_name">
              <Input />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item label="Last Name" name="last_name">
              <Input />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item label="Email" name="email">
          <Input disabled />
        </Form.Item>
        <Form.Item label="Phone" name="phone">
          <Input />
        </Form.Item>
        <Form.Item label="Job Title" name="job_title">
          <Input />
        </Form.Item>
        <Form.Item>
          <Button type="primary">Update Profile</Button>
        </Form.Item>
      </Form>
    </div>
  );
};

const NotificationSettings: React.FC = () => {
  return (
    <div>
      <Title level={4}>Notification Settings</Title>
      <Form layout="vertical">
        <Title level={5}>Email Notifications</Title>
        <Form.Item label="Incident Assignments" name="email_incidents" valuePropName="checked">
          <Switch defaultChecked />
        </Form.Item>
        <Form.Item label="Alert Notifications" name="email_alerts" valuePropName="checked">
          <Switch />
        </Form.Item>
        <Form.Item label="Daily Summary" name="email_summary" valuePropName="checked">
          <Switch defaultChecked />
        </Form.Item>
        <Divider />
        <Title level={5}>Browser Notifications</Title>
        <Form.Item label="Enable Browser Notifications" name="browser_notifications" valuePropName="checked">
          <Switch defaultChecked />
        </Form.Item>
        <Form.Item>
          <Button type="primary">Save Preferences</Button>
        </Form.Item>
      </Form>
    </div>
  );
};

const menuItems = [
  { key: '/settings', icon: <SettingOutlined />, label: 'General' },
  { key: '/settings/profile', icon: <UserOutlined />, label: 'Profile' },
  { key: '/settings/notifications', icon: <BellOutlined />, label: 'Notifications' },
  { key: '/settings/security', icon: <SafetyOutlined />, label: 'Security' },
  { key: '/settings/api-keys', icon: <ApiOutlined />, label: 'API Keys' },
];

const SettingsPage: React.FC = () => {
  const location = useLocation();
  const { user } = useAuth();

  // Filter menu items based on user role
  const visibleMenuItems = user?.role === 'admin'
    ? menuItems
    : menuItems.filter(item => item.key === '/settings/profile' || item.key === '/settings/notifications');

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>Settings</Title>
      <Row gutter={24}>
        <Col span={6}>
          <Card>
            <Menu
              mode="vertical"
              selectedKeys={[location.pathname]}
              items={visibleMenuItems.map((item) => ({
                ...item,
                label: <Link to={item.key}>{item.label}</Link>,
              }))}
            />
          </Card>
        </Col>
        <Col span={18}>
          <Card>
            <Routes>
              <Route index element={user?.role === 'admin' ? <GeneralSettings /> : <ProfileSettings />} />
              <Route path="profile" element={<ProfileSettings />} />
              <Route path="notifications" element={<NotificationSettings />} />
              <Route path="security" element={<div><Title level={4}>Security Settings</Title><p>Coming soon...</p></div>} />
              <Route path="api-keys" element={<div><Title level={4}>API Keys</Title><p>Coming soon...</p></div>} />
            </Routes>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SettingsPage;
