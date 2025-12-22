import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Layout, Menu } from 'antd';
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
} from '@ant-design/icons';
import { useSelector } from 'react-redux';

import type { RootState } from '../../app/store';

const { Sider } = Layout;

const menuItems = [
  {
    key: '/',
    icon: <DashboardOutlined />,
    label: <Link to="/">Dashboard</Link>,
  },
  {
    key: '/incidents',
    icon: <WarningOutlined />,
    label: <Link to="/incidents">Incidents</Link>,
  },
  {
    key: '/alerts',
    icon: <AlertOutlined />,
    label: <Link to="/alerts">Alerts</Link>,
  },
  {
    key: '/analytics',
    icon: <BarChartOutlined />,
    label: <Link to="/analytics">Analytics</Link>,
  },
  {
    type: 'divider' as const,
  },
  {
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
        label: <Link to="/predictions">Predictions</Link>,
      },
    ],
  },
  {
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
  },
  {
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
  },
  {
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
  },
  {
    type: 'divider' as const,
  },
  {
    key: '/integrations',
    icon: <ApiOutlined />,
    label: <Link to="/integrations">Integrations</Link>,
  },
  {
    key: '/teams',
    icon: <TeamOutlined />,
    label: <Link to="/teams">Teams</Link>,
  },
  {
    key: '/audit-log',
    icon: <AuditOutlined />,
    label: <Link to="/audit-log">Audit Log</Link>,
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: <Link to="/settings">Settings</Link>,
  },
];

const Sidebar: React.FC = () => {
  const location = useLocation();
  const collapsed = useSelector((state: RootState) => state.ui.sidebarCollapsed);

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
