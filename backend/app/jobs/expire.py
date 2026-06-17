import asyncio
import sys
from datetime import datetime, timedelta, timezone

from app.core.logging import get_logger, setup_logging
from app.db.session import AsyncSessionLocal, engine
from app.repository.payment import PaymentRepository

logger = get_logger(__name__)

EXPIRY_MINUTES = 15


async def run() -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=EXPIRY_MINUTES)
    async with AsyncSessionLocal() as db:
        expired = await PaymentRepository(db).expire_stale(cutoff)
    if expired:
        logger.info("expired %s stale payments", expired)
    return expired


async def run_expiry_loop(interval_seconds: int = 60) -> None:
    logger.info("payment expiry loop started")
    while True:
        try:
            await run()
        except Exception:
            logger.exception("payment expiry loop error")
        await asyncio.sleep(interval_seconds)


async def _main() -> int:
    setup_logging()
    try:
        await run()
        return 0
    finally:
        await engine.dispose()


if __name__ == "__main__":
    sys.exit(asyncio.run(_main()))
