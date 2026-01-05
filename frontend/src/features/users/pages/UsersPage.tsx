import React, { useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Input,
  Select,
  Modal,
  Form,
  message,
  Popconfirm,
  Avatar,
  Typography,
  Row,
  Col,
  Tooltip,
  Badge,
} from 'antd';
import {
  UserAddOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  StopOutlined,
  CrownOutlined,
  UserOutlined,
  MailOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

import {
  useListUsersQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useActivateUserMutation,
  useDeactivateUserMutation,
  useChangeUserRoleMutation,
  User,
} from '../../../store/api/usersApi';
import { useRBAC } from '../../../hooks/useRBAC';

const { Title, Text } = Typography;
const { Option } = Select;

const roleColors: Record<string, string> = {
  super_admin: 'purple',
  admin: 'blue',
  operator: 'green',
  viewer: 'default',
};

const roleLabels: Record<string, string> = {
  super_admin: 'Super Admin',
  admin: 'Admin',
  operator: 'Operator',
  viewer: 'Viewer',
};

const UsersPage: React.FC = () => {
  const { isSuperAdmin, user: currentUser } = useRBAC();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<string | undefined>();
  const [activeFilter, setActiveFilter] = useState<boolean | undefined>();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();

  const { data, isLoading, refetch } = useListUsersQuery({
    page,
    page_size: pageSize,
    search: search || undefined,
    role: roleFilter,
    is_active: activeFilter,
  });

  const [createUser, { isLoading: isCreating }] = useCreateUserMutation();
  const [updateUser, { isLoading: isUpdating }] = useUpdateUserMutation();
  const [deleteUser] = useDeleteUserMutation();
  const [activateUser] = useActivateUserMutation();
  const [deactivateUser] = useDeactivateUserMutation();
  const [changeUserRole] = useChangeUserRoleMutation();

  const handleOpenModal = (user?: User) => {
    if (user) {
      setEditingUser(user);
      form.setFieldsValue({
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        role: user.role,
        phone: user.phone,
        job_title: user.job_title,
      });
    } else {
      setEditingUser(null);
      form.resetFields();
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingUser(null);
    form.resetFields();
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingUser) {
        await updateUser({
          id: editingUser.id,
          data: values,
        }).unwrap();
        message.success('User updated successfully');
      } else {
        await createUser(values).unwrap();
        message.success('User created successfully');
      }
      handleCloseModal();
    } catch (error: any) {
      message.error(error?.data?.detail || 'Operation failed');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteUser(id).unwrap();
      message.success('User deleted successfully');
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to delete user');
    }
  };

  const handleToggleActive = async (user: User) => {
    try {
      if (user.is_active) {
        await deactivateUser(user.id).unwrap();
        message.success('User deactivated');
      } else {
        await activateUser(user.id).unwrap();
        message.success('User activated');
      }
    } catch (error: any) {
      message.error(error?.data?.detail || 'Operation failed');
    }
  };

  const handleRoleChange = async (userId: string, role: string) => {
    try {
      await changeUserRole({ id: userId, role }).unwrap();
      message.success('Role updated successfully');
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to change role');
    }
  };

  const columns: ColumnsType<User> = [
    {
      title: 'User',
      key: 'user',
      render: (_, record) => (
        <Space>
          <Avatar
            src={record.avatar_url}
            icon={record.role === 'super_admin' || record.role === 'admin' ? <CrownOutlined /> : <UserOutlined />}
            style={{
              backgroundColor: record.is_active ? roleColors[record.role] === 'purple' ? '#722ed1' : '#1890ff' : '#d9d9d9',
            }}
          />
          <div>
            <div>
              <Text strong>{record.full_name}</Text>
              {record.id === currentUser?.id && (
                <Tag color="cyan" style={{ marginLeft: 8 }}>You</Tag>
              )}
            </div>
            <Text type="secondary" style={{ fontSize: 12 }}>
              <MailOutlined style={{ marginRight: 4 }} />
              {record.email}
            </Text>
          </div>
        </Space>
      ),
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      width: 150,
      render: (role: string, record) => (
        <Select
          value={role}
          style={{ width: 130 }}
          onChange={(newRole) => handleRoleChange(record.id, newRole)}
          disabled={
            record.id === currentUser?.id ||
            (record.role === 'super_admin' && !isSuperAdmin) ||
            (!isSuperAdmin && role === 'super_admin')
          }
        >
          <Option value="viewer">
            <Tag color={roleColors.viewer}>{roleLabels.viewer}</Tag>
          </Option>
          <Option value="operator">
            <Tag color={roleColors.operator}>{roleLabels.operator}</Tag>
          </Option>
          <Option value="admin">
            <Tag color={roleColors.admin}>{roleLabels.admin}</Tag>
          </Option>
          {isSuperAdmin && (
            <Option value="super_admin">
              <Tag color={roleColors.super_admin}>{roleLabels.super_admin}</Tag>
            </Option>
          )}
        </Select>
      ),
    },
    {
      title: 'Status',
      key: 'status',
      width: 100,
      render: (_, record) => (
        <Badge
          status={record.is_active ? 'success' : 'error'}
          text={record.is_active ? 'Active' : 'Inactive'}
        />
      ),
    },
    {
      title: 'Job Title',
      dataIndex: 'job_title',
      key: 'job_title',
      render: (title) => title || '-',
    },
    {
      title: 'Last Login',
      dataIndex: 'last_login',
      key: 'last_login',
      render: (date) => (date ? new Date(date).toLocaleString() : 'Never'),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_, record) => {
        const isCurrentUser = record.id === currentUser?.id;
        const isSuperAdminUser = record.role === 'super_admin';
        const canModify = !isCurrentUser && (!isSuperAdminUser || isSuperAdmin);

        return (
          <Space>
            <Tooltip title="Edit">
              <Button
                type="text"
                icon={<EditOutlined />}
                onClick={() => handleOpenModal(record)}
                disabled={!canModify}
              />
            </Tooltip>
            <Tooltip title={record.is_active ? 'Deactivate' : 'Activate'}>
              <Button
                type="text"
                icon={record.is_active ? <StopOutlined /> : <CheckCircleOutlined />}
                onClick={() => handleToggleActive(record)}
                disabled={!canModify}
                danger={record.is_active}
              />
            </Tooltip>
            <Popconfirm
              title="Delete user"
              description="Are you sure you want to delete this user?"
              onConfirm={() => handleDelete(record.id)}
              okText="Yes"
              cancelText="No"
              disabled={!canModify}
            >
              <Tooltip title="Delete">
                <Button
                  type="text"
                  icon={<DeleteOutlined />}
                  danger
                  disabled={!canModify}
                />
              </Tooltip>
            </Popconfirm>
          </Space>
        );
      },
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
          <Col>
            <Title level={4} style={{ margin: 0 }}>
              <UserOutlined style={{ marginRight: 8 }} />
              User Management
            </Title>
          </Col>
          <Col>
            <Space>
              <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
                Refresh
              </Button>
              <Button
                type="primary"
                icon={<UserAddOutlined />}
                onClick={() => handleOpenModal()}
              >
                Add User
              </Button>
            </Space>
          </Col>
        </Row>

        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={8}>
            <Input
              placeholder="Search by name or email"
              prefix={<SearchOutlined />}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              allowClear
            />
          </Col>
          <Col span={4}>
            <Select
              placeholder="Filter by role"
              value={roleFilter}
              onChange={setRoleFilter}
              allowClear
              style={{ width: '100%' }}
            >
              <Option value="super_admin">Super Admin</Option>
              <Option value="admin">Admin</Option>
              <Option value="operator">Operator</Option>
              <Option value="viewer">Viewer</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Select
              placeholder="Filter by status"
              value={activeFilter}
              onChange={setActiveFilter}
              allowClear
              style={{ width: '100%' }}
            >
              <Option value={true}>Active</Option>
              <Option value={false}>Inactive</Option>
            </Select>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={data?.items}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: data?.total || 0,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} users`,
            onChange: (p, ps) => {
              setPage(p);
              setPageSize(ps);
            },
          }}
        />
      </Card>

      <Modal
        title={editingUser ? 'Edit User' : 'Add New User'}
        open={isModalOpen}
        onCancel={handleCloseModal}
        footer={null}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{ role: 'viewer' }}
        >
          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Please enter email' },
              { type: 'email', message: 'Please enter a valid email' },
            ]}
          >
            <Input disabled={!!editingUser} />
          </Form.Item>

          {!editingUser && (
            <Form.Item
              name="password"
              label="Password"
              rules={[
                { required: true, message: 'Please enter password' },
                { min: 8, message: 'Password must be at least 8 characters' },
              ]}
            >
              <Input.Password />
            </Form.Item>
          )}

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="first_name"
                label="First Name"
                rules={[{ required: true, message: 'Please enter first name' }]}
              >
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="last_name"
                label="Last Name"
                rules={[{ required: true, message: 'Please enter last name' }]}
              >
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="role" label="Role">
            <Select>
              <Option value="viewer">Viewer</Option>
              <Option value="operator">Operator</Option>
              <Option value="admin">Admin</Option>
              {isSuperAdmin && <Option value="super_admin">Super Admin</Option>}
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="phone" label="Phone">
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="job_title" label="Job Title">
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={handleCloseModal}>Cancel</Button>
              <Button
                type="primary"
                htmlType="submit"
                loading={isCreating || isUpdating}
              >
                {editingUser ? 'Update' : 'Create'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UsersPage;
