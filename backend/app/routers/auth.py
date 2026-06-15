from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import SyncState
from ..config import settings
from ..services import strava as strava_svc
from ..services import garmin as garmin_svc
import logging

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.get("/strava/login")
async def strava_login():
    redirect_uri = f"{settings.backend_url}/auth/strava/callback"
    url = strava_svc.get_authorization_url(redirect_uri)
    return RedirectResponse(url)


@router.get("/strava/callback")
async def strava_callback(code: str, db: AsyncSession = Depends(get_db)):
    tokens = await strava_svc.exchange_code(code)

    state = await db.scalar(select(SyncState).where(SyncState.source == "strava"))
    if not state:
        state = SyncState(source="strava")
        db.add(state)

    state.strava_access_token = tokens["access_token"]
    state.strava_refresh_token = tokens["refresh_token"]
    state.strava_token_expires_at = tokens["expires_at"]
    await db.commit()

    return RedirectResponse(f"{settings.frontend_url}?connected=strava")


@router.get("/strava/status")
async def strava_status(db: AsyncSession = Depends(get_db)):
    state = await db.scalar(select(SyncState).where(SyncState.source == "strava"))
    return {"connected": bool(state and state.strava_access_token), "last_sync": state.last_sync if state else None}


@router.post("/garmin/connect")
async def garmin_connect(email: str, password: str, db: AsyncSession = Depends(get_db)):
    try:
        session = await garmin_svc.connect(email, password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    state = await db.scalar(select(SyncState).where(SyncState.source == "garmin"))
    if not state:
        state = SyncState(source="garmin")
        db.add(state)
    state.garmin_session = session
    await db.commit()
    return {"connected": True}


@router.get("/garmin/status")
async def garmin_status(db: AsyncSession = Depends(get_db)):
    state = await db.scalar(select(SyncState).where(SyncState.source == "garmin"))
    return {"connected": bool(state and state.garmin_session), "last_sync": state.last_sync if state else None}
