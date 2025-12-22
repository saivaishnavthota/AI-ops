from enum import Enum
from typing import List


class Permission(str, Enum):
    """Available permissions in the system."""

    # Organization
    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"

    # Users
    USERS_READ = "users:read"
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"

    # Teams
    TEAMS_READ = "teams:read"
    TEAMS_CREATE = "teams:create"
    TEAMS_UPDATE = "teams:update"
    TEAMS_DELETE = "teams:delete"

    # Incidents
    INCIDENTS_READ = "incidents:read"
    INCIDENTS_CREATE = "incidents:create"
    INCIDENTS_UPDATE = "incidents:update"
    INCIDENTS_DELETE = "incidents:delete"
    INCIDENTS_ASSIGN = "incidents:assign"
    INCIDENTS_RESOLVE = "incidents:resolve"

    # Alerts
    ALERTS_READ = "alerts:read"
    ALERTS_CREATE = "alerts:create"
    ALERTS_UPDATE = "alerts:update"
    ALERTS_DELETE = "alerts:delete"
    ALERTS_ACKNOWLEDGE = "alerts:acknowledge"
    ALERTS_SUPPRESS = "alerts:suppress"

    # Playbooks
    PLAYBOOKS_READ = "playbooks:read"
    PLAYBOOKS_CREATE = "playbooks:create"
    PLAYBOOKS_UPDATE = "playbooks:update"
    PLAYBOOKS_DELETE = "playbooks:delete"
    PLAYBOOKS_EXECUTE = "playbooks:execute"
    PLAYBOOKS_APPROVE = "playbooks:approve"

    # Settings
    SETTINGS_READ = "settings:read"
    SETTINGS_UPDATE = "settings:update"

    # Integrations
    INTEGRATIONS_READ = "integrations:read"
    INTEGRATIONS_CREATE = "integrations:create"
    INTEGRATIONS_UPDATE = "integrations:update"
    INTEGRATIONS_DELETE = "integrations:delete"

    # Audit
    AUDIT_READ = "audit:read"


# Role-based permission mapping
ROLE_PERMISSIONS = {
    "super_admin": [p.value for p in Permission],  # All permissions
    "admin": [p.value for p in Permission],  # All permissions
    "operator": [
        Permission.ORG_READ.value,
        Permission.USERS_READ.value,
        Permission.TEAMS_READ.value,
        Permission.INCIDENTS_READ.value,
        Permission.INCIDENTS_CREATE.value,
        Permission.INCIDENTS_UPDATE.value,
        Permission.INCIDENTS_ASSIGN.value,
        Permission.INCIDENTS_RESOLVE.value,
        Permission.ALERTS_READ.value,
        Permission.ALERTS_ACKNOWLEDGE.value,
        Permission.ALERTS_SUPPRESS.value,
        Permission.PLAYBOOKS_READ.value,
        Permission.PLAYBOOKS_EXECUTE.value,
        Permission.SETTINGS_READ.value,
        Permission.INTEGRATIONS_READ.value,
    ],
    "viewer": [
        Permission.ORG_READ.value,
        Permission.USERS_READ.value,
        Permission.TEAMS_READ.value,
        Permission.INCIDENTS_READ.value,
        Permission.ALERTS_READ.value,
        Permission.PLAYBOOKS_READ.value,
        Permission.SETTINGS_READ.value,
    ],
}


def get_permissions_for_role(role: str) -> List[str]:
    """Get list of permissions for a role."""
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(role: str, permission: str, additional_permissions: List[str] = None) -> bool:
    """Check if a role has a specific permission."""
    role_perms = get_permissions_for_role(role)
    all_perms = set(role_perms)

    if additional_permissions:
        all_perms.update(additional_permissions)

    return permission in all_perms
