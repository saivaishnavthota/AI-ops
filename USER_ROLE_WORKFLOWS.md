# AI-Ops Platform - User Role Workflows

## Overview

The AI-Ops Platform implements Role-Based Access Control (RBAC) with four distinct user roles, each with specific permissions and access levels.

## User Roles

### 1. Super Admin
The highest privilege level with complete system control.

**Access:**
- All platform features
- Organization management
- User management (including creating other super admins)
- System settings
- Audit logs
- All admin capabilities

**Dashboard View:**
- Full statistics and metrics
- All incident/alert data
- System health monitoring
- User activity overview

### 2. Admin
Organization-level administration.

**Access:**
- User management (cannot create super admins)
- Team management
- Settings configuration
- Integrations management
- Cloud resources
- Security features
- Audit logs
- All operator capabilities

**Dashboard View:**
- Organization statistics
- User management tools
- Configuration options
- Full incident/alert management

### 3. Operator
Day-to-day operations and incident management.

**Access:**
- Dashboard (read)
- Incidents (create, update, assign, resolve)
- Alerts (acknowledge, suppress)
- Playbooks (view, execute)
- Teams (view)
- AI Predictions (view)
- Analytics (view)
- Service Desk (tickets, knowledge base)

**Dashboard View:**
- Operational metrics
- Active incidents
- Alert summary
- Team assignments

### 4. Viewer
Read-only access for monitoring and observation.

**Access:**
- Dashboard (read)
- Incidents (read)
- Alerts (read)
- Playbooks (read)
- Analytics (read)

**Dashboard View:**
- Summary statistics
- Incident overview (read-only)
- Alert monitoring (read-only)

---

## Navigation Access by Role

| Feature | Super Admin | Admin | Operator | Viewer |
|---------|-------------|-------|----------|--------|
| Dashboard | Yes | Yes | Yes | Yes |
| Incidents | Full | Full | CRUD + Assign | Read |
| Alerts | Full | Full | Ack/Suppress | Read |
| Analytics | Yes | Yes | Yes | Yes |
| Playbooks | Full | Full | Execute | Read |
| Predictions | Yes | Yes | Yes | No |
| Teams | Full | Full | Read | No |
| Users | Full | Full | No | No |
| Settings | Full | Full | No | No |
| Integrations | Full | Full | No | No |
| Cloud | Full | Full | No | No |
| Security | Full | Full | No | No |
| Audit Log | Yes | Yes | No | No |

---

## Workflow Diagrams

### Admin Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│                         ADMIN WORKFLOW                            │
└──────────────────────────────────────────────────────────────────┘

                              ┌─────────┐
                              │  Login  │
                              └────┬────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
               ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
               │Dashboard│   │  Users  │   │Settings │
               └────┬────┘   └────┬────┘   └────┬────┘
                    │             │              │
    ┌───────────────┼─────────────┼──────────────┼───────────────┐
    │               │             │              │               │
┌───▼───┐      ┌───▼───┐    ┌───▼───┐      ┌───▼───┐       ┌───▼───┐
│Incident│     │Alerts │    │Create │      │Config │       │Integr │
│ Mgmt  │      │ Mgmt  │    │ User  │      │ Org   │       │ations │
└───┬───┘      └───┬───┘    └───┬───┘      └───────┘       └───────┘
    │              │            │
    ▼              ▼            ▼
┌──────────────────────────────────────┐
│         Admin Actions:               │
│  - Create/Edit/Delete Users          │
│  - Assign Roles (up to admin)        │
│  - Configure Organization Settings   │
│  - Manage Integrations               │
│  - View Audit Logs                   │
│  - Manage Teams                      │
│  - Full Incident Control             │
│  - Cloud Resource Management         │
│  - Security Investigations           │
└──────────────────────────────────────┘
```

### Operator Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│                        OPERATOR WORKFLOW                          │
└──────────────────────────────────────────────────────────────────┘

                              ┌─────────┐
                              │  Login  │
                              └────┬────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
         ┌────▼────┐          ┌────▼────┐         ┌────▼────┐
         │Dashboard│          │Incidents│         │ Alerts  │
         └────┬────┘          └────┬────┘         └────┬────┘
              │                    │                    │
              ▼                    ▼                    ▼
    ┌──────────────┐      ┌──────────────┐     ┌──────────────┐
    │ View Stats   │      │   Actions:   │     │   Actions:   │
    │ Active Count │      │  - Create    │     │ - Acknowledge│
    │ Team Status  │      │  - Update    │     │ - Suppress   │
    └──────────────┘      │  - Assign    │     │ - View       │
                          │  - Resolve   │     └──────────────┘
                          └──────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
         ┌────▼────┐          ┌────▼────┐         ┌────▼────┐
         │Playbooks│          │ Tickets │         │Analytics│
         └────┬────┘          └────┬────┘         └─────────┘
              │                    │
              ▼                    ▼
    ┌──────────────┐      ┌──────────────┐
    │   Actions:   │      │   Actions:   │
    │  - View      │      │  - Create    │
    │  - Execute   │      │  - Manage    │
    └──────────────┘      └──────────────┘
```

