from sqlalchemy.exc import IntegrityError

from app.model.merchant import Merchant
from app.schema.merchant import MerchantCreate
from app.repository.merchant import MerchantRepository
from app.core.security import hash_password
from app.core.exceptions import ConflictError


async def create_merchant(repo: MerchantRepository, merchant_data: MerchantCreate) -> Merchant:
    merchant = Merchant(
        email=merchant_data.email,
        business_name=merchant_data.business_name,
        password_hash=hash_password(merchant_data.password),
    )

    try:
        return await repo.create_merchant(merchant)
    except IntegrityError:
        raise ConflictError("A merchant with this email already exists")
