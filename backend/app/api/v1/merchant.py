from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schema.merchant import MerchantCreate
from app.service.merchant import create_merchant
from app.repository.merchant import MerchantRepository


router = APIRouter(prefix="/merchants", tags=["Merchants"])

def get_merchant_repo(db: AsyncSession = Depends(get_db)):
    return MerchantRepository(db)

@router.post("")
async def create_merchant_route(merchant_data: MerchantCreate, repo: MerchantRepository = Depends(get_merchant_repo)):
    return await create_merchant(repo, merchant_data)