### Viewer Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│                         VIEWER WORKFLOW                           │
└──────────────────────────────────────────────────────────────────┘

                              ┌─────────┐
                              │  Login  │
                              └────┬────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
    ┌────▼────┐               ┌────▼────┐              ┌────▼────┐
    │Dashboard│               │Incidents│              │ Alerts  │
    │(View)   │               │ (View)  │              │ (View)  │
    └─────────┘               └─────────┘              └─────────┘
         │                         │                         │
         │                         │                         │
    ┌────▼────┐               ┌────▼────┐              ┌────▼────┐
    │Analytics│               │Playbooks│              │         │
    │(View)   │               │ (View)  │              │   N/A   │
    └─────────┘               └─────────┘              └─────────┘

    ┌──────────────────────────────────────────────────────────────┐
    │                    READ-ONLY ACCESS                           │
    │  - View dashboard statistics                                  │
    │  - Monitor incidents (cannot modify)                          │
    │  - View alerts (cannot acknowledge)                           │
    │  - View playbooks (cannot execute)                            │
    │  - View analytics and reports                                 │
    └──────────────────────────────────────────────────────────────┘
```

---

## Permission Matrix

### Incident Permissions

| Action | Super Admin | Admin | Operator | Viewer |
|--------|-------------|-------|----------|--------|
| View | Yes | Yes | Yes | Yes |
| Create | Yes | Yes | Yes | No |
| Update | Yes | Yes | Yes | No |
| Delete | Yes | Yes | No | No |
| Assign | Yes | Yes | Yes | No |
| Resolve | Yes | Yes | Yes | No |

### Alert Permissions

| Action | Super Admin | Admin | Operator | Viewer |
|--------|-------------|-------|----------|--------|
| View | Yes | Yes | Yes | Yes |
| Create | Yes | Yes | No | No |
| Update | Yes | Yes | No | No |
| Delete | Yes | Yes | No | No |
| Acknowledge | Yes | Yes | Yes | No |
| Suppress | Yes | Yes | Yes | No |

### User Management Permissions

| Action | Super Admin | Admin | Operator | Viewer |
|--------|-------------|-------|----------|--------|
| View Users | Yes | Yes | No | No |
| Create User | Yes | Yes | No | No |
| Update User | Yes | Yes* | No | No |
| Delete User | Yes | Yes* | No | No |
| Change Role | Yes | Yes** | No | No |

*Admin cannot modify Super Admin users
**Admin cannot assign Super Admin role

### Playbook Permissions

| Action | Super Admin | Admin | Operator | Viewer |
|--------|-------------|-------|----------|--------|
| View | Yes | Yes | Yes | Yes |
| Create | Yes | Yes | No | No |
| Update | Yes | Yes | No | No |
| Delete | Yes | Yes | No | No |
| Execute | Yes | Yes | Yes | No |

---

## API Endpoints by Role

### Public Endpoints (No Auth)
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/forgot-password`
- `POST /api/v1/auth/reset-password`

### Authenticated Endpoints (All Roles)
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/incidents` (filtered by role)
- `GET /api/v1/alerts` (filtered by role)
- `GET /api/v1/incidents/statistics`

### Operator and Above
- `POST /api/v1/incidents`
- `PUT /api/v1/incidents/{id}`
- `POST /api/v1/incidents/{id}/acknowledge`
- `POST /api/v1/incidents/{id}/resolve`
- `POST /api/v1/incidents/{id}/assign`
- `POST /api/v1/alerts/{id}/acknowledge`
- `POST /api/v1/alerts/{id}/suppress`
- `POST /api/v1/playbooks/{id}/execute`

### Admin Only
- `GET /api/v1/users`
- `POST /api/v1/users`
- `PUT /api/v1/users/{id}`
- `DELETE /api/v1/users/{id}`
- `POST /api/v1/users/{id}/activate`
- `POST /api/v1/users/{id}/deactivate`
- `POST /api/v1/users/{id}/change-role`
- `GET /api/v1/audit-logs`
- `PUT /api/v1/organizations/{id}`
- `GET /api/v1/integrations`
- `POST /api/v1/integrations`

### Super Admin Only
- `DELETE /api/v1/organizations/{id}`
- Create/modify other Super Admin users

---

## Frontend Route Protection

Routes are protected using the `RoleGuard` component:

```tsx
// Admin only route
<Route path="users" element={
  <AdminOnly>
    <UsersPage />
  </AdminOnly>
} />

// Operator and above
<Route path="playbooks" element={
  <OperatorAndAbove>
    <PlaybooksPage />
  </OperatorAndAbove>
} />
```

---

## Implementation Files

### Frontend
- `src/hooks/useRBAC.ts` - Role-based access control hook
- `src/components/auth/RoleGuard.tsx` - Route protection component
- `src/components/layout/Sidebar.tsx` - Role-based navigation
- `src/features/users/pages/UsersPage.tsx` - User management (Admin)
- `src/store/api/usersApi.ts` - Users API hooks

### Backend
- `backend/app/models/user.py` - User model with roles
- `backend/app/api/v1/endpoints/users.py` - User management API
- `backend/app/core/permissions.py` - Permission definitions

---

## Quick Reference

### Login as Different Roles

The system creates an admin user during organization registration. To create users with different roles:

1. Login as Admin/Super Admin
2. Navigate to Users page
3. Click "Add User"
4. Set the desired role

### Testing Role Restrictions

1. **As Viewer**: Try to access `/users` - should see "Access Denied"
2. **As Operator**: Try to delete an incident - should fail
3. **As Admin**: Try to modify a Super Admin user - should fail
4. **As Super Admin**: Full access to all features

---

## Security Best Practices

1. **Principle of Least Privilege**: Assign the minimum role required
2. **Regular Audits**: Review user roles periodically via Audit Log
3. **Super Admin Protection**: Limit Super Admin accounts
4. **Session Management**: Users are logged out on role change
5. **API Validation**: All endpoints validate permissions server-side
