from fastapi import APIRouter, BackgroundTasks
from ..services.scheduler import run_all_syncs, sync_strava, sync_garmin

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/trigger")
async def trigger_sync(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_all_syncs)
    return {"message": "Sync started in background"}


@router.post("/strava")
async def trigger_strava_sync(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_strava)
    return {"message": "Strava sync started"}


@router.post("/garmin")
async def trigger_garmin_sync(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_garmin)
    return {"message": "Garmin sync started"}
