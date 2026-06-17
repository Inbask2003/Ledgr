import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.core.dependencies import get_current_merchant, get_ledger_repo
from app.model.merchant import Merchant
from app.repository.ledger import LedgerRepository
from app.schema.ledger import LedgerBalance, LedgerEntryOut

router = APIRouter(prefix="/ledger", tags=["Ledger"])


@router.get("", response_model=list[LedgerEntryOut])
async def list_ledger(
    merchant: Merchant = Depends(get_current_merchant),
    repo: LedgerRepository = Depends(get_ledger_repo),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    entries, _ = await repo.list(
        merchant.id, date_from=date_from, date_to=date_to, limit=limit, offset=offset
    )
    return entries


@router.get("/balance", response_model=LedgerBalance)
async def get_balance(
    merchant: Merchant = Depends(get_current_merchant),
    repo: LedgerRepository = Depends(get_ledger_repo),
    currency: str = "INR",
):
    balance = await repo.balance(merchant.id, currency)
    return LedgerBalance(merchant_id=merchant.id, currency=currency, balance=balance)


@router.get("/export")
async def export_ledger(
    merchant: Merchant = Depends(get_current_merchant),
    repo: LedgerRepository = Depends(get_ledger_repo),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["entry_id", "created_at", "account", "direction", "amount", "currency", "payment_id", "refund_id", "description"]
    )

    offset = 0
    page_size = 100
    while True:
        entries, total = await repo.list(
            merchant.id, date_from=date_from, date_to=date_to, limit=page_size, offset=offset
        )
        for e in entries:
            writer.writerow(
                [e.id, e.created_at.isoformat(), e.account, e.direction, e.amount, e.currency, e.payment_id or "", e.refund_id or "", e.description]
            )
        offset += page_size
        if offset >= total:
            break

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ledger.csv"},
    )
