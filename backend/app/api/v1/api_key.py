from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_api_key_repo, get_current_merchant
from app.model.merchant import Merchant
from app.repository.api_key import ApiKeyRepository
from app.schema.api_key import ApiKeyCreate, ApiKeyCreated, ApiKeyOut
from app.service import api_key as api_key_service

router = APIRouter(prefix="/api-keys", tags=["API keys"])


@router.post("", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    data: ApiKeyCreate,
    merchant: Merchant = Depends(get_current_merchant),
    repo: ApiKeyRepository = Depends(get_api_key_repo),
):
    api_key, full_key = await api_key_service.create_api_key(repo, merchant, data.name)
    return ApiKeyCreated(key=full_key, **ApiKeyOut.model_validate(api_key).model_dump())


@router.get("", response_model=list[ApiKeyOut])
async def list_api_keys(
    merchant: Merchant = Depends(get_current_merchant),
    repo: ApiKeyRepository = Depends(get_api_key_repo),
):
    return await repo.list_for_merchant(merchant.id)


@router.delete("/{key_id}", response_model=ApiKeyOut)
async def revoke_api_key(
    key_id: UUID,
    merchant: Merchant = Depends(get_current_merchant),
    repo: ApiKeyRepository = Depends(get_api_key_repo),
):
    return await api_key_service.revoke_api_key(repo, merchant, key_id)
