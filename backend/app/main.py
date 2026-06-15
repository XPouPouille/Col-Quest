from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import auth, cols, sync
from .services.scheduler import start_scheduler
from .config import settings
import logging
import json
from pathlib import Path
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_cols()
    start_scheduler()
    yield


async def seed_cols():
    """Insert built-in cols from JSON if table is empty."""
    from .database import AsyncSessionLocal
    from .models import Col

    data_path = Path(__file__).parent / "data" / "cols_europe.json"
    cols_data = json.loads(data_path.read_text())

    async with AsyncSessionLocal() as db:
        count = await db.scalar(select(Col).limit(1))
        if count is not None:
            return
        for c in cols_data:
            db.add(Col(
                name=c["name"],
                latitude=c["lat"],
                longitude=c["lng"],
                altitude=c["alt"],
                country=c.get("country", ""),
            ))
        await db.commit()


app = FastAPI(title="Col Quest API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cols.router)
app.include_router(sync.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
