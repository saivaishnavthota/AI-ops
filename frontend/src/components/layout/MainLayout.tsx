import React from 'react';
import { Outlet } from 'react-router-dom';
import { Layout } from 'antd';
import { useSelector } from 'react-redux';

import Sidebar from './Sidebar';
import Header from './Header';
import type { RootState } from '../../app/store';

const { Content } = Layout;

const MainLayout: React.FC = () => {
  const sidebarCollapsed = useSelector((state: RootState) => state.ui.sidebarCollapsed);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar />
      <Layout style={{ marginLeft: sidebarCollapsed ? 80 : 250, transition: 'margin-left 0.2s' }}>
        <Header />
        <Content
          style={{
            margin: '24px',
            padding: '24px',
            background: '#fff',
            borderRadius: '8px',
            minHeight: 280,
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
