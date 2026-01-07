# Audit Logs - User Guide

## Overview
The Audit Logs feature provides a comprehensive, real-time view of all actions performed in the AI-Ops platform. Every user action is automatically logged and can be reviewed for security, compliance, and troubleshooting purposes.

## Accessing Audit Logs

### Navigation
1. Login to the platform
2. Click on **Settings** in the sidebar
3. Select **Audit Log**

### Required Permissions
- ✅ Super Admin
- ✅ Admin  
- ✅ Operator
- ❌ Viewer (Access Denied)

## Dashboard Overview

### Statistics Cards (Top of Page)
1. **Total Actions Today** - Number of actions performed today
2. **Total Actions** - All-time action count
3. **Active Users** - Number of unique users with activity

### Main Features

#### 1. Refresh Button
- Click to reload the latest audit logs
- Updates statistics and log entries
- Shows loading indicator during refresh

#### 2. Export Button
- Downloads audit logs as CSV file
- Includes all filtered results
- Filename format: `audit-log-YYYY-MM-DD.csv`

#### 3. Search Bar
- Search by description
- Search by user name
- Search by resource name
- Real-time filtering

#### 4. Resource Type Filter
- Filter by specific resource types:
  - All (default)
  - incident
  - alert
  - playbook
  - user
  - integration
  - cloud_resource
  - auth

## Audit Log Table

### Columns

1. **Timestamp**
   - When the action occurred
   - Format: MM/DD/YYYY, HH:MM:SS AM/PM
   - Sortable (click column header)

2. **User**
   - User avatar
   - Full name
   - Email address (below name)

3. **Action**
   - Color-coded tags:
     - 🔵 Blue: Create, Update, Acknowledge
     - 🟢 Green: Resolve, Start, Login
     - 🔴 Red: Login Failed
     - 🟣 Purple: Assign
     - 🟠 Orange: Alert Created
     - 🟡 Gold: Role Changed

4. **Resource**
   - Resource type tag
   - Resource name (if available)
   - Resource ID (below, in small text)

5. **Description**
   - Human-readable description of the action
   - Truncated with ellipsis if too long

6. **Status**
   - 🟢 SUCCESS (green)
   - 🔴 FAILURE (red)

7. **IP Address**
   - Source IP of the request
   - Useful for security auditing

8. **Actions**
   - 👁️ View Details button
   - Opens detailed drawer

## Detailed View

Click the eye icon (👁️) on any log entry to see full details:

### Information Displayed

1. **Basic Information**
   - Timestamp (full precision)
   - User (name and email with avatar)
   - Action (color-coded tag)
   - Resource Type
   - Resource ID
   - Resource Name
   - Status
   - IP Address
   - User Agent (browser/device info)

2. **Description Card**
   - Full description text
   - No truncation

3. **Changes Card** (if applicable)
   - Shows before/after values
   - Field-by-field comparison
   - 🔴 Red tag: Old value
   - 🟢 Green tag: New value

4. **Error Card** (if action failed)
   - Error message
   - Stack trace (if available)
   - Displayed in red text

## Common Actions Logged

### Authentication
- `login` - Successful login
- `login_failed` - Failed login attempt
- `logout` - User logout

### Incidents
- `incident.created` - New incident created
- `incident.updated` - Incident details modified
- `incident.assigned` - Incident assigned to user
- `incident.resolved` - Incident marked as resolved
- `incident.closed` - Incident closed

### Alerts
- `alert.created` - New alert triggered
- `alert.acknowledged` - Alert acknowledged by user
- `alert.resolved` - Alert resolved

### Playbooks
- `playbook.executed` - Automated playbook run
- `playbook.created` - New playbook created
- `playbook.updated` - Playbook modified

### Users
- `user.created` - New user account created
- `user.updated` - User profile updated
- `user.role_changed` - User role modified
- `user.deleted` - User account deleted

### Cloud Resources
- `resource.started` - Cloud resource started
- `resource.stopped` - Cloud resource stopped
- `resource.created` - New resource provisioned
- `resource.deleted` - Resource terminated

### Integrations
- `integration.configured` - Integration settings updated
- `integration.enabled` - Integration activated
- `integration.disabled` - Integration deactivated

