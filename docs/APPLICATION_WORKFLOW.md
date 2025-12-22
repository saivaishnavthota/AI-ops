# AI-Ops Platform - Application Workflow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     React Frontend (Vite + TypeScript)               │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │    │
│  │  │Dashboard │ │Incidents │ │ Alerts   │ │Playbooks │ │Settings  │  │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │    │
│  │  │ Cloud    │ │ Security │ │ Tickets  │ │  Teams   │ │Predictions│  │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │    │
│  │                    ↓ RTK Query + WebSocket ↓                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     FastAPI Backend (Python 3.11)                    │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                    API Endpoints (v1)                         │   │    │
│  │  │  /auth  /incidents  /alerts  /organizations  /ai  /ws        │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                    Service Layer                              │   │    │
│  │  │  AuthService  IncidentService  AlertService  AIService       │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                    AI/ML Module (Mistral)                     │   │    │
│  │  │  Classifier  Suggester  Correlator  Predictor                │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                      │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                 │
│  │   SQLite/      │  │     Redis      │  │    Celery      │                 │
│  │   PostgreSQL   │  │   (Cache +     │  │   (Background  │                 │
│  │   (Primary DB) │  │    Pub/Sub)    │  │    Tasks)      │                 │
│  └────────────────┘  └────────────────┘  └────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Workflows

### 1. Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────▶│  Login   │────▶│  Auth    │────▶│  JWT     │
│  Opens   │     │  Page    │     │  API     │     │  Token   │
│  App     │     │          │     │          │     │  Issued  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                        │
                                        ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Access  │◀────│  Store   │◀────│ Validate │◀────│  Hash    │
│  Granted │     │  Token   │     │ Password │     │  Compare │
└──────────┘     └──────────┘     └──────────┘     └──────────┘

Token Structure:
- Access Token (15 min expiry)
- Refresh Token (7 days expiry)
- User ID, Org ID, Roles embedded
```

### 2. Incident Management Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    INCIDENT LIFECYCLE                            │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────┐
  │  ALERT   │ ─── Automatic trigger from monitoring
  │ RECEIVED │
  └────┬─────┘
       │
       ▼
  ┌──────────┐     ┌──────────────────────────────────────┐
  │  AI      │────▶│ Classification:                      │
  │ ANALYSIS │     │ - Category (Infrastructure/App/DB)   │
  └────┬─────┘     │ - Priority (P1-P5)                   │
       │           │ - Severity (Critical/High/Med/Low)   │
       │           │ - Suggested Resolution               │
       │           └──────────────────────────────────────┘
       ▼
  ┌──────────┐
  │ INCIDENT │ ─── Create incident with AI classification
  │ CREATED  │
  └────┬─────┘
       │
       ▼
  ┌──────────┐     ┌──────────────────────────────────────┐
  │ ASSIGNED │────▶│ Assignment Rules:                    │
  │          │     │ - Auto-assign based on category      │
  └────┬─────┘     │ - On-call team routing               │
       │           │ - Workload balancing                 │
       │           └──────────────────────────────────────┘
       ▼
  ┌──────────┐
  │INVESTIGATING│
  │          │ ─── Team works on resolution
  └────┬─────┘
       │
       ├────────────────┬────────────────┐
       ▼                ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ RESOLVED │    │ ESCALATED│    │ ON HOLD  │
  └────┬─────┘    └────┬─────┘    └──────────┘
       │               │
       ▼               ▼
  ┌──────────┐    ┌──────────┐
  │  CLOSED  │    │ P1 TEAM  │
  └──────────┘    │ ENGAGED  │
                  └──────────┘
```

