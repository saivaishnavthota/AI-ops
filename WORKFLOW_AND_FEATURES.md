# AI-Ops Platform - Workflow & Features Guide

## Table of Contents

1. [Platform Overview](#platform-overview)
2. [Core Features](#core-features)
3. [User Roles & Permissions](#user-roles--permissions)
4. [Workflow Diagrams](#workflow-diagrams)
5. [Feature Details](#feature-details)
6. [AI/ML Capabilities](#aiml-capabilities)
7. [Integrations](#integrations)
8. [API Reference](#api-reference)

---

## Platform Overview

The **AI-Ops Platform** is an enterprise-grade, multi-tenant SaaS application designed for IT operations teams to manage incidents, process alerts, and leverage AI-powered automation for faster incident resolution.

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + TypeScript + Ant Design |
| Backend | FastAPI (Python 3.11+) |
| Database | PostgreSQL 15 |
| Cache/Queue | Redis 7 |
| Task Queue | Celery |
| AI Engine | Mistral AI |
| Real-time | WebSocket (Socket.io) |
| Deployment | Docker Compose |

---

## Core Features

### 1. Incident Management
- Full incident lifecycle management
- Priority and severity classification
- AI-powered categorization and resolution suggestions
- Team assignment and escalation
- Timeline tracking and audit trail
- Comments and internal notes

### 2. Alert Management
- Multi-source alert ingestion (webhooks)
- Intelligent deduplication
- AI-powered alert correlation
- Alert suppression with time-based expiry
- Convert alerts to incidents

### 3. AI/ML Capabilities
- Automatic incident classification
- Resolution suggestions with step-by-step instructions
- Alert correlation and root cause analysis
- Predictive incident detection

### 4. Multi-Tenancy
- Organization-level data isolation
- Subscription tiers (Free, Starter, Professional, Enterprise)
- Custom organization settings

### 5. Real-Time Notifications
- WebSocket-based live updates
- In-app notification center
- Email and Slack notifications

### 6. Audit & Compliance
- Comprehensive audit logging
- User action tracking
- Change history for incidents

### 7. Team Management
- Team creation and organization
- On-call status tracking
- Role-based access control

---

## User Roles & Permissions

### Role Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                      SUPER_ADMIN                            │
│                   (Full System Access)                      │
├─────────────────────────────────────────────────────────────┤
│                         ADMIN                               │
│              (Full Organization Access)                     │
├─────────────────────────────────────────────────────────────┤
│                       OPERATOR                              │
│        (Create/Update Incidents, Execute Playbooks)         │
├─────────────────────────────────────────────────────────────┤
│                        VIEWER                               │
│                    (Read-Only Access)                       │
└─────────────────────────────────────────────────────────────┘
```

### Permission Matrix

| Permission | Super Admin | Admin | Operator | Viewer |
|------------|:-----------:|:-----:|:--------:|:------:|
| **Organization** |
| Read Organization | ✅ | ✅ | ✅ | ✅ |
| Update Organization | ✅ | ✅ | ❌ | ❌ |
| Delete Organization | ✅ | ❌ | ❌ | ❌ |
| **Users** |
| Read Users | ✅ | ✅ | ❌ | ❌ |
| Create Users | ✅ | ✅ | ❌ | ❌ |
| Update Users | ✅ | ✅ | ❌ | ❌ |
| Delete Users | ✅ | ✅ | ❌ | ❌ |
| **Incidents** |
| Read Incidents | ✅ | ✅ | ✅ | ✅ |
| Create Incidents | ✅ | ✅ | ✅ | ❌ |
| Update Incidents | ✅ | ✅ | ✅ | ❌ |
| Delete Incidents | ✅ | ✅ | ❌ | ❌ |
| Assign Incidents | ✅ | ✅ | ✅ | ❌ |
| Resolve Incidents | ✅ | ✅ | ✅ | ❌ |
| **Alerts** |
| Read Alerts | ✅ | ✅ | ✅ | ✅ |
| Acknowledge Alerts | ✅ | ✅ | ✅ | ❌ |
| Suppress Alerts | ✅ | ✅ | ✅ | ❌ |
| **Playbooks** |
| Read Playbooks | ✅ | ✅ | ✅ | ✅ |
| Create Playbooks | ✅ | ✅ | ❌ | ❌ |
| Execute Playbooks | ✅ | ✅ | ✅ | ❌ |
| **Settings** |
| Read Settings | ✅ | ✅ | ✅ | ❌ |
| Update Settings | ✅ | ✅ | ❌ | ❌ |
| **Integrations** |
| Manage Integrations | ✅ | ✅ | ❌ | ❌ |
| **Audit** |
| Read Audit Logs | ✅ | ✅ | ❌ | ❌ |

---

## Workflow Diagrams

### 1. User Authentication Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │     │   Frontend   │     │   Backend    │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │  Enter Credentials │                    │
       │───────────────────>│                    │
       │                    │                    │
       │                    │  POST /api/v1/auth/login
       │                    │───────────────────>│
       │                    │                    │
       │                    │                    │ Validate Credentials
       │                    │                    │ Generate JWT Tokens
       │                    │                    │
       │                    │  { access_token,   │
       │                    │    refresh_token,  │
       │                    │    user }          │
       │                    │<───────────────────│
       │                    │                    │
       │                    │ Store Tokens       │
       │                    │ (Redux + Storage)  │
       │                    │                    │
       │  Redirect to       │                    │
       │  Dashboard         │                    │
       │<───────────────────│                    │
       │                    │                    │
```

### 2. Token Refresh Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │     │   Backend    │     │    Redis     │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │  API Request       │                    │
       │  (Expired Token)   │                    │
       │───────────────────>│                    │
       │                    │                    │
       │  401 Unauthorized  │                    │
       │<───────────────────│                    │
       │                    │                    │
       │  POST /api/v1/auth/refresh              │
       │  { refresh_token } │                    │
       │───────────────────>│                    │
       │                    │                    │
       │                    │  Validate Token    │
       │                    │                    │
       │  New Tokens        │                    │
       │<───────────────────│                    │
       │                    │                    │
       │  Retry Original    │                    │
       │  Request           │                    │
       │───────────────────>│                    │
       │                    │                    │
```

### 3. Incident Management Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INCIDENT LIFECYCLE                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────┐
    │  OPEN   │─────>│ ACKNOWLEDGED │─────>│ IN_PROGRESS │─────>│ RESOLVED │
    └─────────┘      └──────────────┘      └─────────────┘      └──────────┘
         │                                                            │
         │                                                            │
         │                                                            ▼
         │                                                      ┌──────────┐
         └─────────────────────────────────────────────────────>│  CLOSED  │
                            (Direct Close)                      └──────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         DETAILED WORKFLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌─────────────────┐
     │ Incident Source │
     │ (Manual/Alert)  │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Create Incident │
     │ Status: OPEN    │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐      ┌─────────────────────────┐
     │ AI Classification│─────>│ Category, Priority,    │
     │ (Automatic)      │      │ Severity, Keywords     │
     └────────┬────────┘      └─────────────────────────┘
              │
              ▼
     ┌─────────────────┐      ┌─────────────────────────┐
     │ Assign to Team/ │─────>│ Notification Sent to   │
     │ User            │      │ Assignee               │
     └────────┬────────┘      └─────────────────────────┘
              │
              ▼
     ┌─────────────────┐
     │ Acknowledge     │
     │ Status: ACK     │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐      ┌─────────────────────────┐
     │ Work on Issue   │─────>│ AI Resolution          │
     │ Status: IN_PROG │      │ Suggestions Available  │
     └────────┬────────┘      └─────────────────────────┘
              │
              │ Add Comments
              │ Update Timeline
              │
              ▼
     ┌─────────────────┐
     │ Resolve         │
     │ + Root Cause    │
     │ + Resolution    │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Close Incident  │
     │ Status: CLOSED  │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Audit Log       │
     │ Created         │
     └─────────────────┘
```

### 4. Alert Processing Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ALERT LIFECYCLE                                    │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐      ┌──────────────┐      ┌──────────────┐
    │ FIRING  │─────>│ ACKNOWLEDGED │─────>│   RESOLVED   │
    └─────────┘      └──────────────┘      └──────────────┘
         │
         │
         ▼
    ┌──────────────┐
    │  SUPPRESSED  │
    └──────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         ALERT INGESTION FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │  Prometheus  │   │   Datadog    │   │  CloudWatch  │   │   Custom     │
  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
         │                  │                  │                  │
         └────────────┬─────┴────────┬─────────┴────────┬─────────┘
                      │              │                  │
                      ▼              ▼                  ▼
              ┌─────────────────────────────────────────────┐
              │            Webhook Endpoint                  │
              │         POST /api/v1/alerts/ingest          │
              └─────────────────────┬───────────────────────┘
                                    │
                                    ▼
              ┌─────────────────────────────────────────────┐
              │           Fingerprint Generation            │
              │    (source + name + host + labels hash)     │
              └─────────────────────┬───────────────────────┘
                                    │
                          ┌─────────┴─────────┐
                          │                   │
                          ▼                   ▼
              ┌───────────────────┐ ┌───────────────────┐
              │  New Alert?       │ │  Existing Alert?  │
              │  Create Record    │ │  Increment Count  │
              │                   │ │  Update Timestamp │
              └─────────┬─────────┘ └─────────┬─────────┘
                        │                     │
                        └──────────┬──────────┘
                                   │
                                   ▼
              ┌─────────────────────────────────────────────┐
              │            AI Correlation                    │
              │     (Group related alerts, find root cause) │
              └─────────────────────┬───────────────────────┘
                                    │
                                    ▼
              ┌─────────────────────────────────────────────┐
              │           Notification Dispatch             │
              │        (WebSocket, Email, Slack)            │
              └─────────────────────────────────────────────┘
```

### 5. Alert to Incident Conversion

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ALERT TO INCIDENT CONVERSION                              │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌─────────────────┐
     │  Alert (Firing) │
     │  Critical/High  │
     └────────┬────────┘
              │
              │ User Action: "Create Incident"
              │
              ▼
     ┌─────────────────┐
     │ Map Alert Data  │
     │ to Incident     │
     │                 │
     │ • Title ← Alert │
     │   Name          │
     │ • Desc ← Alert  │
     │   Description   │
     │ • Priority ←    │
     │   Severity Map  │
     │ • Source ←      │
     │   Alert ID      │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Create Incident │
     │ Link to Alert   │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Update Alert    │
     │ Status: Linked  │
     │ incident_id set │
     └─────────────────┘
```

### 6. AI Analysis Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI INCIDENT ANALYSIS                                 │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌─────────────────┐
     │    Incident     │
     │  (Title + Desc) │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │                     AI CLASSIFICATION                           │
     │  ┌─────────────────────────────────────────────────────────┐   │
     │  │ Input: Title, Description, Source, Severity             │   │
     │  └────────────────────────┬────────────────────────────────┘   │
     │                           │                                     │
     │                           ▼                                     │
     │  ┌─────────────────────────────────────────────────────────┐   │
     │  │                  Mistral AI API                          │   │
     │  │            (mistral-small-latest)                        │   │
     │  └────────────────────────┬────────────────────────────────┘   │
     │                           │                                     │
     │                           ▼                                     │
     │  ┌─────────────────────────────────────────────────────────┐   │
     │  │ Output:                                                  │   │
     │  │ • Category (infrastructure, security, network, etc.)    │   │
     │  │ • Suggested Priority (P1-P5)                            │   │
     │  │ • Suggested Severity (critical, high, medium, low)      │   │
     │  │ • Keywords []                                           │   │
     │  │ • Affected Components []                                │   │
     │  │ • Confidence Score (0-1)                                │   │
     │  └─────────────────────────────────────────────────────────┘   │
     └─────────────────────────────────────────────────────────────────┘
              │
              ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │                   AI RESOLUTION SUGGESTIONS                     │
     │  ┌─────────────────────────────────────────────────────────┐   │
     │  │ Input: Incident + Classification + Historical Data      │   │
     │  └────────────────────────┬────────────────────────────────┘   │
     │                           │                                     │
     │                           ▼                                     │
     │  ┌─────────────────────────────────────────────────────────┐   │
     │  │ Output:                                                  │   │
     │  │ • Resolution Steps []                                   │   │
     │  │   - Step description                                    │   │
     │  │   - Commands to run                                     │   │
     │  │   - Expected outcome                                    │   │
     │  │ • Estimated Resolution Time                             │   │
     │  │ • Risk Level                                            │   │
     │  │ • Related Playbooks []                                  │   │
     │  └─────────────────────────────────────────────────────────┘   │
     └─────────────────────────────────────────────────────────────────┘
```

### 7. Real-Time Notification Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      NOTIFICATION SYSTEM                                     │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌─────────────────┐
     │     Event       │
     │ (Incident/Alert)│
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Create          │
     │ Notification    │
     │ Record          │
     └────────┬────────┘
              │
              ├───────────────────┬───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
     ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
     │   WebSocket     │ │   Email         │ │   Slack         │
     │   (Real-time)   │ │   (Celery Task) │ │   (Celery Task) │
     └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
              │                   │                   │
              ▼                   ▼                   ▼
     ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
     │   Browser       │ │   User Email    │ │   Slack         │
     │   Notification  │ │   Inbox         │ │   Channel       │
     │   Center        │ │                 │ │                 │
     └─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 8. Background Task Processing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CELERY TASK ARCHITECTURE                                │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌─────────────────────────────────────────────────────────────────┐
     │                        CELERY BEAT                              │
     │                   (Scheduled Tasks)                             │
     │  ┌─────────────────────────────────────────────────────────┐   │
     │  │ • check_stale_incidents   (every 5 min)                 │   │
     │  │ • check_stale_alerts      (every 5 min)                 │   │
     │  │ • correlate_alerts        (every 10 min)                │   │
     │  │ • health_check            (every 1 min)                 │   │
     │  │ • daily_report            (daily at 00:00)              │   │
     │  │ • weekly_report           (weekly on Monday)            │   │
     │  └─────────────────────────────────────────────────────────┘   │
     └─────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │                        REDIS BROKER                             │
     │                      (Message Queue)                            │
     └─────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │                      CELERY WORKERS                             │
     │                    (4 Concurrent Workers)                       │
     │  ┌─────────────────────────────────────────────────────────┐   │
     │  │ Task Types:                                              │   │
     │  │ • incidents.analyze_incident                            │   │
     │  │ • incidents.check_stale_incidents                       │   │
     │  │ • alerts.correlate_alerts                               │   │
     │  │ • alerts.check_stale_alerts                             │   │
     │  │ • notifications.send_email                              │   │
     │  │ • notifications.send_slack                              │   │
     │  │ • health.run_health_checks                              │   │
     │  │ • reports.generate_daily_report                         │   │
     │  └─────────────────────────────────────────────────────────┘   │
     └─────────────────────────────────────────────────────────────────┘
```

---

## Feature Details

### 1. Incident Management

#### Incident Properties

| Field | Description |
|-------|-------------|
| `incident_number` | Auto-generated unique identifier (e.g., INC-ABC123) |
| `title` | Short summary of the incident |
| `description` | Detailed description |
| `status` | open, acknowledged, in_progress, resolved, closed |
| `priority` | P1 (Critical), P2 (High), P3 (Medium), P4 (Low), P5 (Planning) |
| `severity` | critical, high, medium, low, info |
| `category` | AI-classified category |
| `assigned_team_id` | Team responsible |
| `assigned_user_id` | Individual assignee |
| `root_cause` | Root cause analysis (filled on resolution) |
| `resolution_notes` | How the incident was resolved |

#### Incident Actions

| Action | Description | Required Role |
|--------|-------------|---------------|
| Create | Create new incident | Operator+ |
| Update | Modify incident details | Operator+ |
| Acknowledge | Mark as being looked at | Operator+ |
| Assign | Assign to team/user | Operator+ |
| Resolve | Mark as resolved with root cause | Operator+ |
| Close | Final closure | Operator+ |
| Delete | Permanently remove | Admin+ |
| Add Comment | Add discussion/notes | Operator+ |

#### Incident Statistics

| Metric | Description |
|--------|-------------|
| Open Incidents | Count of open incidents |
| Resolved Today | Incidents resolved in last 24h |
| MTTR | Mean Time To Resolution |
| By Priority | Breakdown by P1-P5 |
| By Status | Breakdown by status |

---

### 2. Alert Management

#### Alert Properties

| Field | Description |
|-------|-------------|
| `name` | Alert rule name |
| `description` | Alert description |
| `status` | firing, acknowledged, resolved, suppressed |
| `severity` | critical, warning, info |
| `source` | prometheus, datadog, cloudwatch, custom, etc. |
| `host` | Affected host/server |
| `service` | Affected service |
| `metric` | Metric name that triggered alert |
| `fingerprint` | Unique hash for deduplication |
| `occurrence_count` | Number of times alert fired |
| `first_seen_at` | First occurrence timestamp |
| `last_seen_at` | Most recent occurrence |

#### Alert Sources

| Source | Integration Type |
|--------|------------------|
| Prometheus | Webhook (AlertManager) |
| Datadog | Webhook |
| CloudWatch | SNS → Webhook |
| PagerDuty | Webhook |
| Custom | Generic Webhook |

#### Alert Actions

| Action | Description |
|--------|-------------|
| Acknowledge | Mark alert as being handled |
| Suppress | Silence alert for a duration |
| Resolve | Mark as resolved |
| Create Incident | Convert alert to incident |

---

### 3. Team Management

#### Team Structure

```
Organization
    │
    ├── Team A (Engineering)
    │   ├── Admin User
    │   ├── Operator User 1
    │   └── Operator User 2
    │
    ├── Team B (DevOps)
    │   ├── Admin User
    │   └── Operator User 3
    │
    └── Team C (Support)
        └── Viewer User 1
```

#### Team Features

- **On-Call Status**: Track which team members are on-call
- **Notification Preferences**: Team-level notification settings
- **Escalation Policies**: Define escalation chains (future)
- **Team Statistics**: Incidents handled, response times

---

### 4. Playbooks (Runbooks)

#### Playbook Structure

```yaml
Playbook:
  name: "Database Connection Reset"
  description: "Steps to reset database connections"
  category: "database"
  steps:
    - order: 1
      title: "Check connection pool"
      description: "Verify current pool status"
      command: "psql -c 'SELECT count(*) FROM pg_stat_activity'"
    - order: 2
      title: "Reset connections"
      description: "Kill idle connections"
      command: "psql -c 'SELECT pg_terminate_backend(pid)...'"
  tags: ["database", "postgresql", "connections"]
  estimated_duration: "5 minutes"
```

---

### 5. Notifications

#### Notification Types

| Type | Icon | Use Case |
|------|------|----------|
| `info` | ℹ️ | General information |
| `warning` | ⚠️ | Warnings and alerts |
| `error` | ❌ | Errors and failures |
| `success` | ✅ | Successful operations |
| `alert` | 🚨 | New alerts |
| `incident` | 🔥 | Incident updates |
| `system` | ⚙️ | System notifications |

#### Notification Priorities

| Priority | Behavior |
|----------|----------|
| `low` | Standard delivery |
| `medium` | Highlighted in UI |
| `high` | Push notification + highlight |
| `urgent` | All channels + sound alert |

---

### 6. Audit Logging

#### Tracked Actions

| Category | Actions |
|----------|---------|
| Authentication | login, logout, password_change, mfa_enable |
| Incidents | create, update, acknowledge, resolve, close, delete |
| Alerts | acknowledge, suppress, resolve |
| Users | create, update, delete, role_change |
| Teams | create, update, delete, member_add, member_remove |
| Settings | update |
| Integrations | create, update, delete, test |

#### Audit Log Entry

```json
{
  "id": "uuid",
  "action": "incident.resolve",
  "user_id": "uuid",
  "organization_id": "uuid",
  "resource_type": "incident",
  "resource_id": "uuid",
  "details": {
    "root_cause": "Memory leak in service X",
    "resolution_notes": "Restarted service and applied patch"
  },
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## AI/ML Capabilities

### 1. Incident Classification

**Input**: Incident title, description, source, current severity

**Output**:
| Field | Description |
|-------|-------------|
| `category` | One of 10 categories (infrastructure, application, security, network, database, monitoring, authentication, integration, capacity, other) |
| `suggested_priority` | P1-P5 recommendation |
| `suggested_severity` | critical/high/medium/low/info recommendation |
| `keywords` | Extracted key terms |
| `affected_components` | Identified affected systems |
| `confidence` | 0-1 confidence score |

### 2. Resolution Suggestions

**Input**: Classified incident, historical data

**Output**:
| Field | Description |
|-------|-------------|
| `steps` | Ordered resolution steps with commands |
| `estimated_time` | Expected resolution time |
| `risk_level` | low/medium/high risk assessment |
| `related_playbooks` | Matching playbook recommendations |

### 3. Alert Correlation

**Input**: Multiple alerts within time window

**Output**:
| Field | Description |
|-------|-------------|
| `correlation_groups` | Groups of related alerts |
| `root_cause_alert` | Identified root cause |
| `correlation_type` | temporal/topological/causal |
| `confidence` | 0-1 confidence score |

---

## Integrations

### Configured Integrations

| Integration | Purpose | Configuration |
|-------------|---------|---------------|
| **Slack** | Notifications, incident updates | Webhook URL, Bot Token, Channel |
| **PagerDuty** | Escalation, on-call management | API Key, Service ID |
| **Datadog** | Alert ingestion, metrics | API Key, App Key |
| **AWS** | Cloud resource monitoring | Access Key, Secret, Region |
| **Azure** | Cloud resource monitoring | Tenant ID, Client ID, Subscription |

### Webhook Configuration

```
Endpoint: POST /api/v1/alerts/ingest

Headers:
  X-Source-Name: <source_name>
  X-API-Key: <api_key>
  Content-Type: application/json

Payload:
{
  "name": "High CPU Usage",
  "description": "CPU usage exceeded 90%",
  "severity": "warning",
  "host": "web-server-01",
  "service": "nginx",
  "metric": "cpu_usage_percent",
  "value": 92.5,
  "labels": {
    "environment": "production",
    "region": "us-east-1"
  }
}
```

---

## API Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register organization + admin |
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | User logout |
| POST | `/api/v1/auth/password-reset/request` | Request password reset |
| POST | `/api/v1/auth/password-reset/confirm` | Confirm password reset |

### Incident Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/incidents` | List incidents (paginated) |
| POST | `/api/v1/incidents` | Create incident |
| GET | `/api/v1/incidents/{id}` | Get incident details |
| PUT | `/api/v1/incidents/{id}` | Update incident |
| DELETE | `/api/v1/incidents/{id}` | Delete incident |
| POST | `/api/v1/incidents/{id}/acknowledge` | Acknowledge incident |
| POST | `/api/v1/incidents/{id}/resolve` | Resolve incident |
| POST | `/api/v1/incidents/{id}/close` | Close incident |
| POST | `/api/v1/incidents/{id}/assign` | Assign incident |
| GET | `/api/v1/incidents/{id}/comments` | Get comments |
| POST | `/api/v1/incidents/{id}/comments` | Add comment |
| GET | `/api/v1/incidents/{id}/timeline` | Get timeline |
| GET | `/api/v1/incidents/statistics` | Get statistics |

### Alert Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/alerts` | List alerts (paginated) |
| POST | `/api/v1/alerts/ingest` | Ingest alert (webhook) |
| GET | `/api/v1/alerts/{id}` | Get alert details |
| POST | `/api/v1/alerts/{id}/acknowledge` | Acknowledge alert |
| POST | `/api/v1/alerts/{id}/suppress` | Suppress alert |
| POST | `/api/v1/alerts/{id}/resolve` | Resolve alert |
| POST | `/api/v1/alerts/{id}/create-incident` | Create incident from alert |
| POST | `/api/v1/alerts/correlate` | Correlate alerts |

### AI Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/classify` | Classify incident |
| POST | `/api/v1/ai/suggest-resolution` | Get resolution suggestions |
| POST | `/api/v1/ai/analyze` | Full incident analysis |
| POST | `/api/v1/ai/correlate-alerts` | Correlate alerts |
| GET | `/api/v1/ai/status` | AI service status |

### Organization Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/organizations/me` | Get current organization |
| PUT | `/api/v1/organizations/me` | Update organization |
| GET | `/api/v1/organizations/me/users` | List users |
| POST | `/api/v1/organizations/me/users` | Create user |
| GET | `/api/v1/organizations/me/teams` | List teams |
| POST | `/api/v1/organizations/me/teams` | Create team |

### Other Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications` | Get user notifications |
| PUT | `/api/v1/notifications/{id}/read` | Mark as read |
| GET | `/api/v1/audit-logs` | Get audit logs |
| GET | `/api/v1/health` | Health check |

---

## Appendix

### Priority Definitions

| Priority | Name | Response SLA | Resolution SLA |
|----------|------|--------------|----------------|
| P1 | Critical | 15 minutes | 4 hours |
| P2 | High | 30 minutes | 8 hours |
| P3 | Medium | 2 hours | 24 hours |
| P4 | Low | 8 hours | 72 hours |
| P5 | Planning | 24 hours | 2 weeks |

### Severity Definitions

| Severity | Impact |
|----------|--------|
| Critical | Complete service outage, data loss risk |
| High | Major functionality impaired |
| Medium | Partial functionality impaired |
| Low | Minor issue, workaround available |
| Info | Informational, no immediate action |

### Environment Variables

```bash
# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<64-char-secret>

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Redis
REDIS_URL=redis://host:6379/0

# Security
CORS_ORIGINS=https://app.example.com
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI
MISTRAL_API_KEY=<api-key>
MISTRAL_MODEL=mistral-small-latest
AI_CLASSIFICATION_ENABLED=true
AI_SUGGESTION_ENABLED=true
AI_CORRELATION_ENABLED=true
AI_CONFIDENCE_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
```

---

*Document Version: 1.0*
*Last Updated: December 2024*
