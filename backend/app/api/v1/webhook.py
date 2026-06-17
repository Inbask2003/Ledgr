from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_merchant, get_webhook_repo
from app.core.exceptions import NotFoundError
from app.model.merchant import Merchant
from app.repository.webhook import WebhookRepository
from app.schema.webhook import (
    WebhookEndpointIn,
    WebhookEndpointOut,
    WebhookEventOut,
    WebhookEventPage,
)
from app.service import webhook as webhook_service

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.put("/endpoint", response_model=WebhookEndpointOut)
async def set_endpoint(
    data: WebhookEndpointIn,
    merchant: Merchant = Depends(get_current_merchant),
    repo: WebhookRepository = Depends(get_webhook_repo),
):
    return await webhook_service.set_endpoint(repo, merchant, str(data.url))


@router.get("/endpoint", response_model=WebhookEndpointOut)
async def get_endpoint(
    merchant: Merchant = Depends(get_current_merchant),
    repo: WebhookRepository = Depends(get_webhook_repo),
):
    endpoint = await repo.get_endpoint(merchant.id)
    if endpoint is None:
        raise NotFoundError("No webhook endpoint configured")
    return endpoint


@router.delete("/endpoint", status_code=status.HTTP_204_NO_CONTENT)
async def delete_endpoint(
    merchant: Merchant = Depends(get_current_merchant),
    repo: WebhookRepository = Depends(get_webhook_repo),
):
    await webhook_service.delete_endpoint(repo, merchant)


@router.get("/events", response_model=WebhookEventPage)
async def list_events(
    merchant: Merchant = Depends(get_current_merchant),
    repo: WebhookRepository = Depends(get_webhook_repo),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    items, total = await repo.list_events(merchant.id, limit=limit, offset=offset)
    return WebhookEventPage(items=items, total=total, limit=limit, offset=offset)


@router.post("/events/{event_id}/replay", response_model=WebhookEventOut)
async def replay_event(
    event_id: UUID,
    merchant: Merchant = Depends(get_current_merchant),
    repo: WebhookRepository = Depends(get_webhook_repo),
):
    return await webhook_service.replay_event(repo, merchant, event_id)
