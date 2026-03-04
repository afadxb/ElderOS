"""Bed-zone polygon calibration tool.

Grabs a frame from an RTSP camera (or loads an image file), lets the user
click to define a polygon, and saves the normalized vertices to a JSON file
or pushes them to the ElderOS backend API.

Usage:
    # From live camera
    python -m src.tools.zone_calibrator --camera cam-101

    # From a saved image
    python -m src.tools.zone_calibrator --image snapshot.jpg --room room-101

    # Push result to backend API instead of saving locally
    python -m src.tools.zone_calibrator --camera cam-101 --push

Controls:
    Left-click   : Add vertex
    Right-click   : Remove last vertex
    R             : Reset all vertices
    S             : Save and exit
    Q / ESC       : Quit without saving
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import yaml


# ---------------------------------------------------------------------------
# Globals for mouse callback
# ---------------------------------------------------------------------------

_vertices: list[tuple[int, int]] = []
_frame: np.ndarray | None = None
_window_name = "ElderOS Zone Calibrator"


def _mouse_callback(event, x, y, flags, param):
    global _vertices
    if event == cv2.EVENT_LBUTTONDOWN:
        _vertices.append((x, y))
    elif event == cv2.EVENT_RBUTTONDOWN and _vertices:
        _vertices.pop()


def _draw_overlay(frame: np.ndarray) -> np.ndarray:
    """Draw the polygon and vertices on the frame."""
    overlay = frame.copy()

    if len(_vertices) >= 3:
        pts = np.array(_vertices, dtype=np.int32).reshape((-1, 1, 2))
        cv2.fillPoly(overlay, [pts], (0, 180, 0, 80))
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, overlay)
        cv2.polylines(overlay, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
    elif len(_vertices) == 2:
        cv2.line(overlay, _vertices[0], _vertices[1], (0, 255, 0), 2)

    for i, (x, y) in enumerate(_vertices):
        cv2.circle(overlay, (x, y), 6, (0, 0, 255), -1)
        cv2.putText(overlay, str(i + 1), (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Instructions
    h = overlay.shape[0]
    instructions = [
        "L-Click: add point | R-Click: undo | R: reset",
        "S: save & exit | Q/ESC: quit",
        f"Vertices: {len(_vertices)}",
    ]
    for i, text in enumerate(instructions):
        cv2.putText(overlay, text, (10, h - 10 - (len(instructions) - 1 - i) * 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return overlay


# ---------------------------------------------------------------------------
# Frame acquisition
# ---------------------------------------------------------------------------

def grab_frame_from_rtsp(rtsp_url: str) -> np.ndarray:
    """Grab a single frame from an RTSP stream."""
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open RTSP stream: {rtsp_url}")

    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError(f"Failed to grab frame from: {rtsp_url}")
    return frame


def load_camera_config(camera_id: str, config_dir: str = "./config") -> dict:
    """Load a specific camera config from sensors.yaml."""
    sensors_path = Path(config_dir) / "sensors.yaml"
    if not sensors_path.exists():
        raise FileNotFoundError(f"sensors.yaml not found at {sensors_path}")

    with open(sensors_path) as f:
        data = yaml.safe_load(f) or {}

    for cam in data.get("cameras", []):
        if cam["id"] == camera_id:
            return cam

    raise ValueError(f"Camera '{camera_id}' not found in sensors.yaml")


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def normalize_vertices(
    vertices: list[tuple[int, int]], width: int, height: int
) -> list[list[float]]:
    """Convert pixel coordinates to normalized 0.0-1.0 coordinates."""
    return [
        [round(x / width, 4), round(y / height, 4)]
        for x, y in vertices
    ]


def save_zone_local(
    room_id: str, vertices_norm: list[list[float]], output_dir: str = "./config/zones"
) -> str:
    """Save zone vertices to a local JSON file."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / f"{room_id}.json"

    zone_data = {
        "room_id": room_id,
        "label": "bed",
        "vertices": vertices_norm,
    }

    with open(file_path, "w") as f:
        json.dump(zone_data, f, indent=2)

    return str(file_path)


