import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Form, Input, Button, message, Checkbox } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useDispatch } from 'react-redux';

import { useLoginMutation } from '../../../store/api/authApi';
import { authApi } from '../../../store/api/authApi';
import { setCredentials } from '../../../store/slices/authSlice';

interface LoginFormValues {
  email: string;
  password: string;
  remember: boolean;
}

const LoginPage: React.FC = () => {
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [loginMutation, { isLoading: isLoginLoading }] = useLoginMutation();
  const [isFetchingUser, setIsFetchingUser] = useState(false);

  const isLoading = isLoginLoading || isFetchingUser;

  const onFinish = async (values: LoginFormValues) => {
    try {
      // Step 1: Login and get tokens
      const tokenResponse = await loginMutation({
        email: values.email,
        password: values.password,
        remember_me: values.remember,
      }).unwrap();

      // Step 2: Temporarily store tokens to make authenticated request
      localStorage.setItem('accessToken', tokenResponse.access_token);
      localStorage.setItem('refreshToken', tokenResponse.refresh_token);

      // Step 3: Fetch actual user data from API
      setIsFetchingUser(true);
      try {
        const userResult = await dispatch(
          authApi.endpoints.getMe.initiate(undefined, { forceRefetch: true })
        ).unwrap();

        // Step 4: Store credentials with real user data
        dispatch(setCredentials({
          user: userResult,
          accessToken: tokenResponse.access_token,
          refreshToken: tokenResponse.refresh_token,
        }));

        message.success('Login successful!');
        navigate('/');
      } catch (userError) {
        // If we can't fetch user, clear tokens and show error
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        console.error('Failed to fetch user profile:', userError);
        message.error('Login succeeded but failed to load user profile. Please try again.');
      } finally {
        setIsFetchingUser(false);
      }
    } catch (error: unknown) {
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
