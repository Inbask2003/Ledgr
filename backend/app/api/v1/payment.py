from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    get_current_merchant,
    get_ledger_repo,
    get_payment_repo,
    get_refund_repo,
)
from app.model.enums import PaymentStatus
from app.model.merchant import Merchant
from app.repository.ledger import LedgerRepository
from app.repository.payment import PaymentRepository
from app.repository.refund import RefundRepository
from app.schema.payment import PaymentCreate, PaymentOut, PaymentPage
from app.schema.refund import RefundCreate, RefundOut
from app.service import payment as payment_service
from app.service import refund as refund_service

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: PaymentCreate,
    merchant: Merchant = Depends(get_current_merchant),
    repo: PaymentRepository = Depends(get_payment_repo),
):
    return await payment_service.create_payment(repo, merchant, data)


@router.get("", response_model=PaymentPage)
async def list_payments(
    merchant: Merchant = Depends(get_current_merchant),
    repo: PaymentRepository = Depends(get_payment_repo),
    status: PaymentStatus | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    min_amount: int | None = Query(default=None, ge=0),
    max_amount: int | None = Query(default=None, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    items, total = await repo.list(
        merchant.id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        max_amount=max_amount,
        limit=limit,
        offset=offset,
    )
    return PaymentPage(items=items, total=total, limit=limit, offset=offset)


@router.get("/{payment_id}", response_model=PaymentOut)
async def get_payment(
    payment_id: UUID,
    merchant: Merchant = Depends(get_current_merchant),
    repo: PaymentRepository = Depends(get_payment_repo),
):
    return await payment_service.get_payment(repo, merchant, payment_id)


@router.post("/{payment_id}/confirm", response_model=PaymentOut)
async def confirm_payment(
    payment_id: UUID,
    merchant: Merchant = Depends(get_current_merchant),
    repo: PaymentRepository = Depends(get_payment_repo),
    ledger_repo: LedgerRepository = Depends(get_ledger_repo),
):
    return await payment_service.confirm_payment(repo, ledger_repo, merchant, payment_id)


@router.post("/{payment_id}/cancel", response_model=PaymentOut)
async def cancel_payment(
    payment_id: UUID,
    merchant: Merchant = Depends(get_current_merchant),
    repo: PaymentRepository = Depends(get_payment_repo),
):
    return await payment_service.cancel_payment(repo, merchant, payment_id)


@router.post("/{payment_id}/refunds", response_model=RefundOut, status_code=status.HTTP_201_CREATED)
async def refund_payment(
    payment_id: UUID,
    data: RefundCreate,
    merchant: Merchant = Depends(get_current_merchant),
    repo: PaymentRepository = Depends(get_payment_repo),
    refund_repo: RefundRepository = Depends(get_refund_repo),
    ledger_repo: LedgerRepository = Depends(get_ledger_repo),
):
    return await refund_service.refund_payment(
        repo, refund_repo, ledger_repo, merchant, payment_id, data
    )


@router.get("/{payment_id}/refunds", response_model=list[RefundOut])
async def list_refunds(
    payment_id: UUID,
    merchant: Merchant = Depends(get_current_merchant),
    repo: PaymentRepository = Depends(get_payment_repo),
    refund_repo: RefundRepository = Depends(get_refund_repo),
):
    await payment_service.get_payment(repo, merchant, payment_id)
    return await refund_repo.list_for_payment(merchant.id, payment_id)
