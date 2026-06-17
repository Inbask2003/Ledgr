from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_audit_repo, get_current_merchant
from app.model.merchant import Merchant
from app.repository.audit import AuditRepository
from app.schema.audit import AuditLogPage

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("", response_model=AuditLogPage)
async def list_audit_logs(
    merchant: Merchant = Depends(get_current_merchant),
    repo: AuditRepository = Depends(get_audit_repo),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    items, total = await repo.list_for_merchant(merchant.id, limit=limit, offset=offset)
    return AuditLogPage(items=items, total=total, limit=limit, offset=offset)
