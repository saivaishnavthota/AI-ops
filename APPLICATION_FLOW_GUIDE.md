# AI-Ops Platform - Application Flow & Testing Guide

## 📋 Table of Contents
1. [Access Information](#access-information)
2. [Authentication Flow](#authentication-flow)
3. [Dashboard](#dashboard)
4. [Incidents Management](#incidents-management)
5. [Alerts Management](#alerts-management)
6. [Other Features](#other-features)
7. [API Endpoints Reference](#api-endpoints-reference)

---

## 🔐 Access Information

### Production URLs
- **Frontend**: `http://149.102.158.71:6201` or `http://localhost:6201`
- **Backend API**: `http://149.102.158.71:6200` or `http://localhost:6200`
- **PostgreSQL**: `localhost:6204`
- **Redis**: `localhost:6203`

### Default Login Credentials
```
Email: admin@test.com
Password: Test123!@#
```

---

## 1️⃣ Authentication Flow

### Step 1: Access Login Page
1. Open your browser and navigate to:
   - `http://149.102.158.71:6201` or
   - `http://localhost:6201`
2. You should be automatically redirected to `/login` if not authenticated

### Step 2: Login
1. Enter credentials:
   - **Email**: `admin@test.com`
   - **Password**: `Test123!@#`
2. Optionally check "Remember me"
3. Click **"Sign In"** button
4. **Expected Result**: 
   - Success message: "Login successful!"
   - Redirect to Dashboard (`/`)

### Step 3: Verify Authentication
- Check browser console (F12) for any errors
- Verify you see the main layout with sidebar navigation
- Check that access token is stored in localStorage

### Step 4: Logout (Optional)
- Click on user menu (top right)
- Select "Logout"
- Should redirect back to `/login`

---

## 2️⃣ Dashboard

### Step 1: View Dashboard
1. After login, you should land on the Dashboard (`/`)
2. **Expected Elements**:
   - Page title: "Dashboard"
   - 4 Statistics Cards:
     - Open Incidents (orange)
     - Active Alerts (red)
     - Resolved Today (green)
     - MTTR (Mean Time To Resolve) in hours (blue)

### Step 2: Check Statistics
- Verify statistics are loading from API
- Check browser Network tab for:
  - `GET /api/v1/incidents/statistics`
  - `GET /api/v1/alerts/statistics`

### Step 3: View Recent Incidents Table
- Scroll down to see "Recent Incidents" table
- Table should show:
  - Incident Number (clickable)
  - Title
  - Status (colored tags)
  - Priority (colored tags)
  - Created time

### Step 4: View Alert Distribution
- Check "Alert Distribution" card on the right
- Shows breakdown by severity:
  - Critical (red)
  - Warning (orange)
  - Info (blue)

### Step 5: Quick Actions
- Review "Quick Actions" section
- Links should be clickable (may navigate to respective pages)

---

## 3️⃣ Incidents Management

### A. List Incidents

#### Step 1: Navigate to Incidents
1. Click **"Incidents"** in the sidebar (Warning icon)
2. Or navigate directly to: `http://localhost:6201/incidents`
3. **Expected Result**: Incident List Page loads

#### Step 2: View Incident List
- **Expected Elements**:
  - Page title: "Incidents"
  - "Create Incident" button (top right)
  - Filter section with:
    - Status dropdown
    - Priority dropdown
    - Severity dropdown
    - Search input
  - Data table showing:
    - Incident Number
    - Title
    - Status
    - Priority
    - Severity
    - Created Date
    - Actions column

#### Step 3: Test Filters
1. **Status Filter**:
   - Click status dropdown
   - Select "Open"
   - Table should filter to show only open incidents
2. **Priority Filter**:
   - Select "P1 - Critical"
   - Table should show only P1 incidents
3. **Search**:
   - Type in search box
   - Table should filter by title/description

#### Step 4: Test Pagination
- If more than 20 incidents exist, pagination should appear
- Click next/previous page
- Verify data loads correctly

### B. Create Incident

#### Step 1: Open Create Modal
1. Click **"Create Incident"** button (top right, with Plus icon)
2. **Expected Result**: Modal opens with form

#### Step 2: Fill Incident Form
1. **Title** (Required):
   - Enter: "Test Incident - Database Connection Issue"
2. **Description** (Optional):
   - Enter: "Database connection timeout occurring intermittently"
3. **Priority** (Required):
   - Select: "P1 - Critical"
4. **Severity** (Required):
   - Select: "Critical"
5. **Category** (Optional):
   - Enter: "Database"
6. **Affected Services** (Optional):
   - Type: "postgres-service"
   - Press Enter to add tag
   - Add more: "api-service"
7. **Tags** (Optional):
   - Type: "production"
   - Press Enter to add
   - Add: "urgent"

#### Step 3: Submit Incident
1. Click **"Create"** button in modal
2. **Expected Result**:
   - Success message: "Incident created successfully!"
   - Modal closes
   - Form resets
   - Incident list refreshes
   - New incident appears in table

#### Step 4: Verify Created Incident
- Check the incident list
- New incident should appear at the top (most recent)
- Verify all entered data is displayed correctly

### C. View Incident Details

#### Step 1: Open Incident Detail
1. Click on an incident number in the list (e.g., "INC-000042")
2. Or click "View" in Actions column
3. **Expected Result**: Navigate to `/incidents/{id}`

#### Step 2: View Incident Details Page
- **Expected Elements**:
  - Incident title and number
  - Status badge
  - Priority badge
  - Severity badge
  - Description
  - Metadata section
  - Timeline/Activity section
  - Comments section
  - Related alerts (if any)

#### Step 3: Test Incident Actions
- Look for action buttons:
  - Update Status
  - Assign to Team
  - Add Comment
  - Resolve Incident
- Test each action if available

---

## 4️⃣ Alerts Management

### Step 1: Navigate to Alerts
1. Click **"Alerts"** in the sidebar (Alert icon)
2. Or navigate to: `http://localhost:6201/alerts`
3. **Expected Result**: Alert List Page loads

### Step 2: View Alert List
- **Expected Elements**:
  - Page title: "Alerts"
  - Filter section:
    - Status filter
    - Severity filter
    - Source filter
    - Search input
  - Data table showing:
    - Alert title
    - Severity
    - Status
    - Source
    - Host
    - Service
    - Created date
    - Actions

### Step 3: Test Alert Filters
1. **Status Filter**:
   - Select "Firing" to see active alerts
   - Select "Resolved" to see resolved alerts
2. **Severity Filter**:
   - Select "Critical" to see only critical alerts
3. **Source Filter**:
   - Filter by source (e.g., "prometheus", "datadog")

### Step 4: View Alert Details
1. Click on an alert row or "View" button
2. **Expected Result**: Alert detail drawer/modal opens
3. View:
   - Alert title and message
   - Severity and status
   - Source information
   - Host and service details
   - Tags
   - Related incident (if linked)

### Step 5: Test Alert Actions
- **Acknowledge Alert**: Click acknowledge button
- **Suppress Alert**: Suppress if available
- **Create Incident**: Convert alert to incident
- **Resolve Alert**: Mark as resolved

---

## 5️⃣ Other Features

### Analytics Dashboard
1. Navigate: Click **"Analytics"** in sidebar
2. URL: `http://localhost:6201/analytics`
3. **Expected**: Charts and metrics dashboard
4. **Test**: View different analytics views and filters

### Playbooks
1. Navigate: **Operations** → **Playbooks**
2. URL: `http://localhost:6201/playbooks`
3. **Expected**: List of playbooks for incident response
4. **Test**: View, create, or execute playbooks

### Predictions
1. Navigate: **Operations** → **Predictions**
2. URL: `http://localhost:6201/predictions`
3. **Expected**: AI predictions for incidents/alerts
4. **Test**: View prediction models and results

### Service Desk

#### Tickets
1. Navigate: **Service Desk** → **Tickets**
2. URL: `http://localhost:6201/tickets`
3. **Expected**: Service desk ticket management
4. **Test**: Create, view, update tickets

#### Knowledge Base
1. Navigate: **Service Desk** → **Knowledge Base**
2. URL: `http://localhost:6201/knowledge-base`
3. **Expected**: Knowledge base articles
4. **Test**: Search and view articles

### Cloud Management

#### Resources
1. Navigate: **Cloud** → **Resources**
2. URL: `http://localhost:6201/cloud/resources`
3. **Expected**: Cloud resource inventory

#### Costs
1. Navigate: **Cloud** → **Costs**
2. URL: `http://localhost:6201/cloud/costs`
3. **Expected**: Cloud cost analysis

#### Optimization
1. Navigate: **Cloud** → **Optimization**
2. URL: `http://localhost:6201/cloud/optimization`
3. **Expected**: Cloud optimization recommendations

### Security

#### Events
1. Navigate: **Security** → **Events**
2. URL: `http://localhost:6201/security/events`
3. **Expected**: Security event logs

#### Investigations
1. Navigate: **Security** → **Investigations**
2. URL: `http://localhost:6201/security/investigations`
3. **Expected**: Security investigation cases

### Organization Settings

#### Integrations
1. Navigate: **Integrations** in sidebar
2. URL: `http://localhost:6201/integrations`
3. **Expected**: Integration management (Prometheus, Datadog, etc.)
4. **Test**: View, add, configure integrations

#### Teams
1. Navigate: **Teams** in sidebar
2. URL: `http://localhost:6201/teams`
3. **Expected**: Team management
4. **Test**: View teams, create team, assign members

#### Settings
1. Navigate: **Settings** in sidebar
2. URL: `http://localhost:6201/settings`
3. **Expected**: Organization and user settings
4. **Test**: Update profile, organization settings

#### Audit Log
1. Navigate: **Audit Log** in sidebar
2. URL: `http://localhost:6201/audit-log`
3. **Expected**: Audit trail of system actions
4. **Test**: View and filter audit logs

---

## 6️⃣ API Endpoints Reference

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Register
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Incidents
- `GET /api/v1/incidents` - List incidents (with filters)
- `GET /api/v1/incidents/statistics` - Get incident statistics
- `POST /api/v1/incidents` - Create incident
- `GET /api/v1/incidents/{id}` - Get incident details
- `PATCH /api/v1/incidents/{id}` - Update incident
- `POST /api/v1/incidents/{id}/assign` - Assign incident
- `POST /api/v1/incidents/{id}/resolve` - Resolve incident
- `POST /api/v1/incidents/{id}/comments` - Add comment

### Alerts
- `GET /api/v1/alerts` - List alerts (with filters)
- `GET /api/v1/alerts/statistics` - Get alert statistics
- `GET /api/v1/alerts/{id}` - Get alert details
- `PATCH /api/v1/alerts/{id}` - Update alert
- `POST /api/v1/alerts/{id}/acknowledge` - Acknowledge alert
- `POST /api/v1/alerts/{id}/suppress` - Suppress alert
- `POST /api/v1/alerts/{id}/create-incident` - Create incident from alert

---

## 🧪 Testing Checklist

### ✅ Core Functionality
- [ ] Login with default credentials
- [ ] View dashboard statistics
- [ ] Navigate to Incidents page
- [ ] View incident list
- [ ] Filter incidents by status, priority, severity
- [ ] Create new incident
- [ ] View incident details
- [ ] Navigate to Alerts page
- [ ] View alert list
- [ ] Filter alerts
- [ ] View alert details

### ✅ UI/UX
- [ ] All sidebar links work
- [ ] Buttons are clickable and responsive
- [ ] Modals open and close correctly
- [ ] Forms validate input correctly
- [ ] Success/error messages display
- [ ] Loading states show during API calls
- [ ] Tables paginate correctly

### ✅ API Integration
- [ ] All API calls return data
- [ ] No 401 Unauthorized errors
- [ ] No 500 Internal Server errors
- [ ] CORS headers are correct
- [ ] Token refresh works automatically

### ✅ Data Flow
- [ ] Created incidents appear in list
- [ ] Statistics update after actions
- [ ] Filters persist during navigation
- [ ] Data refreshes after mutations

---

## 🐛 Common Issues & Solutions

### Issue: "401 Unauthorized" errors
**Solution**: 
- Check if token is stored in localStorage
- Verify token refresh logic in `baseApi.ts`
- Check CORS configuration in backend

### Issue: "Create Incident" button not working
**Solution**: 
- Verify modal state is managed correctly
- Check form validation
- Verify API endpoint is correct

### Issue: Data not showing
**Solution**:
- Check browser console for errors
- Verify API responses in Network tab
- Check if backend services are running
- Verify database has data

### Issue: Filters not working
**Solution**:
- Check filter state management
- Verify API query parameters
- Check backend filter logic

---

## 📞 Support

If you encounter issues:
1. Check browser console (F12) for errors
2. Check Network tab for failed API calls
3. Check backend logs: `docker-compose -f docker-compose.prod.yml logs backend`
4. Check frontend logs: `docker-compose -f docker-compose.prod.yml logs frontend`

---

**Last Updated**: 2025-12-23
**Version**: 1.0.0

