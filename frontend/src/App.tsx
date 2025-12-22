import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Spin } from 'antd';

import { useAuth } from './hooks/useAuth';
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

        {/* Operations */}
        <Route path="playbooks" element={<PlaybooksPage />} />
        <Route path="predictions" element={<PredictionsPage />} />

        {/* Analytics */}
        <Route path="analytics" element={<AnalyticsDashboard />} />

        {/* Service Desk */}
        <Route path="tickets" element={<TicketsPage />} />
        <Route path="knowledge-base" element={<KnowledgeBasePage />} />

        {/* Cloud */}
        <Route path="cloud/resources" element={<CloudResourcesPage />} />
        <Route path="cloud/costs" element={<CloudCostsPage />} />
        <Route path="cloud/optimization" element={<CloudOptimizationPage />} />

        {/* Security */}
        <Route path="security/events" element={<SecurityEventsPage />} />
        <Route path="security/investigations" element={<SecurityInvestigationsPage />} />

        {/* Organization */}
        <Route path="integrations" element={<IntegrationsPage />} />
        <Route path="teams" element={<TeamsPage />} />
        <Route path="settings/*" element={<SettingsPage />} />

        {/* Audit */}
        <Route path="audit-log" element={<AuditLogPage />} />
      </Route>

      {/* Catch all - redirect to dashboard */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
