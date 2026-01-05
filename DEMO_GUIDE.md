# AI-Ops Platform Demo Guide

This guide provides everything you need to demonstrate the AI-Ops Platform to your team lead.

## Quick Start

### 1. Seed Demo Data

Before demonstrating, populate the database with realistic demo data:

```bash
cd backend
python -m scripts.seed_demo_data
```

This creates:
- 1 Organization (TechOps Demo Company)
- 6 Users across 4 roles
- 4 Teams with member assignments
- 30+ Incidents with comments and timeline
- 60+ Alerts with correlations
- 8 Playbooks with execution history
- Notifications and Audit logs

### 2. Start the Application

```bash
# Development mode
docker-compose up -d

# Or production mode
docker-compose -f docker-compose.prod.yml up -d
```

---

## Demo User Accounts

All accounts use password: `Demo@123!`

| Role | Email | Description | Access Level |
|------|-------|-------------|--------------|
| Super Admin | super.admin@demo.com | Platform Administrator | Full access to all features |
| Admin | admin@demo.com | IT Operations Manager | Manage users, teams, settings |
| Operator | operator@demo.com | Senior SRE | Create/manage incidents, run playbooks |
| Operator | operator2@demo.com | DevOps Engineer | Create/manage incidents, run playbooks |
| Viewer | viewer@demo.com | Support Analyst | Read-only access |
| Viewer | viewer2@demo.com | Technical Writer | Read-only access |

---

## Role-Based Access Control (RBAC) Demo

### Demonstrating RBAC Differences

1. **Login as Super Admin** (super.admin@demo.com)
   - Show full sidebar with all menu items
   - Navigate to Users page - can create/edit/delete users
   - Navigate to Settings - can modify organization settings
   - Navigate to Audit Log - can see all actions

2. **Login as Admin** (admin@demo.com)
   - Similar access to Super Admin
   - Can manage teams and users
   - Can approve playbook executions

3. **Login as Operator** (operator@demo.com)
   - Cannot see Users management
   - Cannot modify organization settings
   - CAN create and manage incidents
   - CAN run playbooks
   - CAN acknowledge alerts

4. **Login as Viewer** (viewer@demo.com)
   - Read-only access everywhere
   - Cannot create incidents
   - Cannot run playbooks
   - Cannot acknowledge alerts
   - Show disabled buttons/actions

---

## Feature Walkthrough

### 1. Dashboard Overview

**Path:** `/dashboard`

**Demonstrate:**
- Real-time statistics (total incidents, open alerts, resolved today)
- Incident trend charts (30-day history)
- Alert distribution by severity
- Active incidents list
- Recent activity feed

**Key Points:**
- Data updates in real-time via WebSocket
- Charts show historical trends for capacity planning
- Quick actions to jump to relevant sections

---

### 2. Incident Management

**Path:** `/incidents`

**Demo Scenario: Create and Resolve an Incident**

1. **View Incident List**
   - Show filtering by status, priority, severity
   - Demonstrate search functionality
   - Point out AI classification badges

2. **Create New Incident**
   - Click "Create Incident"
   - Title: "High CPU utilization on api-server-01"
   - Description: "CPU usage has exceeded 90% for the past 15 minutes, causing slow API responses"
   - Watch AI automatically classify it:
     - Category: Infrastructure
     - Subcategory: Compute
     - Priority: P2
     - Severity: High
   - Show AI confidence score

3. **View AI Suggestions**
   - Open the incident details
   - Show "AI Suggested Resolution" tab
   - Walk through suggested steps:
     1. Identify top CPU-consuming processes
     2. Check for runaway processes
     3. Review application logs
     4. Scale if needed
   - Point out estimated time and risk level

4. **Incident Lifecycle**
   - Acknowledge incident
   - Assign to team/user
   - Add comment with investigation findings
   - Show timeline updates
   - Resolve with resolution notes
   - Close incident

---

### 3. Alert Management

**Path:** `/alerts`

**Demo Scenario: Alert Correlation**

1. **View Alert Dashboard**
   - Show alerts from multiple sources (Prometheus, Datadog, NewRelic)
   - Demonstrate severity filtering
   - Show alert count badges

2. **Alert Correlation**
   - Point out grouped alerts (same host/service)
   - Show AI correlation confidence scores
   - Demonstrate root cause identification
   - Create incident from correlated alerts

3. **Alert Actions**
   - Acknowledge alert
   - Suppress alert (with reason)
   - Link alert to existing incident

---

