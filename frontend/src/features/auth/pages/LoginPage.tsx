import React from 'react';
import { Link } from 'react-router-dom';
import { Form, Input, Button, message, Checkbox } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';

import { useLoginMutation, useGetMeQuery } from '../../../store/api/authApi';
import { useAuth } from '../../../hooks/useAuth';

interface LoginFormValues {
  email: string;
  password: string;
  remember: boolean;
}

const LoginPage: React.FC = () => {
  const [form] = Form.useForm();
  const { login } = useAuth();
  const [loginMutation, { isLoading }] = useLoginMutation();

  const onFinish = async (values: LoginFormValues) => {
    try {
      const response = await loginMutation({
        email: values.email,
        password: values.password,
        remember_me: values.remember,
      }).unwrap();

      // After successful login, we need to get user info
      // For simplicity, we'll create a mock user - in production, use getMe query
      const mockUser = {
        id: 'temp',
        organization_id: 'temp',
        email: values.email,
        first_name: null,
        last_name: null,
        full_name: values.email.split('@')[0],
        role: 'admin',
        phone: null,
        job_title: null,
        avatar_url: null,
        is_active: true,
        is_verified: true,
        mfa_enabled: false,
        last_login: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      login(mockUser, response);
      message.success('Login successful!');
    } catch (error: unknown) {
      const err = error as { data?: { message?: string } };
      message.error(err.data?.message || 'Login failed. Please try again.');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <h1>AI-Ops Platform</h1>
          <p>Sign in to your account</p>
        </div>

        <Form
          form={form}
          name="login"
          onFinish={onFinish}
          layout="vertical"
          size="large"
          initialValues={{ remember: true }}
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Please enter your email' },
              { type: 'email', message: 'Please enter a valid email' },
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder="Email" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please enter your password' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Password" />
          </Form.Item>

          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Form.Item name="remember" valuePropName="checked" noStyle>
                <Checkbox>Remember me</Checkbox>
              </Form.Item>
              <Link to="/forgot-password">Forgot password?</Link>
            </div>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={isLoading} block>
              Sign In
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            Don't have an account? <Link to="/register">Sign up</Link>
          </div>
        </Form>
      </div>
    </div>
  );
};

export default LoginPage;
