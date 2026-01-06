# Alert Management System - Implementation Guide

## Overview

This document describes the comprehensive Alert Management system with AI-powered features including:

- **Multi-source alert ingestion** via webhooks
- **Intelligent deduplication** using fingerprinting
- **AI-powered alert correlation** using ML similarity
- **Alert suppression** with time-based expiry
- **Convert alerts to incidents** automatically or manually

## Architecture

### Backend Components

#### 1. Models (`backend/app/models/alert_enhancement.py`)

New database models:

- **AlertCorrelationRule**: Rules for correlating related alerts
- **AlertSuppressionRule**: Rules for suppressing noisy alerts
- **AlertWebhookEndpoint**: Webhook endpoints for ingesting alerts
- **AlertDeduplication**: Tracking of deduplicated alerts
- **AlertToIncidentConversion**: Tracking alert-to-incident conversions

#### 2. Services

**AlertManagementService** (`backend/app/services/alert_management.py`):
- `ingest_alert()`: Main entry point for alert ingestion
- `_normalize_alert_data()`: Normalize alerts from different sources
- `_generate_alert_fingerprint()`: Generate unique fingerprint for deduplication
- `_find_duplicate_alert()`: Find existing duplicate alerts
- `_should_suppress_alert()`: Check suppression rules
- `_correlate_alert()`: Perform AI-powered correlation
- `convert_alert_to_incident()`: Convert alert to incident
- `get_alert_statistics()`: Get comprehensive statistics

**AIService** (`backend/app/services/ai_service.py`):
- `find_similar_alerts()`: AI-powered similarity detection using TF-IDF
- `correlate_alerts_by_pattern()`: Pattern-based correlation
- `predict_alert_severity()`: ML-based severity prediction
- `detect_alert_anomalies()`: Anomaly detection in alert patterns

#### 3. API Endpoints

Enhanced `/api/v1/alerts` endpoints:

```python
GET    /alerts                          # List alerts with advanced filtering
GET    /alerts/stats                    # Get comprehensive statistics
POST   /alerts                          # Create alert (with intelligent processing)
GET    /alerts/{id}                     # Get alert details
PUT    /alerts/{id}                     # Update alert
DELETE /alerts/{id}                     # Delete alert
POST   /alerts/{id}/convert-to-incident # Convert to incident
GET    /alerts/{id}/correlations        # Get correlated alerts

# Webhook Management
GET    /alerts/webhooks/endpoints       # List webhook endpoints
POST   /alerts/webhooks/endpoints       # Create webhook endpoint
POST   /alerts/webhooks/ingest/{id}     # Webhook ingestion (public)

# Rule Management
GET    /alerts/suppression-rules        # List suppression rules
POST   /alerts/suppression-rules        # Create suppression rule
GET    /alerts/correlation-rules        # List correlation rules
POST   /alerts/correlation-rules        # Create correlation rule
```

#### 4. Schemas (`backend/app/schemas/alert_enhancement.py`)

Pydantic schemas for:
- Webhook endpoints (create, update, response)
- Suppression rules (create, update, response)
- Correlation rules (create, update, response)
- Deduplication tracking
- Alert-to-incident conversions

### Frontend Components

#### AlertManagementPage (`frontend/src/features/alerts/pages/AlertManagementPage.tsx`)

React component with 4 main tabs:

1. **Active Alerts**: View and manage all alerts
   - Filter by severity, status, source, service, environment
   - Acknowledge, suppress, or convert to incident
   - View occurrence counts and deduplication info

2. **Correlations**: View AI-powered alert correlations
   - See grouped related alerts
   - Identify root cause alerts
   - Understand correlation patterns

3. **Webhooks**: Manage webhook endpoints
   - Add webhooks for Prometheus, Grafana, Datadog, PagerDuty, etc.
   - View webhook statistics
   - Copy webhook URLs

4. **Rules**: Configure correlation and suppression rules
   - Create AI-powered correlation rules
   - Set up time-based suppression rules
   - Manage rule priorities

## Features in Detail

### 1. Multi-Source Alert Ingestion

Supports webhooks from:
- **Prometheus**: AlertManager webhook format
- **Grafana**: Grafana alerting webhook
- **Datadog**: Datadog webhook integration
- **PagerDuty**: PagerDuty webhook events
- **Generic**: Custom webhook format

**Example Webhook Setup:**

```bash
# Create webhook endpoint
POST /api/v1/alerts/webhooks/endpoints
{
  "name": "Prometheus Production",
  "source_type": "prometheus",
  "description": "Production cluster alerts",
  "secret_token": "your-secret-token"
}

# Response includes webhook URL
{
  "id": "uuid",
  "endpoint_url": "/api/v1/alerts/webhooks/ingest/abc123xyz",
  ...
}

# Configure Prometheus AlertManager
receivers:
  - name: 'aiops-platform'
    webhook_configs:
      - url: 'https://your-domain.com/api/v1/alerts/webhooks/ingest/abc123xyz'
        send_resolved: true
        http_config:
          headers:
            X-Signature: 'sha256=...'
```

