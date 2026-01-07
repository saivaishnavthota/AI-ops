# Audit Logging Coverage Report

## Current Status (January 7, 2026)

### ✅ Currently Logged Actions

Based on database analysis:

| Action | Resource Type | Count | Status |
|--------|---------------|-------|--------|
| login | auth | 2 | ✅ Working |
| login_failed | auth | 1 | ✅ Working |
| logout | user | 7 | ⚠️ Old format |
| update | user | 14 | ✅ From seed data |
| update | incident | 13 | ✅ From seed data |
| execute | playbook | 12 | ✅ From seed data |
| resolve | alert | 11 | ✅ From seed data |
| create | alert | 9 | ✅ From seed data |
| create | incident | 8 | ✅ From seed data |
| assign | incident | 7 | ✅ From seed data |
| create | user | 7 | ✅ From seed data |
| login | user | 7 | ⚠️ Old format |
| update | settings | 7 | ✅ From seed data |
| update | team | 6 | ✅ From seed data |
| acknowledge | alert | 4 | ✅ From seed data |

### ❌ Missing Audit Logging

#### Critical Endpoints (Need Immediate Logging)

**Incidents:**
- ❌ Create incident (real-time)
- ❌ Update incident (real-time)
- ❌ Delete incident
- ❌ Assign incident (real-time)
- ❌ Resolve incident (real-time)
- ❌ Close incident
- ❌ Add comment

**Alerts:**
- ❌ Create alert (real-time)
- ❌ Update alert
- ❌ Delete alert
- ❌ Acknowledge alert (real-time)
- ❌ Resolve alert (real-time)

**Users:**
- ❌ Create user (real-time)
- ❌ Update user (real-time)
- ❌ Delete user
- ❌ Activate user
- ❌ Deactivate user
- ❌ Change role

**Teams:**
- ❌ Create team
- ❌ Update team (real-time from seed)
- ❌ Delete team
- ❌ Add member
- ❌ Remove member
- ❌ Update member role

**Playbooks:**
- ❌ Create playbook
- ❌ Update playbook
- ❌ Delete playbook
- ❌ Execute playbook (real-time)

**Tickets:**
- ❌ Create ticket
- ❌ Update ticket
- ❌ Delete ticket
- ❌ Assign ticket
- ❌ Resolve ticket
- ❌ Add comment

**Predictions:**
- ❌ Create prediction
- ❌ Update prediction
- ❌ Delete prediction
- ❌ Take action
- ❌ Dismiss

**Cloud Resources:**
- ❌ Create resource
- ❌ Update resource
- ❌ Delete resource
- ❌ Start resource
- ❌ Stop resource

**Security Events:**
- ❌ Create event
- ❌ Update event
- ❌ Delete event
- ❌ Investigate

**Investigations:**
- ❌ Create investigation
- ❌ Update investigation
- ❌ Close investigation

**Knowledge Base:**
- ❌ Create article
- ❌ Update article
- ❌ Delete article
- ❌ Mark helpful

**Organizations:**
- ❌ Update settings
- ❌ Update features
- ❌ Update subscription

**Notifications:**
- ❌ Mark as read
- ❌ Delete notification

## Recommended Implementation Plan

### Phase 1: Critical Actions (High Priority)
**Timeline:** Immediate

1. **Authentication** ✅ DONE
   - login
   - login_failed
   - logout

2. **Incidents**
   - create
   - update
   - assign
   - resolve
   - close

3. **Alerts**
   - acknowledge
   - resolve

4. **Users**
   - create
   - update
   - delete
   - change_role

### Phase 2: Important Actions (Medium Priority)
**Timeline:** Next sprint

1. **Teams**
   - create
   - update
   - delete
   - add_member
   - remove_member

2. **Playbooks**
   - create
   - update
   - delete
   - execute

3. **Tickets**
   - create
   - update
   - assign
   - resolve

### Phase 3: Additional Actions (Lower Priority)
**Timeline:** Future

1. **Predictions**
2. **Cloud Resources**
3. **Security Events**
4. **Investigations**
5. **Knowledge Base**
6. **Notifications**

