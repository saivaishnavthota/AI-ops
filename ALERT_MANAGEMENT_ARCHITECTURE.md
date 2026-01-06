# Alert Management System - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         External Monitoring Tools                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Prometheus│  │ Grafana  │  │ Datadog  │  │PagerDuty │  │  Custom  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼────────┘
        │             │             │             │             │
        │ Webhooks    │             │             │             │
        └─────────────┴─────────────┴─────────────┴─────────────┘
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────────┐
        │         Webhook Ingestion Layer (Public API)          │
        │  POST /api/v1/alerts/webhooks/ingest/{endpoint_id}    │
        │  • Signature Verification                             │
        │  • Source Type Detection                              │
        │  • Field Normalization                                │
        └───────────────────┬───────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────────────────────┐
        │           Alert Management Service                     │
        │                                                        │
        │  ┌──────────────────────────────────────────────┐    │
        │  │ 1. Normalize Alert Data                      │    │
        │  │    • Map fields from different sources       │    │
        │  │    • Standardize severity levels             │    │
        │  └──────────────────┬───────────────────────────┘    │
        │                     ▼                                  │
        │  ┌──────────────────────────────────────────────┐    │
        │  │ 2. Generate Fingerprint                      │    │
        │  │    • SHA-256(title+source+service+env+tags)  │    │
        │  └──────────────────┬───────────────────────────┘    │
        │                     ▼                                  │
        │  ┌──────────────────────────────────────────────┐    │
        │  │ 3. Check for Duplicates                      │    │
        │  │    • Search by fingerprint (24h window)      │    │
        │  │    • Update occurrence count if found        │    │
        │  └──────────────────┬───────────────────────────┘    │
        │                     ▼                                  │
        │  ┌──────────────────────────────────────────────┐    │
        │  │ 4. Apply Suppression Rules                   │    │
        │  │    • Match criteria                          │    │
        │  │    • Check schedule                          │    │
        │  │    • Suppress if conditions met              │    │
        │  └──────────────────┬───────────────────────────┘    │
        │                     ▼                                  │
        │  ┌──────────────────────────────────────────────┐    │
        │  │ 5. AI-Powered Correlation                    │    │
        │  │    • TF-IDF text similarity                  │    │
        │  │    • Pattern-based correlation               │    │
        │  │    • Create correlation links                │    │
        │  └──────────────────┬───────────────────────────┘    │
        │                     ▼                                  │
        │  ┌──────────────────────────────────────────────┐    │
        │  │ 6. Check Auto-Conversion Rules               │    │
        │  │    • Critical severity → Incident            │    │
        │  │    • 3+ correlations → Incident              │    │
        │  │    • Custom rules                            │    │
        │  └──────────────────┬───────────────────────────┘    │
        └────────────────────┼────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────────────────┐
        │                  AI Service                             │
        │                                                         │
        │  ┌─────────────────────────────────────────────────┐  │
        │  │ find_similar_alerts()                           │  │
        │  │  • Extract text features (TF-IDF)               │  │
        │  │  • Calculate cosine similarity                  │  │
        │  │  • Filter by threshold (0.8)                    │  │
        │  │  • Return similar alerts with scores            │  │
        │  └─────────────────────────────────────────────────┘  │
        │                                                         │
        │  ┌─────────────────────────────────────────────────┐  │
        │  │ correlate_alerts_by_pattern()                   │  │
        │  │  • Same service + environment                   │  │
        │  │  • Same host                                    │  │
        │  │  • Temporal cascading (5 min window)            │  │
        │  └─────────────────────────────────────────────────┘  │
        │                                                         │
        │  ┌─────────────────────────────────────────────────┐  │
        │  │ detect_alert_anomalies()                        │  │
        │  │  • Alert spike detection                        │  │
        │  │  • New source detection                         │  │
        │  │  • Pattern changes                              │  │
        │  └─────────────────────────────────────────────────┘  │
        └────────────────────────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────────────────┐
        │                    Database Layer                       │
        │                                                         │
        │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
        │  │    alerts    │  │alert_        │  │alert_       │ │
        │  │              │  │correlations  │  │deduplications│ │
        │  └──────────────┘  └──────────────┘  └─────────────┘ │
        │                                                         │
        │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
        │  │alert_        │  │alert_        │  │alert_       │ │
        │  │correlation_  │  │suppression_  │  │webhook_     │ │
        │  │rules         │  │rules         │  │endpoints    │ │
        │  └──────────────┘  └──────────────┘  └─────────────┘ │
        │                                                         │
        │  ┌──────────────┐                                      │
        │  │alert_        │                                      │
        │  │incident_     │                                      │
        │  │conversions   │                                      │
        │  └──────────────┘                                      │
        └────────────────────────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────────────────┐
        │                   API Layer (REST)                      │
        │                                                         │
        │  GET    /api/v1/alerts                                 │
        │  POST   /api/v1/alerts                                 │
        │  GET    /api/v1/alerts/stats                           │
        │  POST   /api/v1/alerts/{id}/convert-to-incident        │
        │  GET    /api/v1/alerts/{id}/correlations               │
        │  GET    /api/v1/alerts/webhooks/endpoints              │
        │  POST   /api/v1/alerts/webhooks/endpoints              │
        │  GET    /api/v1/alerts/suppression-rules               │
        │  POST   /api/v1/alerts/suppression-rules               │
        │  GET    /api/v1/alerts/correlation-rules               │
        │  POST   /api/v1/alerts/correlation-rules               │
        └────────────────────┬───────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────────────────┐
        │                  Frontend (React)                       │
        │                                                         │
        │  ┌──────────────────────────────────────────────────┐ │
        │  │         AlertManagementPage Component            │ │
        │  │                                                  │ │
        │  │  ┌────────────┐  ┌────────────┐  ┌──────────┐  │ │
        │  │  │   Active   │  │Correlations│  │ Webhooks │  │ │
        │  │  │   Alerts   │  │            │  │          │  │ │
        │  │  └────────────┘  └────────────┘  └──────────┘  │ │
        │  │                                                  │ │
        │  │  ┌────────────┐  ┌────────────────────────────┐ │ │
        │  │  │   Rules    │  │    Statistics Dashboard    │ │ │
        │  │  │            │  │                            │ │ │
        │  │  └────────────┘  └────────────────────────────┘ │ │
        │  └──────────────────────────────────────────────────┘ │
        └────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
