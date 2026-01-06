import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Spin } from 'antd';

import { useAuth } from './hooks/useAuth';
import AppInitializer from './components/AppInitializer';
import MainLayout from './components/layout/MainLayout';
import LoginPage from './features/auth/pages/LoginPage';
import RegisterPage from './features/auth/pages/RegisterPage';
import DashboardPage from './features/dashboard/DashboardPage';
import IncidentListPage from './features/incidents/pages/IncidentListPage';
import IncidentDetailPage from './features/incidents/pages/IncidentDetailPage';
import AlertListPage from './features/alerts/pages/AlertListPage';
import SettingsPage from './features/settings/SettingsPage';

// New pages
import PlaybooksPage from './features/playbooks/pages/PlaybooksPage';
import TeamsPage from './features/teams/pages/TeamsPage';
import IntegrationsPage from './features/integrations/pages/IntegrationsPage';
import CloudResourcesPage from './features/cloud/pages/CloudResourcesPage';
import CloudCostsPage from './features/cloud/pages/CloudCostsPage';
import CloudOptimizationPage from './features/cloud/pages/CloudOptimizationPage';
import SecurityEventsPage from './features/security/pages/SecurityEventsPage';
import SecurityInvestigationsPage from './features/security/pages/SecurityInvestigationsPage';
import TicketsPage from './features/servicedesk/pages/TicketsPage';
import KnowledgeBasePage from './features/servicedesk/pages/KnowledgeBasePage';
import PredictionsPage from './features/predictions/pages/PredictionsPage';
import AnalyticsDashboard from './features/analytics/pages/AnalyticsDashboard';
import AuditLogPage from './features/settings/pages/AuditLogPage';
import UsersPage from './features/users/pages/UsersPage';

// Role-based access control
import { RoleGuard, AdminOnly, OperatorAndAbove } from './components/auth/RoleGuard';

// Protected route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Public route wrapper (redirect if authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

const App: React.FC = () => {
  return (
    <AppInitializer>
      <Routes>
        {/* Public routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          }
        />

        {/* Protected routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          {/* Dashboard */}
          <Route index element={<DashboardPage />} />

          {/* Incidents */}
          <Route path="incidents" element={<IncidentListPage />} />
          <Route path="incidents/:id" element={<IncidentDetailPage />} />

          {/* Alerts */}
          <Route path="alerts" element={<AlertListPage />} />

          {/* Operations - Operator and above */}
          <Route path="playbooks" element={
            <OperatorAndAbove>
              <PlaybooksPage />
            </OperatorAndAbove>
          } />
          <Route path="predictions" element={
            <OperatorAndAbove>
              <PredictionsPage />
            </OperatorAndAbove>
          } />

          {/* Analytics - All users */}
          <Route path="analytics" element={<AnalyticsDashboard />} />

          {/* Service Desk - Operator and above */}
          <Route path="tickets" element={
            <OperatorAndAbove>
              <TicketsPage />
            </OperatorAndAbove>
          } />
          <Route path="knowledge-base" element={
            <OperatorAndAbove>
              <KnowledgeBasePage />
            </OperatorAndAbove>
          } />

          {/* Cloud - Admin only */}
          <Route path="cloud/resources" element={
            <AdminOnly>
              <CloudResourcesPage />
            </AdminOnly>
          } />
          <Route path="cloud/costs" element={
            <AdminOnly>
              <CloudCostsPage />
            </AdminOnly>
          } />
          <Route path="cloud/optimization" element={
            <AdminOnly>
              <CloudOptimizationPage />
            </AdminOnly>
          } />

          {/* Security - Admin only */}
          <Route path="security/events" element={
            <AdminOnly>
              <SecurityEventsPage />
            </AdminOnly>
          } />
          <Route path="security/investigations" element={
            <AdminOnly>
              <SecurityInvestigationsPage />
            </AdminOnly>
          } />

          {/* Organization */}
          <Route path="integrations" element={
            <AdminOnly>
              <IntegrationsPage />
            </AdminOnly>
          } />
          <Route path="teams" element={
            <OperatorAndAbove>
              <TeamsPage />
            </OperatorAndAbove>
          } />

          {/* Admin only routes */}
          <Route path="users" element={
            <AdminOnly>
              <UsersPage />
            </AdminOnly>
          } />
          <Route path="settings/*" element={
            <AdminOnly>
              <SettingsPage />
            </AdminOnly>
          } />
          <Route path="audit-log" element={
            <AdminOnly>
              <AuditLogPage />
            </AdminOnly>
          } />
        </Route>

        {/* Catch all - redirect to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppInitializer>
  );
};

export default App;
