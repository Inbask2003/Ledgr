from uuid import UUID

from app.core.exceptions import InvalidStateError, ValidationError
from app.model.enums import LedgerAccount, LedgerDirection, PaymentStatus
from app.model.merchant import Merchant
from app.model.refund import Refund
from app.repository.ledger import LedgerRepository
from app.repository.payment import PaymentRepository
from app.repository.refund import RefundRepository
from app.repository.webhook import WebhookRepository
from app.schema.refund import RefundCreate
from app.service import ledger as ledger_service
from app.service import webhook as webhook_service
from app.service.payment import get_payment
from app.core.logging import get_logger

logger = get_logger(__name__)

REFUNDABLE_STATES = {PaymentStatus.CAPTURED, PaymentStatus.PARTIALLY_REFUNDED}


async def refund_payment(
    payment_repo: PaymentRepository,
    refund_repo: RefundRepository,
    ledger_repo: LedgerRepository,
    merchant: Merchant,
    payment_id: UUID,
    data: RefundCreate,
) -> Refund:
    payment = await get_payment(payment_repo, merchant, payment_id)

    if payment.status not in REFUNDABLE_STATES:
        raise InvalidStateError(
            f"Only a captured payment can be refunded (current: {payment.status})"
        )

    refundable = payment.amount - payment.amount_refunded
    amount = data.amount if data.amount is not None else refundable

    if amount > refundable:
        raise ValidationError(
            f"Refund of {amount} exceeds the refundable amount of {refundable}"
        )

    refund = Refund(
        payment_id=payment.id,
        merchant_id=merchant.id,
        amount=amount,
        currency=payment.currency,
        reason=data.reason,
    )
    await refund_repo.add(refund)

    payment.amount_refunded += amount
    payment.status = (
        PaymentStatus.REFUNDED
        if payment.amount_refunded == payment.amount
        else PaymentStatus.PARTIALLY_REFUNDED
    )

    await ledger_service.post(
        ledger_repo,
        merchant_id=merchant.id,
        payment_id=payment.id,
        refund_id=refund.id,
        currency=payment.currency,
        lines=[
            ledger_service.Line(
                account=LedgerAccount.MERCHANT_BALANCE,
                direction=LedgerDirection.DEBIT,
                amount=amount,
                description=f"Refund {refund.id} on payment {payment.id}",
            ),
            ledger_service.Line(
                account=LedgerAccount.PAYMENTS_CLEARING,
                direction=LedgerDirection.CREDIT,
                amount=amount,
                description=f"Refund {refund.id} on payment {payment.id}",
            ),
        ],
    )

    event_type = (
        "payment.refunded"
        if payment.status == PaymentStatus.REFUNDED
        else "payment.partially_refunded"
    )
    await webhook_service.enqueue_event(
        WebhookRepository(payment_repo.db), merchant.id, payment, event_type
    )

    await payment_repo.commit()
    await payment_repo.refresh(refund)
    logger.info("refunded %s on payment %s for merchant %s", amount, payment.id, merchant.id)
    return refund
