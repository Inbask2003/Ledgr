import asyncio
import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.model.enums import WebhookStatus
from app.model.merchant import Merchant
from app.model.payment import Payment
from app.model.webhook import WebhookEndpoint, WebhookEvent
from app.repository.webhook import WebhookRepository
from app.schema.payment import PaymentOut

logger = get_logger(__name__)

BACKOFF_SECONDS = [60, 300, 1800, 7200, 43200]
MAX_ATTEMPTS = 5
DELIVERY_TIMEOUT = 15.0
POLL_INTERVAL = 5.0


def generate_secret() -> str:
    return f"whsec_{secrets.token_hex(24)}"


def sign(secret: str, timestamp: int, body: bytes) -> str:
    signed = f"{timestamp}.".encode() + body
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


async def set_endpoint(repo: WebhookRepository, merchant: Merchant, url: str) -> WebhookEndpoint:
    endpoint = await repo.get_endpoint(merchant.id)
    if endpoint is None:
        endpoint = WebhookEndpoint(merchant_id=merchant.id, url=url, secret=generate_secret())
    else:
        endpoint.url = url
    return await repo.save_endpoint(endpoint)


async def delete_endpoint(repo: WebhookRepository, merchant: Merchant) -> None:
    endpoint = await repo.get_endpoint(merchant.id)
    if endpoint is None:
        raise NotFoundError("No webhook endpoint configured")
    await repo.delete_endpoint(endpoint)


async def enqueue_event(
    repo: WebhookRepository, merchant_id: UUID, payment: Payment, event_type: str
) -> None:
    endpoint = await repo.get_endpoint(merchant_id)
    if endpoint is None:
        return

    event = WebhookEvent(
        merchant_id=merchant_id,
        payment_id=payment.id,
        event_type=event_type,
        payload={},
    )
    await repo.add_event(event)
    event.payload = {
        "id": str(event.id),
        "type": event_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "merchant_id": str(merchant_id),
        "data": PaymentOut.model_validate(payment).model_dump(mode="json"),
    }


async def replay_event(repo: WebhookRepository, merchant: Merchant, event_id: UUID) -> WebhookEvent:
    event = await repo.get_event(merchant.id, event_id)
    if event is None:
        raise NotFoundError("Webhook event not found")
    event.status = WebhookStatus.PENDING
    event.attempts = 0
    event.last_error = None
    event.next_attempt_at = datetime.now(timezone.utc)
    await repo.commit()
    return event


async def _deliver(url: str, secret: str, event: WebhookEvent) -> int:
    body = json.dumps(event.payload, separators=(",", ":")).encode()
    timestamp = int(time.time())
    headers = {
        "Content-Type": "application/json",
        "Ledgr-Signature": sign(secret, timestamp, body),
        "Ledgr-Event-Id": str(event.id),
        "Ledgr-Event-Type": event.event_type,
    }
    async with httpx.AsyncClient(timeout=DELIVERY_TIMEOUT) as client:
        response = await client.post(url, content=body, headers=headers)
    return response.status_code


async def _process_due_events() -> None:
    async with AsyncSessionLocal() as db:
        repo = WebhookRepository(db)
        now = datetime.now(timezone.utc)
        events = await repo.due_events(now)

        for event in events:
            endpoint = await repo.get_endpoint(event.merchant_id)
            if endpoint is None:
                event.status = WebhookStatus.FAILED
                event.last_error = "No webhook endpoint configured"
                continue

            event.attempts += 1
            try:
                status_code = await _deliver(endpoint.url, endpoint.secret, event)
                if 200 <= status_code < 300:
                    event.status = WebhookStatus.SUCCEEDED
                    event.delivered_at = now
                    event.last_error = None
                else:
                    raise RuntimeError(f"endpoint returned HTTP {status_code}")
            except Exception as exc:
                event.last_error = str(exc)[:500]
                if event.attempts >= MAX_ATTEMPTS:
                    event.status = WebhookStatus.FAILED
                else:
                    delay = BACKOFF_SECONDS[min(event.attempts - 1, len(BACKOFF_SECONDS) - 1)]
                    event.next_attempt_at = now + timedelta(seconds=delay)

        await repo.commit()


async def run_dispatcher() -> None:
    logger.info("webhook dispatcher started")
    while True:
        try:
            await _process_due_events()
        except Exception:
            logger.exception("webhook dispatcher loop error")
        await asyncio.sleep(POLL_INTERVAL)
