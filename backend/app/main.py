from fastapi import FastAPI
from app.core.config import settings
from contextlib import asynccontextmanager
from app.db.session import engine
from app.api.v1.merchant import router as merchant_router
from app.core.logging import setup_logging, get_logger

setup_logging()

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.include_router(router=merchant_router, prefix="/api/v1")

@app.get("/healthz")
def health():
    return {"service": settings.app_name, "version": settings.app_version, "status": "ok"}

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)