## Implementation Approach

### Option 1: Manual Addition (Current)
**Pros:**
- Full control over what's logged
- Can customize per endpoint
- Clear and explicit

**Cons:**
- Time-consuming
- Easy to miss endpoints
- Requires updating each endpoint

### Option 2: Middleware/Decorator (Recommended)
**Pros:**
- Automatic logging for all endpoints
- Consistent implementation
- Easy to maintain

**Cons:**
- Less control over details
- May log unnecessary actions
- Requires careful configuration

### Option 3: Hybrid Approach (Best)
**Pros:**
- Automatic logging for standard CRUD
- Manual logging for complex actions
- Balance of automation and control

**Cons:**
- Requires initial setup
- Need to maintain both systems

## Audit Log Utility Created

**File:** `backend/app/utils/audit_logger.py`

**Functions:**
- `log_action()` - Generic logging
- `log_create()` - Create actions
- `log_update()` - Update actions
- `log_delete()` - Delete actions
- `log_assign()` - Assignment actions
- `log_resolve()` - Resolution actions
- `log_execute()` - Execution actions
- `log_acknowledge()` - Acknowledgment actions
- `log_close()` - Close actions
- `log_activate()` - Activation actions
- `log_deactivate()` - Deactivation actions

**Usage Example:**
```python
from app.utils.audit_logger import log_create

# In endpoint
@router.post("", response_model=IncidentResponse)
async def create_incident(
    data: IncidentCreate,
    current_user: CurrentUser,
    db: DBSession,
    request: Request,
):
    # Create incident
    incident = await service.create_incident(data)
    
    # Log action
    await log_create(
        db=db,
        user=current_user,
        resource_type="incident",
        resource_id=str(incident.id),
        resource_name=incident.title,
        request=request,
    )
    
    return incident
```

## Testing Audit Logging

### Manual Test
1. Perform an action (e.g., create incident)
2. Go to Settings > Audit Log
3. Verify the action appears
4. Check all details are correct

### Automated Test
```python
# Test script
async def test_audit_logging():
    # Perform action
    response = await client.post("/api/v1/incidents", json=data)
    
    # Check audit log
    logs = await client.get("/api/v1/audit-logs?resource_type=incident")
    assert logs[0]["action"] == "create"
    assert logs[0]["resource_id"] == response["id"]
```

## Monitoring Audit Log Coverage

### Query to Check Coverage
```sql
-- Get action counts by resource type
SELECT 
    resource_type,
    action,
    COUNT(*) as count,
    MAX(created_at) as last_occurrence
FROM audit_logs
GROUP BY resource_type, action
ORDER BY resource_type, count DESC;
```

### Expected Actions Per Resource

**Incident:**
- create, update, delete, assign, resolve, close, comment

**Alert:**
- create, update, delete, acknowledge, resolve

**User:**
- create, update, delete, activate, deactivate, change_role

**Team:**
- create, update, delete, add_member, remove_member, update_member

**Playbook:**
- create, update, delete, execute

**Ticket:**
- create, update, delete, assign, resolve, comment

## Next Steps

1. ✅ Create audit logging utility
2. ⏳ Add logging to incident endpoints
3. ⏳ Add logging to alert endpoints
4. ⏳ Add logging to user endpoints
5. ⏳ Add logging to team endpoints
6. ⏳ Add logging to playbook endpoints
7. ⏳ Add logging to ticket endpoints
8. ⏳ Test all audit logging
9. ⏳ Document all logged actions
10. ⏳ Create monitoring dashboard

## Estimated Effort

- **Phase 1 (Critical):** 4-6 hours
- **Phase 2 (Important):** 3-4 hours
- **Phase 3 (Additional):** 4-6 hours
- **Total:** 11-16 hours

## Priority Recommendation

**Immediate Action Required:**
1. Add audit logging to incident create/update/assign/resolve
2. Add audit logging to user create/update/delete/change_role
3. Add audit logging to alert acknowledge/resolve

These are the most critical user actions that need to be tracked for security and compliance.

---

**Report Generated:** January 7, 2026
**Status:** Audit logging utility created, implementation in progress