### 4. Playbooks & Automation

**Path:** `/playbooks`

**Demo Scenario: Execute a Playbook**

1. **Browse Playbooks**
   - Show different automation types
   - Point out success rates
   - Show required approval indicators

2. **View Playbook Details**
   - Open "Restart Service" playbook
   - Walk through automation steps
   - Explain approval workflow
   - Show trigger conditions

3. **Execute Playbook**
   - Select an incident
   - Click "Run Playbook"
   - If requires approval, show approval flow
   - View execution logs in real-time
   - Show success/failure status

4. **View Execution History**
   - Show past executions
   - Demonstrate filtering by status
   - View detailed execution logs

---

### 5. Team Management

**Path:** `/teams`

**Demo Scenario: Team Organization**

1. **View Teams**
   - Show 4 demo teams
   - Infrastructure, Application Support, Security, Database

2. **Team Details**
   - Click on a team
   - Show team members
   - Highlight roles (Lead, Member, On-Call)
   - Show assigned incidents

3. **On-Call Rotation**
   - Point out on-call indicators
   - Explain notification routing

---

### 6. Analytics & Reporting

**Path:** `/analytics`

**Demonstrate:**
- Incident trends over 30 days
- Mean Time To Resolution (MTTR) metrics
- Incidents by category breakdown
- Team performance comparison
- Alert volume analysis

**Key Points:**
- Use filters to drill down
- Export capabilities for reports
- Historical trend analysis

---

### 7. AI Features Demo

**Key AI Capabilities:**

1. **Automatic Incident Classification**
   - Create incident with keywords
   - Watch real-time classification
   - Show category, priority, severity assignment
   - Display confidence score

2. **Resolution Suggestions**
   - AI provides step-by-step guidance
   - Category-specific recommendations
   - Risk assessment included
   - Automation possibilities flagged

3. **Alert Correlation**
   - Automatic grouping of related alerts
   - Root cause identification
   - Noise reduction
   - Incident creation suggestions

**Demo Flow:**

```
Create incident: "Database connection pool exhausted on db-primary-01"

Expected AI Response:
- Category: Database
- Subcategory: Connection
- Priority: P1 (Critical)
- Severity: Critical

AI Suggestions:
1. Check connection pool usage
2. Identify long-running queries
3. Terminate idle connections
4. Increase pool size
5. Restart application
6. Monitor metrics
```

---

### 8. Audit & Compliance

**Path:** `/audit`

**Demonstrate:**
- All actions are logged
- Filter by user, action type, resource
- Show action details (who, what, when)
- Compliance reporting capabilities

---

## Demo Scenarios

### Scenario 1: Critical Incident Response (5 minutes)

1. Login as operator@demo.com
2. Show alert dashboard with critical alert
3. Create incident from alert
4. Watch AI classification
5. Review AI suggestions
6. Run "Restart Service" playbook
7. Resolve incident
8. Show audit trail

### Scenario 2: RBAC Demonstration (3 minutes)

1. Login as viewer@demo.com
2. Show limited menu options
3. Try to create incident (show disabled)
4. Switch to operator@demo.com
5. Show full capabilities
6. Switch to admin@demo.com
7. Show user management

### Scenario 3: AI Intelligence Demo (5 minutes)

1. Create incident with database keywords
2. Show classification confidence
3. Review category-specific suggestions
4. Show alert correlation groups
5. Demonstrate root cause detection

---

## Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL container
docker-compose logs postgres

# Restart services
docker-compose restart
```

**Seed Data Not Showing**
```bash
# Re-run seed script
cd backend
python -m scripts.seed_demo_data
```

**Login Issues**
- Ensure you're using correct password: `Demo@123!`
- Check if user exists in database
- Verify SECRET_KEY is set in environment

---

## Architecture Highlights

Point out during demo:
- **Multi-tenant**: Organization-based data isolation
- **Real-time**: WebSocket for live updates
- **AI-Powered**: Mock AI works without API key
- **Scalable**: Redis caching, Celery for background tasks
- **Secure**: JWT auth, RBAC, Audit logging
- **Modern Stack**: FastAPI + React + PostgreSQL

---

## Post-Demo Notes

After the demo, you can:
1. Clear demo data: Delete the organization in the database
2. Re-seed fresh data: Run `python -m scripts.seed_demo_data`
3. Reset user passwords if needed

---

## Contact

For issues or questions about the demo, refer to:
- Technical documentation in `/docs`
- API documentation at `/api/v1/docs`
- Source code comments
