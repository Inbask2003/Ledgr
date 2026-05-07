from fastapi import APIRouter, Depends
from app.schema.auth import AuthBase
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repository.merchant import MerchantRepository
from app.core.security import hash_password, verify_password
from app.core.token import create_access_token
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

def get_merchant_repo(db: AsyncSession = Depends(get_db)):
    return MerchantRepository(db)

@router.post("/login")
async def login(user_auth: AuthBase, repo: MerchantRepository = Depends(get_merchant_repo)):
    email, password = user_auth
    hashed_password = hash_password(password)

    if not verify_password(password, hashed_password):
        logger.warning(f"not a valid password for {email} email")
        return None
    
    access_token = create_access_token(email)
    return {"access_token": access_token}