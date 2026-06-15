from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from ..database import get_db
from ..models import Col, Ascent
from ..schemas import ColOut, AscentsOut

router = APIRouter(prefix="/cols", tags=["cols"])


@router.get("/", response_model=list[ColOut])
async def list_cols(
    min_altitude: int = Query(0),
    max_altitude: int = Query(9999),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Col).where(Col.altitude >= min_altitude, Col.altitude <= max_altitude)
    )
    cols = result.scalars().all()

    out = []
    for col in cols:
        ascents = (await db.execute(
            select(Ascent).where(Ascent.col_id == col.id).order_by(Ascent.date.desc())
        )).scalars().all()
        out.append(ColOut(
            id=col.id,
            name=col.name,
            latitude=col.latitude,
            longitude=col.longitude,
            altitude=col.altitude,
            country=col.country,
            ascent_count=len(ascents),
            last_ascent=ascents[0].date if ascents else None,
        ))
    return out


@router.get("/ascents/all", response_model=list[AscentsOut])
async def all_ascents(
    date_from: datetime = Query(None),
    date_to: datetime = Query(None),
    min_altitude: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    q = select(Ascent).join(Col).where(Col.altitude >= min_altitude)
    if date_from:
        q = q.where(Ascent.date >= date_from)
    if date_to:
        q = q.where(Ascent.date <= date_to)
    q = q.order_by(Ascent.date.desc())

    result = await db.execute(q)
    ascents = result.scalars().all()

    out = []
    for a in ascents:
        col = await db.get(Col, a.col_id)
        out.append(AscentsOut(
            id=a.id, col_id=a.col_id, col_name=col.name,
            col_latitude=col.latitude, col_longitude=col.longitude, col_altitude=col.altitude,
            activity_id=a.activity_id, source=a.source, date=a.date,
            distance_km=a.distance_km, duration_seconds=a.duration_seconds,
            avg_speed_kmh=a.avg_speed_kmh, avg_gradient_pct=a.avg_gradient_pct,
            elevation_gain_m=a.elevation_gain_m, activity_name=a.activity_name,
            polyline=a.polyline,
        ))
    return out


@router.get("/{col_id}/ascents", response_model=list[AscentsOut])
async def list_ascents(
    col_id: int,
    date_from: datetime = Query(None),
    date_to: datetime = Query(None),
    db: AsyncSession = Depends(get_db)
):
    q = select(Ascent).where(Ascent.col_id == col_id)
    if date_from:
        q = q.where(Ascent.date >= date_from)
    if date_to:
        q = q.where(Ascent.date <= date_to)
    q = q.order_by(Ascent.date.desc())

    result = await db.execute(q)
    ascents = result.scalars().all()
    col = await db.get(Col, col_id)

    return [
        AscentsOut(
            id=a.id,
            col_id=col_id,
            col_name=col.name,
            col_latitude=col.latitude,
            col_longitude=col.longitude,
            col_altitude=col.altitude,
            activity_id=a.activity_id,
            source=a.source,
            date=a.date,
            distance_km=a.distance_km,
            duration_seconds=a.duration_seconds,
            avg_speed_kmh=a.avg_speed_kmh,
            avg_gradient_pct=a.avg_gradient_pct,
            elevation_gain_m=a.elevation_gain_m,
            activity_name=a.activity_name,
            polyline=a.polyline,
        )
        for a in ascents
    ]
