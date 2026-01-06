import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Form, Input, Button, message, Checkbox } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useDispatch } from 'react-redux';

import { useLoginMutation, authApi } from '../../../store/api/authApi';
import { setCredentials } from '../../../store/slices/authSlice';
import type { AppDispatch } from '../../../app/store';

interface LoginFormValues {
  email: string;
  password: string;
  remember: boolean;
}

const LoginPage: React.FC = () => {
  const [form] = Form.useForm();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const [loginMutation, { isLoading }] = useLoginMutation();

  const onFinish = async (values: LoginFormValues) => {
    try {
      // Login and get tokens
      const tokenResponse = await loginMutation({
        email: values.email,
        password: values.password,
        remember_me: values.remember,
      }).unwrap();

      // Store tokens temporarily
      localStorage.setItem('accessToken', tokenResponse.access_token);
      localStorage.setItem('refreshToken', tokenResponse.refresh_token);

      // Fetch user data
      const userResponse = await dispatch(
        authApi.endpoints.getMe.initiate()
      ).unwrap();

      // Update Redux store with user and tokens
      dispatch(setCredentials({
        user: userResponse,
        accessToken: tokenResponse.access_token,
        refreshToken: tokenResponse.refresh_token,
      }));

      message.success('Login successful!');
      navigate('/');
    } catch (error: unknown) {
      // Clear tokens on error
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');

      const err = error as { data?: { message?: string; detail?: string } };
      message.error(err.data?.message || err.data?.detail || 'Login failed. Please try again.');
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
