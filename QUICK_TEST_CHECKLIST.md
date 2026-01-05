# Quick Testing Checklist

## 🔐 Login
- [ ] Access: `http://localhost:6201` or `http://149.102.158.71:6201`
- [ ] Login: `admin@test.com` / `Test123!@#`
- [ ] Verify redirect to Dashboard

## 📊 Dashboard
- [ ] View 4 statistics cards (Open Incidents, Active Alerts, Resolved Today, MTTR)
- [ ] Check "Recent Incidents" table
- [ ] View "Alert Distribution" chart
- [ ] Verify API calls in Network tab

## ⚠️ Incidents
- [ ] Navigate: Sidebar → **Incidents**
- [ ] View incident list table
- [ ] Test filters: Status, Priority, Severity, Search
- [ ] **Create Incident**: Click "Create Incident" button
  - [ ] Fill form (Title, Priority, Severity required)
  - [ ] Add Affected Services (tags)
  - [ ] Add Tags
  - [ ] Submit and verify success
- [ ] Click incident number to view details
- [ ] Verify incident appears in list after creation

## 🚨 Alerts
- [ ] Navigate: Sidebar → **Alerts**
- [ ] View alert list table
- [ ] Test filters: Status, Severity, Source
- [ ] Click alert to view details
- [ ] Test alert actions (Acknowledge, Suppress, Create Incident)

## 🔍 Other Pages (Quick Check)
- [ ] **Analytics**: Sidebar → Analytics
- [ ] **Playbooks**: Operations → Playbooks
- [ ] **Predictions**: Operations → Predictions
- [ ] **Tickets**: Service Desk → Tickets
- [ ] **Knowledge Base**: Service Desk → Knowledge Base
- [ ] **Cloud Resources**: Cloud → Resources
- [ ] **Cloud Costs**: Cloud → Costs
- [ ] **Security Events**: Security → Events
- [ ] **Integrations**: Sidebar → Integrations
- [ ] **Teams**: Sidebar → Teams
- [ ] **Settings**: Sidebar → Settings
- [ ] **Audit Log**: Sidebar → Audit Log

## ✅ Verification Points
- [ ] No console errors (F12)
- [ ] No 401/403/500 errors in Network tab
- [ ] All buttons clickable
- [ ] Modals open/close correctly
- [ ] Forms validate properly
- [ ] Success messages appear
- [ ] Data refreshes after mutations

---

**Quick Access URLs:**
- Frontend: `http://localhost:6201`
- Backend API: `http://localhost:6200/health`
- Login: `admin@test.com` / `Test123!@#`

