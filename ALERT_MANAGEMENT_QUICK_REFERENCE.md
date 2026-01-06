# Alert Management - Quick Reference Card

## 🚀 Quick Setup (3 Steps)

```bash
# 1. Install dependencies
cd backend && pip install scikit-learn numpy pandas

# 2. Run migration
alembic upgrade head

# 3. Start services
uvicorn app.main:app --reload
```

## 📡 Webhook Setup

### Create Endpoint
```bash
POST /api/v1/alerts/webhooks/endpoints
{
  "name": "Prometheus Prod",
  "source_type": "prometheus",
  "secret_token": "secret123"
}
```

### Configure Prometheus
```yaml
receivers:
  - name: 'aiops'
    webhook_configs:
      - url: 'http://domain/api/v1/alerts/webhooks/ingest/{id}'
```

### Configure Grafana
```json
{
  "url": "http://domain/api/v1/alerts/webhooks/ingest/{id}",
  "httpMethod": "POST"
}
```

## 🔧 Common API Calls

### List Alerts
```bash
GET /api/v1/alerts?severity=critical&status=open&environment=production
```

### Get Statistics
```bash
GET /api/v1/alerts/stats
```

### Convert to Incident
```bash
POST /api/v1/alerts/{id}/convert-to-incident
```

### Get Correlations
```bash
GET /api/v1/alerts/{id}/correlations
```

## 📋 Create Rules

### Correlation Rule
```json
POST /api/v1/alerts/correlation-rules
{
  "name": "Same Service Correlation",
  "criteria": {
    "fields": ["service", "environment"],
    "time_window": 300
  },
  "use_ai_correlation": true,
  "similarity_threshold": 0.75
}
```

### Suppression Rule
```json
POST /api/v1/alerts/suppression-rules
{
  "name": "Suppress Low Severity",
  "criteria": {
    "severity": "low",
    "environment": "test"
  },
  "suppression_duration": 3600,
  "max_occurrences": 5
}
```

## 🎯 Key Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Deduplication** | SHA-256 fingerprinting | 60-80% noise reduction |
| **AI Correlation** | TF-IDF similarity | Faster root cause identification |
| **Suppression** | Time-based rules | Reduce alert fatigue |
| **Auto-Incident** | Critical alert conversion | Faster response |
| **Multi-Source** | 5+ integrations | Unified alert view |

## 📊 Statistics Available

```javascript
{
  total_alerts: 1234,
  open_alerts: 45,
  critical_alerts: 8,
  alerts_today: 156,
  alerts_this_week: 892,
  suppressed_alerts: 234,
  converted_to_incidents: 12,
  deduplicated_alerts: 567,
  correlated_alerts: 89
}
```

## 🔍 Filtering Options

```
?severity=critical,high
?status=open,acknowledged
?source=prometheus
?service=api-server
?environment=production
?include_suppressed=true
```

## 🎨 UI Tabs

1. **Active Alerts** - View/manage all alerts
2. **Correlations** - AI-powered grouping
3. **Webhooks** - Manage endpoints
4. **Rules** - Configure correlation/suppression

## 🧪 Test Alert

```bash
curl -X POST http://localhost:8000/api/v1/alerts/webhooks/ingest/{id} \
  -H "Content-Type: application/json" \
  -d '{
    "title": "High CPU Usage",
    "severity": "high",
    "source": "test",
    "service": "web-server",
    "environment": "production",
    "tags": {"host": "server-01"}
  }'
```

## 🗄️ Database Tables

- `alert_correlation_rules` - Correlation configuration
- `alert_suppression_rules` - Suppression configuration
- `alert_webhook_endpoints` - Webhook endpoints
- `alert_deduplications` - Deduplication tracking
- `alert_incident_conversions` - Conversion tracking

## 🔐 Webhook Security

```python
# Signature verification
X-Signature: sha256=<hmac_sha256(body, secret)>
```

## 📈 Performance Tips

1. Use indexed fields for filtering
2. Set appropriate time windows (default: 24h)
3. Adjust similarity threshold (0.6-0.9)
4. Enable caching for rules
5. Use background tasks for heavy operations

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Alerts not deduplicating | Check fingerprint fields consistency |
| Correlation not working | Lower similarity threshold to 0.6-0.7 |
| Webhook failing | Verify endpoint URL and secret token |
| Suppression not working | Check rule criteria and schedule |

## 📞 Support

- Docs: `ALERT_MANAGEMENT_IMPLEMENTATION.md`
- API: `http://localhost:8000/docs`
- Logs: `backend/logs/app.log`

## 🎯 Supported Sources

- ✅ Prometheus
- ✅ Grafana
- ✅ Datadog
- ✅ PagerDuty
- ✅ Generic (custom)

## 💡 Best Practices

1. Start with generic webhooks for testing
2. Configure suppression rules for noisy alerts
3. Use AI correlation with 0.75-0.85 threshold
4. Set up automatic incident conversion for critical alerts
5. Monitor deduplication rate to tune fingerprinting
6. Review correlation accuracy regularly

---

**Quick Links:**
- Full Docs: `ALERT_MANAGEMENT_IMPLEMENTATION.md`
- Summary: `ALERT_MANAGEMENT_SUMMARY.md`
- Setup: `setup_alert_management.sh`