### 2. Intelligent Deduplication

Alerts are deduplicated using:
- **Fingerprinting**: SHA-256 hash of key fields (title, source, service, environment, tags)
- **Time window**: 24-hour window for duplicate detection
- **Occurrence counting**: Track how many times alert fired
- **Update strategy**: Update existing alert instead of creating duplicate

**Example:**
```
Alert 1: "High CPU on web-server-1" (10:00 AM)
Alert 2: "High CPU on web-server-1" (10:05 AM) <- Deduplicated
Alert 3: "High CPU on web-server-1" (10:10 AM) <- Deduplicated

Result: Single alert with occurrence_count=3
```

### 3. AI-Powered Alert Correlation

Uses machine learning to find related alerts:

**TF-IDF Similarity**:
- Extracts text features from alert title, description, tags
- Calculates cosine similarity between alerts
- Groups alerts with similarity > threshold (default 0.8)

**Pattern-Based Correlation**:
- Same service + environment
- Same host
- Temporal cascading (alerts within 5 minutes)

**Example Correlation:**
```
Alert A: "Database connection timeout" (service: api, env: prod)
Alert B: "API response time high" (service: api, env: prod)
Alert C: "User login failures" (service: web, env: prod)

Correlation: A ↔ B (high similarity, same service)
             B ↔ C (temporal, cascading failure)
```

### 4. Alert Suppression

Time-based suppression with flexible rules:

**Suppression Rule Example:**
```json
{
  "name": "Suppress low severity during business hours",
  "criteria": {
    "severity": "low",
    "environment": "production"
  },
  "suppression_duration": 3600,  // 1 hour
  "schedule": {
    "days": ["mon", "tue", "wed", "thu", "fri"],
    "hours": ["09:00-17:00"]
  }
}
```

**Features:**
- Match by severity, source, service, environment
- Time-based schedules (days of week, hours)
- Max occurrences before suppression
- Automatic expiry after duration

### 5. Convert Alerts to Incidents

**Automatic Conversion:**
- Critical severity alerts
- Alerts with 3+ correlations
- Custom rule-based conversion

**Manual Conversion:**
- User-initiated from UI
- Preserves alert context
- Links alert to incident

**Example:**
```python
# Automatic conversion for critical alerts
if alert.severity == "critical":
    incident = convert_alert_to_incident(
        alert_id=alert.id,
        method="automatic"
    )

# Manual conversion
POST /api/v1/alerts/{alert_id}/convert-to-incident
{
  "title": "Production Database Outage",
  "severity": "critical",
  "assigned_team_id": "team-uuid"
}
```

## Database Schema

### New Tables

```sql
-- Alert Correlation Rules
CREATE TABLE alert_correlation_rules (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255),
    criteria JSONB,
    use_ai_correlation BOOLEAN DEFAULT TRUE,
    similarity_threshold FLOAT DEFAULT 0.8,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 1,
    correlation_count INTEGER DEFAULT 0,
    last_triggered TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Alert Suppression Rules
CREATE TABLE alert_suppression_rules (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255),
    criteria JSONB,
    suppression_duration INTEGER,
    max_occurrences INTEGER DEFAULT 1,
    schedule JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    suppressed_count INTEGER DEFAULT 0,
    last_triggered TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Alert Webhook Endpoints
CREATE TABLE alert_webhook_endpoints (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255),
    endpoint_url VARCHAR(500) UNIQUE,
    secret_token VARCHAR(255),
    source_type VARCHAR(100),
    source_config JSONB,
    field_mapping JSONB,
    filters JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    alerts_received INTEGER DEFAULT 0,
    last_alert_received TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Alert Deduplications
CREATE TABLE alert_deduplications (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    primary_alert_id UUID REFERENCES alerts(id),
    duplicate_alert_id UUID REFERENCES alerts(id),
    similarity_score FLOAT,
    deduplication_method VARCHAR(100),
    deduplication_criteria JSONB,
    created_at TIMESTAMP WITH TIME ZONE
);

-- Alert to Incident Conversions
CREATE TABLE alert_incident_conversions (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    alert_id UUID REFERENCES alerts(id),
    incident_id UUID REFERENCES incidents(id),
    conversion_method VARCHAR(100),
    conversion_rule_id UUID,
    converted_by_id UUID REFERENCES users(id),
    conversion_context JSONB,
    created_at TIMESTAMP WITH TIME ZONE
);
```