Alert Ingestion Flow:
═══════════════════

External Tool → Webhook → Normalize → Fingerprint → Duplicate Check
                                                            │
                                                            ├─→ Existing? → Update Count
                                                            │
                                                            └─→ New? → Create Alert
                                                                        │
                                                                        ▼
                                                                 Suppression Check
                                                                        │
                                                                        ├─→ Suppress? → Mark Suppressed
                                                                        │
                                                                        └─→ Active? → AI Correlation
                                                                                           │
                                                                                           ▼
                                                                                    Auto-Convert Check
                                                                                           │
                                                                                           ├─→ Critical? → Create Incident
                                                                                           │
                                                                                           └─→ Store Alert
```

## AI Correlation Process

```
Alert Correlation Flow:
═══════════════════════

New Alert
    │
    ▼
Extract Features
    │
    ├─→ Title
    ├─→ Description
    ├─→ Service
    ├─→ Environment
    └─→ Tags
    │
    ▼
TF-IDF Vectorization
    │
    ├─→ Create feature matrix
    └─→ Apply term weighting
    │
    ▼
Similarity Calculation
    │
    ├─→ Cosine similarity with recent alerts
    └─→ Filter by threshold (0.8)
    │
    ▼
Pattern Detection
    │
    ├─→ Same service + environment
    ├─→ Same host
    └─→ Temporal proximity (5 min)
    │
    ▼
Create Correlations
    │
    └─→ Link related alerts
```

## Deduplication Algorithm

```
Deduplication Flow:
═══════════════════

New Alert
    │
    ▼
Generate Fingerprint
    │
    └─→ SHA-256(title + source + service + environment + tags)
    │
    ▼
Search Existing Alerts
    │
    └─→ WHERE fingerprint = ? AND created_at > NOW() - 24h
    │
    ├─→ Found? ──────────────┐
    │                        │
    │                        ▼
    │                   Update Existing
    │                        │
    │                        ├─→ occurrence_count++
    │                        ├─→ last_occurrence = NOW()
    │                        └─→ raw_data = latest
    │                        │
    │                        ▼
    │                   Track Deduplication
    │                        │
    │                        └─→ alert_deduplications table
    │
    └─→ Not Found? ──────────┐
                             │
                             ▼
                        Create New Alert
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                    Component Interaction                     │
└─────────────────────────────────────────────────────────────┘

Frontend                Backend                  Database
   │                       │                         │
   │  GET /alerts          │                         │
   ├──────────────────────>│                         │
   │                       │  SELECT * FROM alerts   │
   │                       ├────────────────────────>│
   │                       │<────────────────────────┤
   │<──────────────────────┤                         │
   │                       │                         │
   │  POST /webhooks       │                         │
   ├──────────────────────>│                         │
   │                       │  INSERT webhook         │
   │                       ├────────────────────────>│
   │                       │<────────────────────────┤
   │<──────────────────────┤                         │
   │                       │                         │
   │                       │  Webhook POST           │
   │                       │<────────────────────────┤ External
   │                       │                         │
   │                       │  Process Alert          │
   │                       │  • Normalize            │
   │                       │  • Deduplicate          │
   │                       │  • Correlate (AI)       │
   │                       │  • Suppress             │
   │                       │                         │
   │                       │  INSERT/UPDATE alert    │
   │                       ├────────────────────────>│
   │                       │<────────────────────────┤
   │                       │                         │
   │  WebSocket Update     │                         │
   │<──────────────────────┤                         │
   │                       │                         │
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      Technology Stack                        │
└─────────────────────────────────────────────────────────────┘

Frontend:
  • React 18
  • Material-UI (MUI)
  • TypeScript
  • Redux Toolkit / RTK Query

Backend:
  • FastAPI (Python)
  • SQLAlchemy (ORM)
  • Pydantic (Validation)
  • Alembic (Migrations)

AI/ML:
  • scikit-learn (TF-IDF, Cosine Similarity)
  • NumPy (Numerical Operations)
  • Pandas (Data Processing)

Database:
  • PostgreSQL
  • JSONB for flexible data
  • UUID for IDs
  • Indexes for performance

Security:
  • HMAC-SHA256 for webhook signatures
  • JWT for API authentication
  • Role-based access control
```

## Performance Optimizations

```
┌─────────────────────────────────────────────────────────────┐
│                   Performance Features                       │
└─────────────────────────────────────────────────────────────┘

1. Indexing Strategy:
   • fingerprint (B-tree index)
   • created_at (B-tree index)
   • organization_id (B-tree index)
   • severity, status, source (B-tree indexes)

2. Query Optimization:
   • 24-hour time window for deduplication
   • Limit correlation search to recent alerts
   • Use JSONB indexes for tag queries

3. Caching:
   • Cache correlation rules
   • Cache suppression rules
   • Cache webhook endpoints

4. Async Processing:
   • Background tasks for AI correlation
   • Async webhook processing
   • Batch updates for statistics

5. Database Optimization:
   • Connection pooling
   • Prepared statements
   • Batch inserts for correlations
```

---

**Architecture Version**: 1.0
**Last Updated**: January 5, 2026
