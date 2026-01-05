import React, { useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Layout, Menu, Tag } from 'antd';
import type { MenuProps } from 'antd';
import {
  DashboardOutlined,
  AlertOutlined,
  WarningOutlined,
  SettingOutlined,
  TeamOutlined,
  CloudOutlined,
  SafetyOutlined,
  DeploymentUnitOutlined,
  ApiOutlined,
  BookOutlined,
  BarChartOutlined,
  AuditOutlined,
  UserOutlined,
  CrownOutlined,
} from '@ant-design/icons';
import { useSelector } from 'react-redux';

import type { RootState } from '../../app/store';
import { useRBAC, UserRole } from '../../hooks/useRBAC';

const { Sider } = Layout;

type MenuItem = Required<MenuProps>['items'][number];

// Build menu items based on role
const buildMenuItems = (role: UserRole | null, collapsed: boolean): MenuItem[] => {
  const isAdmin = role === 'admin' || role === 'super_admin';
  const isOperatorOrAbove = role === 'operator' || isAdmin;

  const items: MenuItem[] = [
    // Dashboard - All users
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: <Link to="/">Dashboard</Link>,
    },
    // Incidents - All users
    {
      key: '/incidents',
      icon: <WarningOutlined />,
      label: <Link to="/incidents">Incidents</Link>,
    },
    // Alerts - All users
    {
      key: '/alerts',
      icon: <AlertOutlined />,
      label: <Link to="/alerts">Alerts</Link>,
    },
    // Analytics - All users
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: <Link to="/analytics">Analytics</Link>,
    },
    { type: 'divider', key: 'divider-1' },
  ];

  // Operations - Operator and above
  if (isOperatorOrAbove) {
    items.push({
      key: 'operations',
      icon: <DeploymentUnitOutlined />,
      label: 'Operations',
      children: [
        {
          key: '/playbooks',
          label: <Link to="/playbooks">Playbooks</Link>,
        },
        {
          key: '/predictions',
          label: <Link to="/predictions">AI Predictions</Link>,
        },
      ],
    });
  }

  // Service Desk - Operator and above
  if (isOperatorOrAbove) {
    items.push({
      key: 'service-desk',
      icon: <BookOutlined />,
      label: 'Service Desk',
      children: [
        {
          key: '/tickets',
          label: <Link to="/tickets">Tickets</Link>,
        },
        {
          key: '/knowledge-base',
          label: <Link to="/knowledge-base">Knowledge Base</Link>,
        },
      ],
    });
  }

  // Cloud - Admin only
  if (isAdmin) {
    items.push({
      key: 'cloud',
      icon: <CloudOutlined />,
      label: 'Cloud',
      children: [
        {
          key: '/cloud/resources',
          label: <Link to="/cloud/resources">Resources</Link>,
        },
        {
          key: '/cloud/costs',
          label: <Link to="/cloud/costs">Cost Analysis</Link>,
        },
        {
          key: '/cloud/optimization',
          label: <Link to="/cloud/optimization">Optimization</Link>,
        },
      ],
    });
  }

  // Security - Admin only
  if (isAdmin) {
    items.push({
      key: 'security',
      icon: <SafetyOutlined />,
      label: 'Security',
      children: [
        {
          key: '/security/events',
          label: <Link to="/security/events">Events</Link>,
        },
        {
          key: '/security/investigations',
          label: <Link to="/security/investigations">Investigations</Link>,
        },
      ],
    });
  }

  // Admin section divider
  if (isAdmin) {
    items.push({ type: 'divider', key: 'divider-2' });
  }

  // Integrations - Admin only
  if (isAdmin) {
    items.push({
      key: '/integrations',
      icon: <ApiOutlined />,
      label: <Link to="/integrations">Integrations</Link>,
    });
  }

  // Teams - Operator and above can view, admin can manage
  if (isOperatorOrAbove) {
    items.push({
      key: '/teams',
      icon: <TeamOutlined />,
      label: <Link to="/teams">Teams</Link>,
    });
  }

  // Users - Admin only
  if (isAdmin) {
    items.push({
      key: '/users',
      icon: <UserOutlined />,
      label: <Link to="/users">Users</Link>,
    });
  }

  // Audit Log - Admin only
  if (isAdmin) {
    items.push({
      key: '/audit-log',
      icon: <AuditOutlined />,
      label: <Link to="/audit-log">Audit Log</Link>,
    });
  }

  // Settings - Admin only
  if (isAdmin) {
    items.push({
      key: '/settings',
      icon: <SettingOutlined />,
      label: <Link to="/settings">Settings</Link>,
    });
  }

  return items;
};

// Role badge colors
const roleBadgeColors: Record<UserRole, string> = {
  super_admin: '#722ed1',
  admin: '#1890ff',
  operator: '#52c41a',
  viewer: '#8c8c8c',
};

const roleLabels: Record<UserRole, string> = {
  super_admin: 'Super Admin',
  admin: 'Admin',
  operator: 'Operator',
  viewer: 'Viewer',
};

const Sidebar: React.FC = () => {
  const location = useLocation();
  const collapsed = useSelector((state: RootState) => state.ui.sidebarCollapsed);
  const { role, user } = useRBAC();

  // Build menu items based on user role
  const menuItems = useMemo(() => buildMenuItems(role, collapsed), [role, collapsed]);

  // Get the current path for menu selection
  const selectedKey = location.pathname;

  // Get open keys based on current path
  const getOpenKeys = () => {
    if (location.pathname.startsWith('/cloud')) return ['cloud'];
    if (location.pathname.startsWith('/security')) return ['security'];
    if (location.pathname.startsWith('/tickets') || location.pathname.startsWith('/knowledge-base')) {
      return ['service-desk'];
    }
    if (location.pathname.startsWith('/playbooks') || location.pathname.startsWith('/predictions')) {
      return ['operations'];
    }
    return [];
  };

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      width={250}
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
      }}
      trigger={null}
    >
      <div
        style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <h1
          style={{
            color: 'white',
            margin: 0,
            fontSize: collapsed ? 18 : 20,
            fontWeight: 600,
            whiteSpace: 'nowrap',
          }}
        >
          {collapsed ? 'AI' : 'AI-Ops Platform'}
        </h1>
      </div>

      {/* User Role Badge */}
      {!collapsed && role && (
        <div
          style={{
            padding: '12px 16px',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          {role === 'super_admin' || role === 'admin' ? (
            <CrownOutlined style={{ color: roleBadgeColors[role] }} />
          ) : (
            <UserOutlined style={{ color: roleBadgeColors[role] }} />
          )}
          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                color: 'rgba(255, 255, 255, 0.85)',
                fontSize: 13,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {user?.fullName}
            </div>
            <Tag
              color={roleBadgeColors[role]}
              style={{ marginTop: 4, fontSize: 11 }}
            >
              {roleLabels[role]}
            </Tag>
          </div>
        </div>
      )}

      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[selectedKey]}
        defaultOpenKeys={getOpenKeys()}
        items={menuItems}
        style={{ borderRight: 0, paddingTop: 16 }}
      />
    </Sider>
  );
};

export default Sidebar;
