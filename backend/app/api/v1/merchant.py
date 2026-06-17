from fastapi import APIRouter, Depends, status

from app.schema.merchant import MerchantCreate, MerchantOut
from app.service.merchant import create_merchant
from app.repository.merchant import MerchantRepository
from app.core.dependencies import get_merchant_repo, get_current_merchant
from app.model.merchant import Merchant

router = APIRouter(prefix="/merchants", tags=["Merchants"])


@router.post("", response_model=MerchantOut, status_code=status.HTTP_201_CREATED)
async def create_merchant_route(
    merchant_data: MerchantCreate,
    repo: MerchantRepository = Depends(get_merchant_repo),
):
    return await create_merchant(repo, merchant_data)


@router.get("/me", response_model=MerchantOut)
async def get_me(merchant: Merchant = Depends(get_current_merchant)):
    return merchant
