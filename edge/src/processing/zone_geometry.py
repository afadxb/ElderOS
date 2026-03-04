"""Bed-zone polygon geometry for spatial event detection.

Uses a ray-casting point-in-polygon algorithm to determine if keypoints
(e.g., pelvis center) are inside or outside a defined bed zone.
Polygon vertices are defined in normalized coordinates (0.0-1.0) relative
to frame dimensions, making them resolution-independent.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float


def point_in_polygon(point: Point, polygon: list[Point]) -> bool:
    """Ray-casting algorithm for point-in-polygon test.

    Args:
        point: The test point.
        polygon: List of vertices defining a closed polygon (minimum 3).

    Returns:
        True if point is inside the polygon.
    """
    n = len(polygon)
    if n < 3:
        return False

    inside = False
    j = n - 1
    for i in range(n):
        pi = polygon[i]
        pj = polygon[j]

        if ((pi.y > point.y) != (pj.y > point.y)) and (
            point.x < (pj.x - pi.x) * (point.y - pi.y) / (pj.y - pi.y) + pi.x
        ):
            inside = not inside
        j = i

    return inside


class BedZone:
    """Represents a bed zone polygon for a single room.

    Vertices are stored in normalized coordinates (0.0-1.0).
    All point tests accept either normalized or pixel coordinates.
    """

    def __init__(
        self,
        room_id: str,
        vertices: list[tuple[float, float]],
        label: str = "bed",
    ) -> None:
        """
        Args:
            room_id: Room identifier this zone belongs to.
            vertices: List of (x, y) tuples in normalized coords (0.0-1.0).
            label: Human-readable label for this zone.
        """
        self.room_id = room_id
        self.label = label
        self._vertices_norm = [Point(x, y) for x, y in vertices]

    @property
    def vertices(self) -> list[Point]:
        return list(self._vertices_norm)

    def contains_normalized(self, x: float, y: float) -> bool:
        """Test if a normalized-coordinate point is inside the bed zone."""
        return point_in_polygon(Point(x, y), self._vertices_norm)

    def contains_pixel(
        self, px: float, py: float, frame_width: int, frame_height: int
    ) -> bool:
        """Test if a pixel-coordinate point is inside the bed zone.

        Converts pixel coordinates to normalized before testing.
        """
        if frame_width <= 0 or frame_height <= 0:
            return False
        nx = px / frame_width
        ny = py / frame_height
        return self.contains_normalized(nx, ny)


class ZoneManager:
    """Manages bed zones for all rooms."""

    def __init__(self) -> None:
        self._zones: dict[str, BedZone] = {}

    def add_zone(self, zone: BedZone) -> None:
        self._zones[zone.room_id] = zone

    def get_zone(self, room_id: str) -> BedZone | None:
        return self._zones.get(room_id)

    def has_zone(self, room_id: str) -> bool:
        return room_id in self._zones

    @classmethod
    def from_config(cls, cameras_config: list[dict]) -> "ZoneManager":
        """Build ZoneManager from the cameras section of sensors.yaml.

        Expects each camera dict to optionally include:
            bed_zone:
              vertices: [[x1,y1], [x2,y2], ...]
              label: "bed"  # optional
        """
        manager = cls()
        for cam in cameras_config:
            zone_data = cam.get("bed_zone")
            if zone_data and zone_data.get("vertices"):
                zone = BedZone(
                    room_id=cam["room_id"],
                    vertices=[tuple(v) for v in zone_data["vertices"]],
                    label=zone_data.get("label", "bed"),
                )
                manager.add_zone(zone)
        return manager
