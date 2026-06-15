from datetime import datetime
from pydantic import BaseModel


class AscentsOut(BaseModel):
    id: int
    col_id: int
    col_name: str
    col_latitude: float
    col_longitude: float
    col_altitude: int
    activity_id: str
    source: str
    date: datetime
    distance_km: float
    duration_seconds: int
    avg_speed_kmh: float
    avg_gradient_pct: float
    elevation_gain_m: int
    activity_name: str
    polyline: str

    class Config:
        from_attributes = True


class ColOut(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    altitude: int
    country: str
    ascent_count: int
    last_ascent: datetime | None

    class Config:
        from_attributes = True


class SyncStatus(BaseModel):
    source: str
    last_sync: datetime | None
    connected: bool
