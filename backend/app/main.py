from fastapi import FastAPI
from app.core.config import settings
from contextlib import asynccontextmanager
from app.db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

@app.get("/healthz")
def health():
    return {"service": settings.app_name, "version": settings.app_version, "status": "ok"}