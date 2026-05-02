from app.model.merchant import Merchant
from app.schema.merchant import MerchantCreate
from app.repository.merchant import MerchantRepository

async def create_merchant(repo: MerchantRepository, merchant_data: MerchantCreate):
    hashed_password = merchant_data.password

    merchant = Merchant(
        email=merchant_data.email, 
        business_name=merchant_data.business_name, 
        password_hash=hashed_password
        )
    
    return await repo.create_merchant(merchant)