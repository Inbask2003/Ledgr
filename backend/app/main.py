import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

from app.core.exceptions import register_exception_handlers
from app.db.session import engine, AsyncSessionLocal
from app.service.webhook import run_dispatcher
from app.jobs.reconcile import run_reconcile_loop
from app.jobs.expire import run_expiry_loop
from app.api.v1.auth import router as auth_router
from app.api.v1.merchant import router as merchant_router
from app.api.v1.payment import router as payment_router
from app.api.v1.ledger import router as ledger_router
from app.api.v1.api_key import router as api_key_router
from app.api.v1.webhook import router as webhook_router
from app.api.v1.audit import router as audit_router
from app.repository.audit import AuditRepository
from app.core.ratelimit import FixedWindowRateLimiter

rate_limiter = FixedWindowRateLimiter(settings.rate_limit_per_minute)


@asynccontextmanager
async def lifespan(app: FastAPI):
    background = [
        asyncio.create_task(run_dispatcher()),
        asyncio.create_task(run_reconcile_loop()),
        asyncio.create_task(run_expiry_loop()),
    ]
    yield
    for task in background:
        task.cancel()
    await engine.dispose()


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.middleware("http")
async def audit_middleware(request, call_next):
    response = await call_next(request)
    if settings.audit_enabled and request.url.path.startswith("/api/v1") and request.method != "OPTIONS":
        try:
            async with AsyncSessionLocal() as db:
                await AuditRepository(db).record(
                    getattr(request.state, "merchant_id", None),
                    request.method,
                    request.url.path,
                    response.status_code,
                )
        except Exception:
            logger.exception("failed to write audit log")
    return response


@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    if settings.rate_limit_enabled and request.url.path.startswith("/api/v1"):
        client_host = request.client.host if request.client else "anon"
        key = request.headers.get("authorization") or client_host
        allowed, retry_after = rate_limiter.check(key, time.time())
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"error": {"code": "rate_limited", "message": "Too many requests"}},
                headers={"Retry-After": str(retry_after)},
            )
    return await call_next(request)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(merchant_router, prefix="/api/v1")
app.include_router(payment_router, prefix="/api/v1")
app.include_router(ledger_router, prefix="/api/v1")
app.include_router(api_key_router, prefix="/api/v1")
app.include_router(webhook_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")


@app.get("/healthz")
async def health():
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    body = {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "ok" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
    }
    return JSONResponse(status_code=200 if db_ok else 503, content=body)


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)
