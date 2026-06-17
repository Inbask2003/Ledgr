from dataclasses import dataclass

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.enums import LedgerDirection
from app.model.ledger import LedgerEntry


@dataclass
class Imbalance:
    merchant_id: str
    debits: int
    credits: int


async def find_imbalances(db: AsyncSession) -> list[Imbalance]:
    debits = func.sum(
        case((LedgerEntry.direction == LedgerDirection.DEBIT, LedgerEntry.amount), else_=0)
    )
    credits = func.sum(
        case((LedgerEntry.direction == LedgerDirection.CREDIT, LedgerEntry.amount), else_=0)
    )

    stmt = (
        select(LedgerEntry.merchant_id, debits, credits)
        .group_by(LedgerEntry.merchant_id)
        .having(debits != credits)
    )
    result = await db.execute(stmt)
    return [
        Imbalance(merchant_id=str(row[0]), debits=int(row[1]), credits=int(row[2]))
        for row in result.all()
    ]
