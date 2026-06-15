from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Col(Base):
    __tablename__ = "cols"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    altitude: Mapped[int] = mapped_column(Integer)  # meters
    country: Mapped[str] = mapped_column(String(100), default="")
    ascents: Mapped[list["Ascent"]] = relationship(back_populates="col", cascade="all, delete-orphan")


class Ascent(Base):
    __tablename__ = "ascents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    col_id: Mapped[int] = mapped_column(ForeignKey("cols.id"))
    col: Mapped["Col"] = relationship(back_populates="ascents")
    activity_id: Mapped[str] = mapped_column(String(100), unique=True)
    source: Mapped[str] = mapped_column(String(20))  # "strava" | "garmin"
    date: Mapped[datetime] = mapped_column(DateTime)
    distance_km: Mapped[float] = mapped_column(Float)
    duration_seconds: Mapped[int] = mapped_column(Integer)
    avg_speed_kmh: Mapped[float] = mapped_column(Float)
    avg_gradient_pct: Mapped[float] = mapped_column(Float)
    elevation_gain_m: Mapped[int] = mapped_column(Integer)
    activity_name: Mapped[str] = mapped_column(String(300), default="")
    polyline: Mapped[str] = mapped_column(Text, default="")


class SyncState(Base):
    __tablename__ = "sync_state"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(20), unique=True)
    last_sync: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    strava_access_token: Mapped[str] = mapped_column(Text, default="")
    strava_refresh_token: Mapped[str] = mapped_column(Text, default="")
    strava_token_expires_at: Mapped[int] = mapped_column(Integer, default=0)
    garmin_session: Mapped[str] = mapped_column(Text, default="")  # serialized garth session
