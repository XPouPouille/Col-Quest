import httpx
from datetime import datetime, timezone
from ..config import settings
from ..models import SyncState

STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_URL = "https://www.strava.com/api/v3"
SCOPES = "read,activity:read_all"


def get_authorization_url(redirect_uri: str) -> str:
    params = {
        "client_id": settings.strava_client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "approval_prompt": "auto",
        "scope": SCOPES,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{STRAVA_AUTH_URL}?{query}"


async def exchange_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(STRAVA_TOKEN_URL, data={
            "client_id": settings.strava_client_id,
            "client_secret": settings.strava_client_secret,
            "code": code,
            "grant_type": "authorization_code",
        })
        resp.raise_for_status()
        return resp.json()


async def refresh_token(refresh_token_str: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(STRAVA_TOKEN_URL, data={
            "client_id": settings.strava_client_id,
            "client_secret": settings.strava_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token_str,
        })
        resp.raise_for_status()
        return resp.json()


async def get_valid_token(state: SyncState) -> str:
    now = int(datetime.now(timezone.utc).timestamp())
    if state.strava_token_expires_at - now < 300:
        tokens = await refresh_token(state.strava_refresh_token)
        state.strava_access_token = tokens["access_token"]
        state.strava_refresh_token = tokens["refresh_token"]
        state.strava_token_expires_at = tokens["expires_at"]
    return state.strava_access_token


async def fetch_activities(access_token: str, after: int = 0) -> list[dict]:
    activities = []
    page = 1
    async with httpx.AsyncClient() as client:
        while True:
            resp = await client.get(
                f"{STRAVA_API_URL}/athlete/activities",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"after": after, "per_page": 100, "page": page},
            )
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break
            # Only cycling activities
            cycling = [a for a in batch if a.get("type") in ("Ride", "VirtualRide", "GravelRide", "MountainBikeRide")]
            activities.extend(cycling)
            if len(batch) < 100:
                break
            page += 1
    return activities


async def get_activity_streams(access_token: str, activity_id: int) -> list[dict]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{STRAVA_API_URL}/activities/{activity_id}/streams",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"keys": "latlng,altitude,time", "key_by_type": "true"},
        )
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        data = resp.json()

    latlng = data.get("latlng", {}).get("data", [])
    altitude = data.get("altitude", {}).get("data", [])
    time_data = data.get("time", {}).get("data", [])

    trackpoints = []
    for i, ll in enumerate(latlng):
        pt = {"lat": ll[0], "lng": ll[1]}
        if i < len(altitude):
            pt["ele"] = altitude[i]
        if i < len(time_data):
            pt["time_offset"] = time_data[i]
        trackpoints.append(pt)
    return trackpoints


async def get_activity_polyline(access_token: str, activity_id: int) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{STRAVA_API_URL}/activities/{activity_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        data = resp.json()
    return data.get("map", {}).get("summary_polyline", "")
