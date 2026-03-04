from enum import StrEnum


class Permission(StrEnum):
    """All application permissions. Values mirror the frontend permission strings exactly."""

    # Vision - Alerts
    ALERTS_VIEW = "vision:alerts:view"
    ALERTS_ACKNOWLEDGE = "vision:alerts:acknowledge"
    ALERTS_RESOLVE = "vision:alerts:resolve"

    # Vision - Rooms
    ROOMS_VIEW = "vision:rooms:view"

    # Vision - Incidents
    INCIDENTS_VIEW = "vision:incidents:view"
    INCIDENTS_EXPORT = "vision:incidents:export"

    # Vision - Review
    REVIEW_VIEW = "vision:review:view"
    REVIEW_TRIAGE = "vision:review:triage"

    # Vision - Residents
    RESIDENTS_VIEW = "vision:residents:view"

    # Vision - Clips
    CLIPS_REQUEST = "vision:clips:request"
    CLIPS_VIEW = "vision:clips:view"

    # Vision - Reports
    REPORTS_VIEW = "vision:reports:view"
    REPORTS_BOARD = "vision:reports:board"

    # Vision - Call Bell
    CALLBELL_VIEW = "vision:callbell:view"
    CALLBELL_RESPOND = "vision:callbell:respond"
    CALLBELL_ANALYTICS = "vision:callbell:analytics"

    # Platform - System
    SYSTEM_VIEW = "platform:system:view"
    SYSTEM_MANAGE = "platform:system:manage"

    # Platform - Settings
    SETTINGS_VIEW = "platform:settings:view"
    SETTINGS_MANAGE = "platform:settings:manage"


# ---------------------------------------------------------------------------
# Role -> Permission mappings
# Each higher clinical role inherits from the one below it.
# Executive and Admin are independent role definitions.
# ---------------------------------------------------------------------------

_PSW_PERMISSIONS: frozenset[Permission] = frozenset(
    {
        Permission.ALERTS_VIEW,
        Permission.ALERTS_ACKNOWLEDGE,
        Permission.ALERTS_RESOLVE,
        Permission.ROOMS_VIEW,
        Permission.INCIDENTS_VIEW,
        Permission.RESIDENTS_VIEW,
        Permission.CALLBELL_VIEW,
        Permission.CALLBELL_RESPOND,
    }
)

_NURSE_PERMISSIONS: frozenset[Permission] = _PSW_PERMISSIONS | frozenset(
    {
        Permission.INCIDENTS_EXPORT,
        Permission.REPORTS_VIEW,
    }
)

_SUPERVISOR_PERMISSIONS: frozenset[Permission] = _NURSE_PERMISSIONS | frozenset(
    {
        Permission.REVIEW_VIEW,
        Permission.REVIEW_TRIAGE,
        Permission.CLIPS_REQUEST,
        Permission.CLIPS_VIEW,
        Permission.CALLBELL_ANALYTICS,
    }
)

_EXECUTIVE_PERMISSIONS: frozenset[Permission] = frozenset(
    {
        Permission.ROOMS_VIEW,
        Permission.INCIDENTS_VIEW,
        Permission.INCIDENTS_EXPORT,
        Permission.RESIDENTS_VIEW,
        Permission.REPORTS_VIEW,
        Permission.REPORTS_BOARD,
        Permission.CALLBELL_VIEW,
        Permission.CALLBELL_ANALYTICS,
    }
)

_ADMIN_PERMISSIONS: frozenset[Permission] = frozenset(
    {
        Permission.ALERTS_VIEW,
        Permission.ROOMS_VIEW,
        Permission.INCIDENTS_VIEW,
        Permission.SYSTEM_VIEW,
        Permission.SYSTEM_MANAGE,
        Permission.SETTINGS_VIEW,
        Permission.SETTINGS_MANAGE,
    }
)

ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "psw": _PSW_PERMISSIONS,
    "nurse": _NURSE_PERMISSIONS,
    "supervisor": _SUPERVISOR_PERMISSIONS,
    "executive": _EXECUTIVE_PERMISSIONS,
    "admin": _ADMIN_PERMISSIONS,
}


def role_has_permission(role: str, permission: Permission) -> bool:
    """Check whether a role includes a specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def role_has_all_permissions(role: str, permissions: set[Permission]) -> bool:
    """Check whether a role includes all of the given permissions."""
    role_perms = ROLE_PERMISSIONS.get(role, frozenset())
    return permissions.issubset(role_perms)