## Use Cases

### 1. Security Auditing
**Scenario:** Investigate suspicious activity

**Steps:**
1. Filter by resource type: `auth`
2. Look for `login_failed` actions
3. Check IP addresses for unusual locations
4. Review user agents for suspicious patterns
5. Export results for security team

### 2. Compliance Reporting
**Scenario:** Generate monthly compliance report

**Steps:**
1. Set date range (if available in filters)
2. Filter by relevant resource types
3. Click Export button
4. Submit CSV to compliance team

### 3. Troubleshooting
**Scenario:** Find who changed an incident

**Steps:**
1. Search for incident ID or name
2. Review timeline of actions
3. Click View Details on relevant entries
4. Check Changes section for modifications
5. Contact user if needed

### 4. User Activity Monitoring
**Scenario:** Review what a specific user did

**Steps:**
1. Search for user's name or email
2. Review all their actions
3. Check timestamps for activity patterns
4. Verify actions align with their role

### 5. Failed Action Investigation
**Scenario:** Understand why an action failed

**Steps:**
1. Filter by Status: `failure`
2. Click View Details on failed action
3. Read error message in Error Card
4. Check user permissions
5. Verify resource availability

## Tips & Best Practices

### For Administrators
1. **Regular Reviews:** Check audit logs weekly for unusual patterns
2. **Failed Logins:** Monitor failed login attempts for security threats
3. **Role Changes:** Review all role modifications for unauthorized changes
4. **Export Regularly:** Keep monthly exports for compliance

### For Operators
1. **Incident Tracking:** Use audit logs to track incident lifecycle
2. **Playbook Verification:** Confirm automated actions executed correctly
3. **Resource Changes:** Monitor cloud resource modifications
4. **Team Activity:** Review team member actions for coordination

### For Security Teams
1. **IP Monitoring:** Watch for logins from unexpected locations
2. **After-Hours Activity:** Check for unusual activity outside business hours
3. **Bulk Actions:** Look for suspicious bulk operations
4. **Failed Actions:** Investigate repeated failures as potential attacks

## Keyboard Shortcuts

- **Ctrl/Cmd + F:** Focus search bar
- **Esc:** Close detail drawer
- **Arrow Keys:** Navigate table rows (when focused)

## Data Retention

- Audit logs are stored indefinitely
- No automatic deletion
- Administrators can manually delete old logs if needed
- Recommended: Export and archive logs older than 1 year

## Privacy & Security

### What is Logged
- ✅ User actions
- ✅ Timestamps
- ✅ IP addresses
- ✅ Resource changes
- ✅ Success/failure status

### What is NOT Logged
- ❌ Passwords
- ❌ API keys
- ❌ Sensitive personal data
- ❌ File contents
- ❌ Private messages

### Access Control
- Only Admin and Operator roles can view audit logs
- Logs are organization-scoped (can't see other orgs)
- All API access is authenticated
- Failed access attempts are logged

## Troubleshooting

### Issue: No logs showing
**Solution:**
1. Check your role (must be Admin or Operator)
2. Click Refresh button
3. Clear filters
4. Check date range (if set)

### Issue: Search not working
**Solution:**
1. Clear search box and try again
2. Check spelling
3. Try searching by different fields
4. Refresh the page

### Issue: Export fails
**Solution:**
1. Check browser popup blocker
2. Ensure you have filtered results
3. Try with fewer results
4. Check browser console for errors

### Issue: Details not loading
**Solution:**
1. Click Refresh button
2. Try a different log entry
3. Check network connection
4. Reload the page

## API Access

For programmatic access to audit logs:

```bash
# Get audit logs
GET /api/v1/audit-logs?page=1&page_size=50

# Get statistics
GET /api/v1/audit-logs/stats

# Get specific log
GET /api/v1/audit-logs/{log_id}

# Get resource audit trail
GET /api/v1/audit-logs/resource/{resource_type}/{resource_id}
```

See API documentation for full details.

## Support

For questions or issues with audit logs:
1. Check this user guide
2. Review API documentation
3. Contact your system administrator
4. Submit a support ticket

---

**Last Updated:** January 7, 2026
**Version:** 1.0.0
