import React from 'react';
import { Link } from 'react-router-dom';
import { Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, TeamOutlined } from '@ant-design/icons';

import { useRegisterMutation } from '../../../store/api/authApi';
import { useAuth } from '../../../hooks/useAuth';

interface RegisterFormValues {
  organization_name: string;
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  confirm_password: string;
}

const RegisterPage: React.FC = () => {
  const [form] = Form.useForm();
  const { login } = useAuth();
  const [registerMutation, { isLoading }] = useRegisterMutation();

  const onFinish = async (values: RegisterFormValues) => {
    try {
      const response = await registerMutation({
        organization_name: values.organization_name,
        email: values.email,
        password: values.password,
        first_name: values.first_name,
        last_name: values.last_name,
      }).unwrap();

      // Create user object from form values
      const mockUser = {
        id: 'temp',
        organization_id: 'temp',
        email: values.email,
        first_name: values.first_name,
        last_name: values.last_name,
        full_name: `${values.first_name} ${values.last_name}`,
        role: 'admin',
        phone: null,
        job_title: null,
        avatar_url: null,
        is_active: true,
        is_verified: false,
        mfa_enabled: false,
        last_login: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      login(mockUser, response);
      message.success('Registration successful! Welcome to AI-Ops Platform.');
    } catch (error: unknown) {
      const err = error as { data?: { message?: string } };
      message.error(err.data?.message || 'Registration failed. Please try again.');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card" style={{ maxWidth: 450 }}>
        <div className="auth-logo">
          <h1>AI-Ops Platform</h1>
          <p>Create your account</p>
        </div>

        <Form
          form={form}
          name="register"
          onFinish={onFinish}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="organization_name"
            rules={[{ required: true, message: 'Please enter your organization name' }]}
          >
            <Input prefix={<TeamOutlined />} placeholder="Organization Name" />
          </Form.Item>

          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="first_name"
              style={{ flex: 1 }}
              rules={[{ required: true, message: 'Required' }]}
            >
              <Input prefix={<UserOutlined />} placeholder="First Name" />
            </Form.Item>

            <Form.Item
              name="last_name"
              style={{ flex: 1 }}
              rules={[{ required: true, message: 'Required' }]}
            >
              <Input placeholder="Last Name" />
            </Form.Item>
          </div>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Please enter your email' },
              { type: 'email', message: 'Please enter a valid email' },
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="Email" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: 'Please enter a password' },
              { min: 8, message: 'Password must be at least 8 characters' },
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Password" />
          </Form.Item>

          <Form.Item
            name="confirm_password"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Please confirm your password' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Passwords do not match'));
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Confirm Password" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={isLoading} block>
              Create Account
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            Already have an account? <Link to="/login">Sign in</Link>
          </div>
        </Form>
      </div>
    </div>
  );
};

export default RegisterPage;
