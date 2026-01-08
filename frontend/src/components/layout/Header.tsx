import React from 'react';
import { Layout, Button, Dropdown, Avatar, Space, Input } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

import { toggleSidebar } from '../../store/slices/uiSlice';
import { useAuth } from '../../hooks/useAuth';
import NotificationDropdown from '../notifications/NotificationDropdown';
import type { RootState } from '../../app/store';

const { Header: AntHeader } = Layout;

const Header: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const collapsed = useSelector((state: RootState) => state.ui.sidebarCollapsed);

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      danger: true,
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      logout();
    } else if (key === 'profile') {
      navigate('/settings/profile');
    } else if (key === 'settings') {
      navigate('/settings');
    }
  };

  return (
    <AntHeader
      style={{
        padding: '0 24px',
        background: '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 1px 4px rgba(0, 0, 0, 0.05)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}
    >
      <Space size="large">
        <Button
          type="text"
          icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={() => dispatch(toggleSidebar())}
          style={{ fontSize: 18 }}
        />
        <Input
          placeholder="Search incidents, alerts, tickets..."
          prefix={<SearchOutlined style={{ color: '#bfbfbf' }} />}
          style={{ width: 300 }}
        />
      </Space>

      <Space size="middle">
        {/* <NotificationDropdown /> */}

        <Dropdown
          menu={{
            items: userMenuItems,
            onClick: handleMenuClick,
          }}
          placement="bottomRight"
          trigger={['click']}
        >
          <Space style={{ cursor: 'pointer' }}>
            <Avatar
              icon={<UserOutlined />}
              src={user?.avatar_url}
              style={{ backgroundColor: '#1890ff' }}
            />
            <span style={{ fontWeight: 500 }}>{user?.full_name || user?.email}</span>
          </Space>
        </Dropdown>
      </Space>
    </AntHeader>
  );
};

export default Header;