### Updated Alert Table

```sql
ALTER TABLE alerts ADD COLUMN description TEXT;
ALTER TABLE alerts ADD COLUMN environment VARCHAR(100);
ALTER TABLE alerts ADD COLUMN external_id VARCHAR(255);
ALTER TABLE alerts ADD COLUMN raw_data JSONB;
ALTER TABLE alerts ADD COLUMN first_occurrence TIMESTAMP WITH TIME ZONE;
ALTER TABLE alerts ADD COLUMN last_occurrence TIMESTAMP WITH TIME ZONE;
ALTER TABLE alerts ADD COLUMN resolved_by_id UUID REFERENCES users(id);
```

## Installation & Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Key new dependencies:
- `scikit-learn`: For AI/ML features
- `numpy`: For numerical operations
- `pandas`: For data processing

### 2. Run Database Migration

```bash
cd backend
alembic upgrade head
```

### 3. Configure Environment

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/aiops
OPENAI_API_KEY=your-key  # Optional, for advanced AI features
```

### 4. Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

## Usage Examples

### Example 1: Setup Prometheus Webhook

```bash
# 1. Create webhook endpoint
curl -X POST http://localhost:8000/api/v1/alerts/webhooks/endpoints \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prometheus Production",
    "source_type": "prometheus",
    "secret_token": "my-secret-123"
  }'

# 2. Configure Prometheus AlertManager
# alertmanager.yml
receivers:
  - name: 'aiops'
    webhook_configs:
      - url: 'http://your-domain/api/v1/alerts/webhooks/ingest/abc123'
```

### Example 2: Create Suppression Rule

```bash
curl -X POST http://localhost:8000/api/v1/alerts/suppression-rules \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Suppress test environment low alerts",
    "criteria": {
      "severity": "low",
      "environment": "test"
    },
    "suppression_duration": 7200,
    "max_occurrences": 5
  }'
```

### Example 3: Create Correlation Rule

```bash
curl -X POST http://localhost:8000/api/v1/alerts/correlation-rules \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Correlate same service alerts",
    "criteria": {
      "fields": ["service", "environment"],
      "time_window": 300
    },
    "use_ai_correlation": true,
    "similarity_threshold": 0.75,
    "priority": 10
  }'
```

## Testing

### Test Alert Ingestion

```bash
# Send test alert via webhook
curl -X POST http://localhost:8000/api/v1/alerts/webhooks/ingest/abc123 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Alert",
    "description": "This is a test alert",
    "severity": "high",
    "source": "test",
    "service": "api",
    "environment": "production",
    "tags": {"team": "platform"}
  }'
```

### Test Deduplication

```bash
# Send same alert twice - should deduplicate
curl -X POST http://localhost:8000/api/v1/alerts/webhooks/ingest/abc123 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "High CPU Usage",
    "service": "web-server",
    "environment": "production"
  }'

# Check occurrence_count should be 2
curl http://localhost:8000/api/v1/alerts?service=web-server
```

## Performance Considerations

1. **Deduplication**: Uses indexed fingerprint field for fast lookups
2. **Correlation**: Limited to 24-hour time window to reduce search space
3. **AI Similarity**: Uses TF-IDF with max 100 features for efficiency
4. **Caching**: Consider caching correlation rules and suppression rules
5. **Async Processing**: Use background tasks for heavy AI operations

## Monitoring

Track these metrics:
- Alert ingestion rate
- Deduplication rate (% of alerts deduplicated)
- Correlation accuracy
- Suppression effectiveness
- Alert-to-incident conversion rate
- Webhook endpoint health

## Future Enhancements

1. **Advanced ML Models**: Train custom models on historical data
2. **Root Cause Analysis**: Automatically identify root cause alerts
3. **Predictive Alerting**: Predict future alerts based on patterns
4. **Alert Routing**: Intelligent routing to teams based on context
5. **Integration Hub**: More monitoring tool integrations
6. **Alert Enrichment**: Automatic context enrichment from external sources

## Troubleshooting

### Alerts not being deduplicated
- Check fingerprint generation logic
- Verify time window settings
- Review alert field consistency

### Correlation not working
- Check similarity threshold (try lowering to 0.6-0.7)
- Verify alerts have sufficient text content
- Check time window settings

### Webhook not receiving alerts
- Verify endpoint URL is correct
- Check secret token configuration
- Review webhook endpoint logs
- Test with curl first

### Suppression not working
- Verify suppression rule criteria matches alerts
- Check schedule configuration
- Ensure rule is active

## Support

For issues or questions:
- Check logs: `backend/logs/app.log`
- Review API documentation: `http://localhost:8000/docs`
- Database queries: Check `alert_deduplications` and `alert_correlations` tables

## License

MIT License - See LICENSE file for details
