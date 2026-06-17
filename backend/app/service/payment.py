from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.core.exceptions import InvalidStateError, NotFoundError
from app.model.enums import LedgerAccount, LedgerDirection, PaymentStatus
from app.model.merchant import Merchant
from app.model.payment import Payment
from app.repository.ledger import LedgerRepository
from app.repository.payment import PaymentRepository
from app.repository.webhook import WebhookRepository
from app.schema.payment import PaymentCreate
from app.service import ledger as ledger_service
from app.service import processor
from app.service import webhook as webhook_service
from app.core.logging import get_logger

logger = get_logger(__name__)


async def create_payment(
    repo: PaymentRepository, merchant: Merchant, data: PaymentCreate
) -> Payment:
    values = {
        "id": uuid4(),
        "merchant_id": merchant.id,
        "amount": data.amount,
        "amount_refunded": 0,
        "currency": data.currency,
        "description": data.description,
        "status": PaymentStatus.CREATED,
        "idempotency_key": data.idempotency_key,
    }

    if not data.idempotency_key:
        return await repo.insert(values)

    payment = await repo.insert_if_absent(values)
    if payment is None:
        payment = await repo.get_by_idempotency_key(merchant.id, data.idempotency_key)
    return payment


async def get_payment(repo: PaymentRepository, merchant: Merchant, payment_id: UUID) -> Payment:
    payment = await repo.get(merchant.id, payment_id)
    if payment is None:
        raise NotFoundError("Payment not found")
    return payment


async def confirm_payment(
    repo: PaymentRepository,
    ledger_repo: LedgerRepository,
    merchant: Merchant,
    payment_id: UUID,
) -> Payment:
    payment = await get_payment(repo, merchant, payment_id)

    if payment.status != PaymentStatus.CREATED:
        raise InvalidStateError(
            f"Only a payment in 'created' state can be confirmed (current: {payment.status})"
        )

    result = processor.charge()

    if result.success:
        payment.status = PaymentStatus.CAPTURED
        payment.captured_at = datetime.now(timezone.utc)
        await ledger_service.post(
            ledger_repo,
            merchant_id=merchant.id,
            payment_id=payment.id,
            currency=payment.currency,
            lines=[
                ledger_service.Line(
                    account=LedgerAccount.PAYMENTS_CLEARING,
                    direction=LedgerDirection.DEBIT,
                    amount=payment.amount,
                    description=f"Captured payment {payment.id}",
                ),
                ledger_service.Line(
                    account=LedgerAccount.MERCHANT_BALANCE,
                    direction=LedgerDirection.CREDIT,
                    amount=payment.amount,
                    description=f"Captured payment {payment.id}",
                ),
            ],
        )
        logger.info("captured payment %s for merchant %s", payment.id, merchant.id)
    else:
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = result.failure_reason
        logger.info(
            "payment %s failed (%s) for merchant %s",
            payment.id,
            result.failure_reason,
            merchant.id,
        )

    event_type = "payment.captured" if result.success else "payment.failed"
    await webhook_service.enqueue_event(
        WebhookRepository(repo.db), merchant.id, payment, event_type
    )

    await repo.commit()
    await repo.refresh(payment)
    return payment


async def cancel_payment(
    repo: PaymentRepository, merchant: Merchant, payment_id: UUID
) -> Payment:
    payment = await get_payment(repo, merchant, payment_id)

    if payment.status != PaymentStatus.CREATED:
        raise InvalidStateError(
            f"Only a payment in 'created' state can be cancelled (current: {payment.status})"
        )

    payment.status = PaymentStatus.CANCELLED
    await repo.commit()
    await repo.refresh(payment)
    return payment
