from dataclasses import dataclass
from uuid import UUID

from app.core.exceptions import LedgrError
from app.model.enums import LedgerDirection
from app.model.ledger import LedgerEntry
from app.repository.ledger import LedgerRepository


@dataclass
class Line:
    account: str
    direction: LedgerDirection
    amount: int
    description: str


async def post(
    repo: LedgerRepository,
    *,
    merchant_id: UUID,
    lines: list[Line],
    currency: str = "INR",
    payment_id: UUID | None = None,
    refund_id: UUID | None = None,
) -> None:
    debits = sum(line.amount for line in lines if line.direction == LedgerDirection.DEBIT)
    credits = sum(line.amount for line in lines if line.direction == LedgerDirection.CREDIT)

    if debits != credits:
        raise LedgrError(f"Unbalanced ledger post: debits={debits} credits={credits}")

    entries = [
        LedgerEntry(
            merchant_id=merchant_id,
            payment_id=payment_id,
            refund_id=refund_id,
            account=line.account,
            direction=line.direction,
            amount=line.amount,
            currency=currency,
            description=line.description,
        )
        for line in lines
    ]
    await repo.add_entries(entries)
