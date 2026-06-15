import garth
import tempfile
import os
from datetime import datetime, date
from pathlib import Path
from ..config import settings

SESSION_FILE = Path("/tmp/garmin_session")


def _get_client():
    client = garth.Client()
    if SESSION_FILE.exists():
        client.load(str(SESSION_FILE))
    return client


async def connect(email: str = None, password: str = None) -> str:
    """Authenticate with Garmin Connect. Returns serialized session."""
    email = email or settings.garmin_email
    password = password or settings.garmin_password

    client = garth.Client()
    client.login(email, password)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        fname = f.name

    client.dump(fname)
    session_data = Path(fname).read_text()
    os.unlink(fname)

    return session_data


def load_client_from_session(session_json: str) -> garth.Client:
    client = garth.Client()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(session_json)
        fname = f.name
    client.load(fname)
    os.unlink(fname)
    return client


async def fetch_activities(session_json: str, start_date: date = None) -> list[dict]:
    client = load_client_from_session(session_json)

    activities = []
    start = 0
    limit = 100

    cycling_types = {"cycling", "road_biking", "gravel_cycling", "mountain_biking", "virtual_ride"}

    while True:
        batch = client.connectapi(
            "/activitylist-service/activities/search/activities",
            params={"start": start, "limit": limit}
        )
        if not batch:
            break

        for act in batch:
            act_type = act.get("activityType", {}).get("typeKey", "").lower()
            if act_type not in cycling_types:
                continue

            act_date_str = act.get("startTimeLocal", "")
            if start_date and act_date_str:
                act_date = datetime.fromisoformat(act_date_str[:10]).date()
                if act_date < start_date:
                    continue

            activities.append({
                "id": str(act.get("activityId")),
                "name": act.get("activityName", ""),
                "date": act_date_str,
                "distance": act.get("distance", 0),
                "duration": act.get("duration", 0),
                "elevation_gain": act.get("elevationGain", 0),
                "avg_speed": act.get("averageSpeed", 0),
            })

        if len(batch) < limit:
            break
        start += limit

    return activities


async def get_activity_gps(session_json: str, activity_id: str) -> list[dict]:
    client = load_client_from_session(session_json)

    try:
        data = client.connectapi(f"/activity-service/activity/{activity_id}/details")
    except Exception:
        return []

    trackpoints = []

    gps_data = data.get("geoPolylineDTO", {})
    polyline_points = gps_data.get("polyline", [])

    for pt in polyline_points:
        trackpoints.append({
            "lat": pt.get("lat", 0),
            "lng": pt.get("lon", 0),
            "ele": pt.get("altitude", 0),
        })

    return trackpoints
