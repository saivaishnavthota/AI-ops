/**
 * Role-Based Access Control (RBAC) Hook
 *
 * Provides role checking and permission management for the frontend.
 */

import { useSelector } from 'react-redux';
import type { RootState } from '../app/store';

// Define user roles
export type UserRole = 'super_admin' | 'admin' | 'operator' | 'viewer';

// Define permissions
export type Permission =
  | 'org:read' | 'org:update' | 'org:delete'
  | 'users:read' | 'users:create' | 'users:update' | 'users:delete'
  | 'teams:read' | 'teams:create' | 'teams:update' | 'teams:delete'
  | 'incidents:read' | 'incidents:create' | 'incidents:update' | 'incidents:delete' | 'incidents:assign' | 'incidents:resolve'
  | 'alerts:read' | 'alerts:create' | 'alerts:update' | 'alerts:delete' | 'alerts:acknowledge' | 'alerts:suppress'
  | 'playbooks:read' | 'playbooks:create' | 'playbooks:update' | 'playbooks:delete' | 'playbooks:execute'
  | 'settings:read' | 'settings:update'
  | 'integrations:read' | 'integrations:create' | 'integrations:update' | 'integrations:delete'
  | 'audit:read';

// Role-based permission mapping
const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  super_admin: [
    'org:read', 'org:update', 'org:delete',
    'users:read', 'users:create', 'users:update', 'users:delete',
    'teams:read', 'teams:create', 'teams:update', 'teams:delete',
    'incidents:read', 'incidents:create', 'incidents:update', 'incidents:delete', 'incidents:assign', 'incidents:resolve',
    'alerts:read', 'alerts:create', 'alerts:update', 'alerts:delete', 'alerts:acknowledge', 'alerts:suppress',
    'playbooks:read', 'playbooks:create', 'playbooks:update', 'playbooks:delete', 'playbooks:execute',
    'settings:read', 'settings:update',
    'integrations:read', 'integrations:create', 'integrations:update', 'integrations:delete',
    'audit:read',
  ],
  admin: [
    'org:read', 'org:update',
    'users:read', 'users:create', 'users:update', 'users:delete',
    'teams:read', 'teams:create', 'teams:update', 'teams:delete',
    'incidents:read', 'incidents:create', 'incidents:update', 'incidents:delete', 'incidents:assign', 'incidents:resolve',
    'alerts:read', 'alerts:create', 'alerts:update', 'alerts:delete', 'alerts:acknowledge', 'alerts:suppress',
    'playbooks:read', 'playbooks:create', 'playbooks:update', 'playbooks:delete', 'playbooks:execute',
    'settings:read', 'settings:update',
    'integrations:read', 'integrations:create', 'integrations:update', 'integrations:delete',
    'audit:read',
  ],
  operator: [
    'org:read',
    'users:read',
    'teams:read',
    'incidents:read', 'incidents:create', 'incidents:update', 'incidents:assign', 'incidents:resolve',
    'alerts:read', 'alerts:acknowledge', 'alerts:suppress',
    'playbooks:read', 'playbooks:execute',
    'settings:read',
    'integrations:read',
  ],
  viewer: [
    'org:read',
    'users:read',
    'teams:read',
    'incidents:read',
    'alerts:read',
    'playbooks:read',
    'settings:read',
  ],
};

// Navigation items that should be visible per role
export const ROLE_NAVIGATION: Record<UserRole, string[]> = {
  super_admin: [
    'dashboard', 'incidents', 'alerts', 'playbooks', 'predictions',
    'analytics', 'teams', 'users', 'settings', 'integrations', 'audit-log',
  ],
  admin: [
    'dashboard', 'incidents', 'alerts', 'playbooks', 'predictions',
    'analytics', 'teams', 'users', 'settings', 'integrations', 'audit-log',
  ],
  operator: [
    'dashboard', 'incidents', 'alerts', 'playbooks', 'predictions',
    'analytics', 'teams',
  ],
  viewer: [
    'dashboard', 'incidents', 'alerts', 'playbooks', 'analytics',
  ],
};

export interface UseRBACReturn {
  user: {
    id: string;
    email: string;
    firstName: string | null;
    lastName: string | null;
    fullName: string;
    role: UserRole;
  } | null;
  role: UserRole | null;
  isAdmin: boolean;
  isSuperAdmin: boolean;
  isOperator: boolean;
  isViewer: boolean;
  hasPermission: (permission: Permission) => boolean;
  hasAnyPermission: (permissions: Permission[]) => boolean;
  hasAllPermissions: (permissions: Permission[]) => boolean;
  canAccessRoute: (route: string) => boolean;
  getPermissions: () => Permission[];
  getAllowedNavItems: () => string[];
}

export function useRBAC(): UseRBACReturn {
  const authUser = useSelector((state: RootState) => state.auth.user);

  const role = (authUser?.role as UserRole) || null;

  const user = authUser ? {
    id: authUser.id,
    email: authUser.email,
    firstName: authUser.first_name,
    lastName: authUser.last_name,
    fullName: authUser.full_name || authUser.email.split('@')[0],
    role: role as UserRole,
  } : null;

  const isAdmin = role === 'admin' || role === 'super_admin';
  const isSuperAdmin = role === 'super_admin';
  const isOperator = role === 'operator';
  const isViewer = role === 'viewer';

  const getPermissions = (): Permission[] => {
    if (!role) return [];
    return ROLE_PERMISSIONS[role] || [];
  };

  const hasPermission = (permission: Permission): boolean => {
    if (!role) return false;
    const permissions = ROLE_PERMISSIONS[role] || [];
    return permissions.includes(permission);
  };

  const hasAnyPermission = (permissions: Permission[]): boolean => {
    return permissions.some(p => hasPermission(p));
  };

  const hasAllPermissions = (permissions: Permission[]): boolean => {
    return permissions.every(p => hasPermission(p));
  };

  const canAccessRoute = (route: string): boolean => {
    if (!role) return false;
    const allowedRoutes = ROLE_NAVIGATION[role] || [];
    return allowedRoutes.includes(route);
  };

  const getAllowedNavItems = (): string[] => {
    if (!role) return [];
    return ROLE_NAVIGATION[role] || [];
  };

  return {
    user,
    role,
    isAdmin,
    isSuperAdmin,
    isOperator,
    isViewer,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    canAccessRoute,
    getPermissions,
    getAllowedNavItems,
  };
}

export default useRBAC;
