/**
 * RoleGuard Component
 *
 * Protects components/routes based on user roles and permissions.
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { Result, Button } from 'antd';
import { useRBAC, UserRole, Permission } from '../../hooks/useRBAC';

interface RoleGuardProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
  requiredPermissions?: Permission[];
  requireAll?: boolean; // If true, user must have ALL permissions, otherwise ANY
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({
  children,
  allowedRoles,
  requiredPermissions,
  requireAll = false,
  fallback,
  redirectTo,
}) => {
  const { role, hasPermission, hasAnyPermission, hasAllPermissions } = useRBAC();

  // Check if user has access
  let hasAccess = true;

  // Check role-based access
  if (allowedRoles && allowedRoles.length > 0) {
    hasAccess = role ? allowedRoles.includes(role) : false;
  }

  // Check permission-based access
  if (hasAccess && requiredPermissions && requiredPermissions.length > 0) {
    if (requireAll) {
      hasAccess = hasAllPermissions(requiredPermissions);
    } else {
      hasAccess = hasAnyPermission(requiredPermissions);
    }
  }

  // If no access, show fallback or redirect
  if (!hasAccess) {
    if (redirectTo) {
      return <Navigate to={redirectTo} replace />;
    }

    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <Result
        status="403"
        title="Access Denied"
        subTitle="You don't have permission to access this page."
        extra={
          <Button type="primary" onClick={() => window.history.back()}>
            Go Back
          </Button>
        }
      />
    );
  }

  return <>{children}</>;
};

/**
 * AdminOnly Component
 * Shorthand for admin-only content
 */
export const AdminOnly: React.FC<{ children: React.ReactNode; fallback?: React.ReactNode }> = ({
  children,
  fallback,
}) => (
  <RoleGuard allowedRoles={['super_admin', 'admin']} fallback={fallback}>
    {children}
  </RoleGuard>
);

/**
 * SuperAdminOnly Component
 * Shorthand for super-admin-only content
 */
export const SuperAdminOnly: React.FC<{ children: React.ReactNode; fallback?: React.ReactNode }> = ({
  children,
  fallback,
}) => (
  <RoleGuard allowedRoles={['super_admin']} fallback={fallback}>
    {children}
  </RoleGuard>
);

/**
 * OperatorAndAbove Component
 * For content accessible to operators, admins, and super admins
 */
export const OperatorAndAbove: React.FC<{ children: React.ReactNode; fallback?: React.ReactNode }> = ({
  children,
  fallback,
}) => (
  <RoleGuard allowedRoles={['super_admin', 'admin', 'operator']} fallback={fallback}>
    {children}
  </RoleGuard>
);

/**
 * WithPermission Component
 * Render children only if user has the required permission
 */
export const WithPermission: React.FC<{
  children: React.ReactNode;
  permission: Permission;
  fallback?: React.ReactNode;
}> = ({ children, permission, fallback }) => {
  const { hasPermission } = useRBAC();

  if (!hasPermission(permission)) {
    return fallback ? <>{fallback}</> : null;
  }

  return <>{children}</>;
};

export default RoleGuard;