### 3. Alert Correlation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ALERT PROCESSING PIPELINE                     │
└─────────────────────────────────────────────────────────────────┘

  External Sources                    AI Correlation Engine
  ┌──────────────┐                   ┌──────────────────────┐
  │ Prometheus   │──┐                │                      │
  ├──────────────┤  │                │  ┌────────────────┐  │
  │ Grafana      │──┤                │  │ Time-based     │  │
  ├──────────────┤  │   Webhook      │  │ Correlation    │  │
  │ DataDog      │──┼───────────────▶│  └────────────────┘  │
  ├──────────────┤  │   Ingestion    │  ┌────────────────┐  │
  │ PagerDuty    │──┤                │  │ Causal         │  │
  ├──────────────┤  │                │  │ Analysis       │  │
  │ Custom       │──┘                │  └────────────────┘  │
  └──────────────┘                   │  ┌────────────────┐  │
                                     │  │ Root Cause     │  │
                                     │  │ Identification │  │
                                     │  └────────────────┘  │
                                     └──────────┬───────────┘
                                                │
                                                ▼
                                     ┌──────────────────────┐
                                     │   Correlated Groups  │
                                     │   ┌──────────────┐   │
                                     │   │ Group 1: DB  │   │
                                     │   │ 5 alerts     │   │
                                     │   │ Root: Disk   │   │
                                     │   └──────────────┘   │
                                     │   ┌──────────────┐   │
                                     │   │ Group 2: API │   │
                                     │   │ 3 alerts     │   │
                                     │   │ Root: Memory │   │
                                     │   └──────────────┘   │
                                     └──────────────────────┘
```

### 4. Playbook Automation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLAYBOOK EXECUTION                            │
└─────────────────────────────────────────────────────────────────┘

  Trigger Conditions                  Execution Engine
  ┌──────────────┐                   ┌──────────────────────┐
  │ Alert Match  │──┐                │                      │
  ├──────────────┤  │                │  ┌────────────────┐  │
  │ Metric       │──┼───────────────▶│  │ Step 1: Check  │  │
  │ Threshold    │  │   Trigger      │  │ Prerequisites  │  │
  ├──────────────┤  │                │  └───────┬────────┘  │
  │ Schedule     │──┤                │          │           │
  ├──────────────┤  │                │  ┌───────▼────────┐  │
  │ Manual       │──┘                │  │ Step 2: Execute│  │
  └──────────────┘                   │  │ Actions        │  │
                                     │  └───────┬────────┘  │
                                     │          │           │
                                     │  ┌───────▼────────┐  │
  Approval Flow (if required)        │  │ Step 3: Verify │  │
  ┌──────────────┐                   │  │ Results        │  │
  │ Pending      │──▶ Approve ──▶    │  └───────┬────────┘  │
  │ Approval     │      │            │          │           │
  └──────────────┘      ▼            │  ┌───────▼────────┐  │
                   ┌──────────┐      │  │ Step 4: Notify │  │
                   │ Execute  │──────│  │ & Log          │  │
                   └──────────┘      │  └────────────────┘  │
                                     └──────────────────────┘
```

### 5. AI Prediction Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PREDICTIVE ANALYTICS                          │
└─────────────────────────────────────────────────────────────────┘

  Data Collection                    AI Analysis
  ┌──────────────┐                  ┌──────────────────────┐
  │ Metrics      │──┐               │                      │
  │ History      │  │               │  Pattern Recognition │
  ├──────────────┤  │               │  ┌────────────────┐  │
  │ Alert        │──┼──────────────▶│  │ Time Series    │  │
  │ Patterns     │  │               │  │ Analysis       │  │
  ├──────────────┤  │               │  └────────────────┘  │
  │ Incident     │──┤               │  ┌────────────────┐  │
  │ History      │  │               │  │ Anomaly        │  │
  ├──────────────┤  │               │  │ Detection      │  │
  │ Resource     │──┘               │  └────────────────┘  │
  │ Utilization  │                  │  ┌────────────────┐  │
  └──────────────┘                  │  │ Trend          │  │
                                    │  │ Forecasting    │  │
                                    │  └────────────────┘  │
                                    └──────────┬───────────┘
                                               │
                                               ▼
  Predictions Output                ┌──────────────────────┐
  ┌──────────────────────────────┐  │  Action Triggers     │
  │ Capacity Warning (3-5 days)  │──│  ┌────────────────┐  │
  │ Performance Risk (1-2 days)  │  │  │ Auto-scale     │  │
  │ Failure Prediction (7 days)  │  │  │ Alert Team     │  │
  │ Security Expiry (14 days)    │  │  │ Create Ticket  │  │
  └──────────────────────────────┘  │  └────────────────┘  │
                                    └──────────────────────┘
