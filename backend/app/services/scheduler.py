from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone
from sqlalchemy import select
from ..database import AsyncSessionLocal
from ..models import SyncState, Col, Ascent
from . import strava as strava_svc
from . import garmin as garmin_svc
from .col_detector import detect_cols_in_track, compute_segment_stats
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def sync_strava():
    logger.info("Starting Strava sync...")
    async with AsyncSessionLocal() as db:
        state = await db.scalar(select(SyncState).where(SyncState.source == "strava"))
        if not state or not state.strava_access_token:
            logger.info("Strava not connected, skipping.")
            return

        access_token = await strava_svc.get_valid_token(state)
        after = int(state.last_sync.timestamp()) if state.last_sync else 0

        activities = await strava_svc.fetch_activities(access_token, after=after)
        cols = (await db.execute(select(Col))).scalars().all()
        cols_data = [{"id": c.id, "latitude": c.latitude, "longitude": c.longitude, "altitude": c.altitude} for c in cols]

        for act in activities:
            act_id = str(act["id"])
            existing = await db.scalar(select(Ascent).where(Ascent.activity_id == act_id))
            if existing:
                continue

            trackpoints = await strava_svc.get_activity_streams(access_token, act["id"])
            if not trackpoints:
                continue

            detected_col_ids = detect_cols_in_track(trackpoints, cols_data)

            summary_polyline = await strava_svc.get_activity_polyline(access_token, act["id"])

            for col_id in detected_col_ids:
                col = next(c for c in cols if c.id == col_id)
                stats = compute_segment_stats(trackpoints, col.latitude, col.longitude)

                unique_id = f"strava_{act_id}_{col_id}"
                existing_ascent = await db.scalar(select(Ascent).where(Ascent.activity_id == unique_id))
                if existing_ascent:
                    continue

                ascent = Ascent(
                    col_id=col_id,
                    activity_id=unique_id,
                    source="strava",
                    date=datetime.fromisoformat(act["start_date_local"].replace("Z", "+00:00")),
                    distance_km=stats["distance_km"],
                    duration_seconds=stats["duration_seconds"] or int(act.get("moving_time", 0)),
                    avg_speed_kmh=stats["avg_speed_kmh"],
                    avg_gradient_pct=stats["avg_gradient_pct"],
                    elevation_gain_m=stats["elevation_gain_m"] or int(act.get("total_elevation_gain", 0)),
                    activity_name=act.get("name", ""),
                    polyline=summary_polyline,
                )
                db.add(ascent)

        state.last_sync = datetime.now(timezone.utc)
        state.strava_access_token = access_token
        await db.commit()
    logger.info("Strava sync complete.")


async def sync_garmin():
    logger.info("Starting Garmin sync...")
    async with AsyncSessionLocal() as db:
        state = await db.scalar(select(SyncState).where(SyncState.source == "garmin"))
        if not state or not state.garmin_session:
            logger.info("Garmin not connected, skipping.")
            return

        since = state.last_sync.date() if state.last_sync else None
        activities = await garmin_svc.fetch_activities(state.garmin_session, since)

        cols = (await db.execute(select(Col))).scalars().all()
        cols_data = [{"id": c.id, "latitude": c.latitude, "longitude": c.longitude, "altitude": c.altitude} for c in cols]

        for act in activities:
            act_id = str(act["id"])
            trackpoints = await garmin_svc.get_activity_gps(state.garmin_session, act_id)
            if not trackpoints:
                continue

            detected_col_ids = detect_cols_in_track(trackpoints, cols_data)

            for col_id in detected_col_ids:
                col = next(c for c in cols if c.id == col_id)
                stats = compute_segment_stats(trackpoints, col.latitude, col.longitude)

                unique_id = f"garmin_{act_id}_{col_id}"
                existing = await db.scalar(select(Ascent).where(Ascent.activity_id == unique_id))
                if existing:
                    continue

                act_date = datetime.fromisoformat(act["date"][:19]) if act["date"] else datetime.now()

                ascent = Ascent(
                    col_id=col_id,
                    activity_id=unique_id,
                    source="garmin",
                    date=act_date,
                    distance_km=stats["distance_km"] or round(act.get("distance", 0) / 1000, 2),
                    duration_seconds=stats["duration_seconds"] or int(act.get("duration", 0)),
                    avg_speed_kmh=stats["avg_speed_kmh"] or round(act.get("avg_speed", 0) * 3.6, 2),
                    avg_gradient_pct=stats["avg_gradient_pct"],
                    elevation_gain_m=stats["elevation_gain_m"] or int(act.get("elevation_gain", 0)),
                    activity_name=act.get("name", ""),
                    polyline="",
                )
                db.add(ascent)

        state.last_sync = datetime.now(timezone.utc)
        await db.commit()
    logger.info("Garmin sync complete.")


async def run_all_syncs():
    await sync_strava()
    await sync_garmin()


def start_scheduler():
    scheduler.add_job(run_all_syncs, CronTrigger(hour=2, minute=0), id="daily_sync", replace_existing=True)
    scheduler.start()
