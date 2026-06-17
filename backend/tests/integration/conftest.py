import psycopg2
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.model  # noqa: F401  (register models on Base.metadata)
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

# The audit middleware writes via the production session factory, which the
# dependency override can't reach, so disable it during tests.
settings.audit_enabled = False
settings.rate_limit_enabled = False

_ASYNC_URL = settings.database_url.rsplit("/", 1)[0] + "/ledgr_test"
_SYNC_BASE = settings.database_url.replace("+asyncpg", "")
_SYNC_URL = _SYNC_BASE.rsplit("/", 1)[0] + "/ledgr_test"


def _ensure_test_database():
    dsn = _SYNC_BASE  # points at the default ledgr database
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'ledgr_test'")
            if cur.fetchone() is None:
                cur.execute("CREATE DATABASE ledgr_test")
    finally:
        conn.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    _ensure_test_database()
    sync_engine = create_engine(_SYNC_URL)
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(_ASYNC_URL)
    table_list = ", ".join(t.name for t in reversed(Base.metadata.sorted_tables))
    async with eng.begin() as conn:
        await conn.execute(text(f"TRUNCATE {table_list} RESTART IDENTITY CASCADE"))
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def client(engine):
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with Session() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session(engine):
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as s:
        yield s


@pytest_asyncio.fixture
async def merchant_token(client):
    email = "priya@example.com"
    password = "supersecret1"
    await client.post(
        "/api/v1/merchants",
        json={"email": email, "business_name": "Priya SaaS", "password": password},
    )
    res = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    return res.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}