```

## Data Models

### Core Entities

```
┌─────────────────────────────────────────────────────────────────┐
│                       ENTITY RELATIONSHIPS                       │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
  │ Organization │◀─────▶│    User      │◀─────▶│    Team      │
  │              │  1:N  │              │  N:M  │              │
  │ - id         │       │ - id         │       │ - id         │
  │ - name       │       │ - email      │       │ - name       │
  │ - settings   │       │ - role       │       │ - type       │
  └──────────────┘       │ - org_id     │       │ - on_call    │
         │               └──────────────┘       └──────────────┘
         │                      │
         │                      │
         ▼                      ▼
  ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
  │   Incident   │◀─────▶│    Alert     │       │   Playbook   │
  │              │  1:N  │              │       │              │
  │ - id         │       │ - id         │       │ - id         │
  │ - title      │       │ - source     │       │ - name       │
  │ - status     │       │ - severity   │       │ - trigger    │
  │ - priority   │       │ - status     │       │ - steps      │
  │ - ai_data    │       │ - ai_corr    │       │ - is_active  │
  └──────────────┘       └──────────────┘       └──────────────┘
         │
         │
         ▼
  ┌──────────────┐       ┌──────────────┐
  │  AuditLog    │       │ Notification │
  │              │       │              │
  │ - id         │       │ - id         │
  │ - action     │       │ - type       │
  │ - entity     │       │ - message    │
  │ - user_id    │       │ - read       │
  │ - timestamp  │       │ - user_id    │
  └──────────────┘       └──────────────┘
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register organization + admin |
| POST | `/api/v1/auth/login` | Login and get JWT tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user profile |

### Incidents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/incidents` | List incidents with filters |
| POST | `/api/v1/incidents` | Create new incident |
| GET | `/api/v1/incidents/{id}` | Get incident details |
| PUT | `/api/v1/incidents/{id}` | Update incident |
| POST | `/api/v1/incidents/{id}/acknowledge` | Acknowledge incident |
| POST | `/api/v1/incidents/{id}/resolve` | Resolve incident |

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/alerts` | List alerts |
| POST | `/api/v1/alerts/webhook` | Ingest alert via webhook |
| POST | `/api/v1/alerts/{id}/acknowledge` | Acknowledge alert |
| POST | `/api/v1/alerts/correlate` | Correlate alerts |

### AI Services
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/ai/status` | AI service health |
| POST | `/api/v1/ai/incidents/{id}/classify` | Classify incident |
| POST | `/api/v1/ai/incidents/{id}/suggest` | Get resolution suggestions |
| POST | `/api/v1/ai/alerts/correlate` | Correlate alerts with AI |

### WebSocket
| Endpoint | Description |
|----------|-------------|
| `/ws/notifications` | Real-time notifications |
| `/ws/incidents` | Live incident updates |
| `/ws/alerts` | Live alert stream |

## Security Measures

1. **Authentication**: JWT with short-lived access tokens
2. **Authorization**: Role-based access control (Admin/Operator/Viewer)
3. **Data Protection**: All passwords hashed with bcrypt
4. **API Security**: Rate limiting, CORS, input validation
5. **Audit Trail**: All actions logged with user/timestamp

## Phase Summary

| Phase | Features |
|-------|----------|
| **Phase 1** | Auth, Incidents, Alerts, Organizations, Teams |
| **Phase 2** | AI Classification, Resolution Suggestions, Alert Correlation |
| **Phase 3** | Real-time WebSocket, Notifications, Analytics, Audit Logs |
