import asyncio
import sys

from app.core.logging import get_logger, setup_logging
from app.db.session import AsyncSessionLocal, engine
from app.service.reconcile import find_imbalances

logger = get_logger(__name__)


async def run() -> int:
    async with AsyncSessionLocal() as db:
        imbalances = await find_imbalances(db)

    if not imbalances:
        logger.info("ledger reconciliation passed: every merchant balances")
        return 0

    for item in imbalances:
        logger.error(
            "ledger imbalance for merchant %s: debits=%s credits=%s",
            item.merchant_id,
            item.debits,
            item.credits,
        )
    return 1


async def run_reconcile_loop(interval_seconds: int = 3600) -> None:
    logger.info("ledger reconciliation loop started")
    while True:
        try:
            await run()
        except Exception:
            logger.exception("reconciliation loop error")
        await asyncio.sleep(interval_seconds)


async def _main() -> int:
    setup_logging()
    try:
        return await run()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    sys.exit(asyncio.run(_main()))
