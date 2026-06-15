import json
from pathlib import Path
from haversine import haversine, Unit

DETECTION_RADIUS_M = 600
ELEVATION_TOLERANCE_M = 80


def _load_builtin_cols():
    data_path = Path(__file__).parent.parent / "data" / "cols_europe.json"
    with open(data_path) as f:
        return json.load(f)


BUILTIN_COLS = _load_builtin_cols()


def detect_cols_in_track(trackpoints: list[dict], db_cols: list[dict]) -> list[int]:
    """
    trackpoints: list of {lat, lng, ele}
    db_cols: list of {id, latitude, longitude, altitude}
    Returns list of col IDs that appear in the track.
    """
    detected = []
    for col in db_cols:
        col_pos = (col["latitude"], col["longitude"])
        col_alt = col["altitude"]
        for pt in trackpoints:
            pt_pos = (pt["lat"], pt["lng"])
            dist = haversine(col_pos, pt_pos, unit=Unit.METERS)
            ele_diff = abs(pt.get("ele", 0) - col_alt)
            if dist <= DETECTION_RADIUS_M and ele_diff <= ELEVATION_TOLERANCE_M:
                detected.append(col["id"])
                break
    return detected


def compute_segment_stats(trackpoints: list[dict], col_lat: float, col_lng: float) -> dict:
    """Compute distance, duration, avg speed, avg gradient for the climb segment leading to col."""
    if len(trackpoints) < 2:
        return {"distance_km": 0, "duration_seconds": 0, "avg_speed_kmh": 0, "avg_gradient_pct": 0, "elevation_gain_m": 0}

    col_pos = (col_lat, col_lng)

    # Find index of closest point to col
    closest_idx = min(
        range(len(trackpoints)),
        key=lambda i: haversine(col_pos, (trackpoints[i]["lat"], trackpoints[i]["lng"]), unit=Unit.METERS)
    )

    # Look back up to 200 points to find start of climb
    segment_end = closest_idx
    segment_start = max(0, closest_idx - 200)

    segment = trackpoints[segment_start:segment_end + 1]
    if len(segment) < 2:
        segment = trackpoints

    total_dist = 0
    total_gain = 0
    for i in range(1, len(segment)):
        p1 = (segment[i - 1]["lat"], segment[i - 1]["lng"])
        p2 = (segment[i]["lat"], segment[i]["lng"])
        total_dist += haversine(p1, p2, unit=Unit.METERS)
        ele_diff = segment[i].get("ele", 0) - segment[i - 1].get("ele", 0)
        if ele_diff > 0:
            total_gain += ele_diff

    dist_km = total_dist / 1000

    # Duration from timestamps if available
    duration = 0
    if "time" in segment[0] and "time" in segment[-1]:
        try:
            from datetime import datetime
            t0 = datetime.fromisoformat(segment[0]["time"])
            t1 = datetime.fromisoformat(segment[-1]["time"])
            duration = int((t1 - t0).total_seconds())
        except Exception:
            duration = 0

    avg_speed = (dist_km / (duration / 3600)) if duration > 0 else 0
    avg_gradient = (total_gain / total_dist * 100) if total_dist > 0 else 0

    return {
        "distance_km": round(dist_km, 2),
        "duration_seconds": duration,
        "avg_speed_kmh": round(avg_speed, 2),
        "avg_gradient_pct": round(avg_gradient, 2),
        "elevation_gain_m": int(total_gain),
    }