def push_zone_to_backend(
    room_id: str,
    vertices_norm: list[list[float]],
    backend_url: str = "http://localhost:8000",
    api_key: str = "edge-device-shared-secret",
) -> bool:
    """Push zone vertices to the ElderOS backend API."""
    import requests

    url = f"{backend_url}/api/rooms/{room_id}/zone"
    payload = {"label": "bed", "vertices": vertices_norm}
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    try:
        resp = requests.put(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to push zone to backend: {e}")
        return False


# ---------------------------------------------------------------------------
# Main calibration loop
# ---------------------------------------------------------------------------

def run_calibrator(
    frame: np.ndarray,
    room_id: str,
    push: bool = False,
    backend_url: str = "http://localhost:8000",
    api_key: str = "edge-device-shared-secret",
) -> list[list[float]] | None:
    """Run the interactive zone calibration GUI.

    Returns normalized vertices on save, or None if cancelled.
    """
    global _vertices, _frame
    _vertices = []
    _frame = frame
    h, w = frame.shape[:2]

    cv2.namedWindow(_window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(_window_name, min(w, 1280), min(h, 720))
    cv2.setMouseCallback(_window_name, _mouse_callback)

    print(f"\nCalibrating bed zone for room: {room_id}")
    print(f"Frame size: {w}x{h}")
    print("Click to draw the bed-zone polygon. Minimum 3 points.\n")

    result = None

    while True:
        display = _draw_overlay(frame)
        cv2.imshow(_window_name, display)

        key = cv2.waitKey(30) & 0xFF

        if key == ord("q") or key == 27:  # Q or ESC
            print("Cancelled.")
            break

        elif key == ord("r"):
            _vertices.clear()
            print("Reset vertices.")

        elif key == ord("s"):
            if len(_vertices) < 3:
                print("Need at least 3 vertices to save.")
                continue

            vertices_norm = normalize_vertices(_vertices, w, h)
            print(f"\nNormalized vertices ({len(vertices_norm)} points):")
            for i, v in enumerate(vertices_norm):
                print(f"  {i + 1}: [{v[0]}, {v[1]}]")

            if push:
                ok = push_zone_to_backend(room_id, vertices_norm, backend_url, api_key)
                if ok:
                    print(f"Zone pushed to backend for room {room_id}")
                else:
                    # Fallback to local save
                    path = save_zone_local(room_id, vertices_norm)
                    print(f"Backend push failed. Saved locally: {path}")
            else:
                path = save_zone_local(room_id, vertices_norm)
                print(f"Zone saved: {path}")

            result = vertices_norm
            break

    cv2.destroyAllWindows()
    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ElderOS Bed-Zone Calibration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--camera", help="Camera ID from sensors.yaml (grabs live frame)")
    group.add_argument("--image", help="Path to a saved image file")

    parser.add_argument("--room", help="Room ID (required if using --image)")
    parser.add_argument("--config-dir", default="./config", help="Config directory")
    parser.add_argument("--push", action="store_true", help="Push to backend API")
    parser.add_argument("--backend-url", default="http://localhost:8000")
    parser.add_argument("--api-key", default="edge-device-shared-secret")

    args = parser.parse_args()

    if args.camera:
        cam_config = load_camera_config(args.camera, args.config_dir)
        room_id = cam_config["room_id"]
        print(f"Grabbing frame from {cam_config['rtsp_url']}...")
        frame = grab_frame_from_rtsp(cam_config["rtsp_url"])
    elif args.image:
        if not args.room:
            parser.error("--room is required when using --image")
        room_id = args.room
        frame = cv2.imread(args.image)
        if frame is None:
            print(f"Error: Cannot load image: {args.image}")
            sys.exit(1)
    else:
        parser.error("Either --camera or --image is required")

    run_calibrator(
        frame=frame,
        room_id=room_id,
        push=args.push,
        backend_url=args.backend_url,
        api_key=args.api_key,
    )


if __name__ == "__main__":
    main()
