"""Exclusion zone filter.

Rooms or spatial regions that have an active exclusion zone should not
generate events (e.g. during scheduled rehab exercises).  Zone definitions
are pushed from the backend.
"""


class ExclusionFilter:
    def __init__(self, config) -> None:
        self._excluded_rooms: set[str] = set()  # room_ids with active exclusion zones

    def update_zones(self, zones: list[dict]) -> None:
        """Refresh the set of excluded rooms from backend-provided zone data.

        Args:
            zones: List of dicts with at least 'room_id' and 'enabled' keys.
        """
        self._excluded_rooms = {z["room_id"] for z in zones if z.get("enabled")}

    def is_excluded(self, room_id: str, detection) -> bool:
        """Check whether a detection should be suppressed.

        In the full implementation this would also check spatial overlap
        between the detection bounding box and the exclusion zone boundaries.
        For now it is a stub that does not exclude anything -- zones are
        loaded from the backend configuration.
        """
        # Placeholder: spatial overlap check would go here
        return False
