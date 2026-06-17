from uuid import uuid4

import pytest

from app.core.exceptions import LedgrError
from app.model.enums import LedgerAccount, LedgerDirection
from app.service import ledger as ledger_service


class FakeLedgerRepo:
    """Captures whatever post() hands the repository, no DB involved."""

    def __init__(self):
        self.entries = []

    async def add_entries(self, entries):
        self.entries.extend(entries)


async def test_post_writes_balanced_entries():
    repo = FakeLedgerRepo()
    merchant_id = uuid4()

    await ledger_service.post(
        repo,
        merchant_id=merchant_id,
        lines=[
            ledger_service.Line(LedgerAccount.PAYMENTS_CLEARING, LedgerDirection.DEBIT, 1000, "in"),
            ledger_service.Line(LedgerAccount.MERCHANT_BALANCE, LedgerDirection.CREDIT, 1000, "in"),
        ],
    )

    assert len(repo.entries) == 2
    assert all(e.merchant_id == merchant_id for e in repo.entries)


async def test_post_rejects_unbalanced_entries():
    repo = FakeLedgerRepo()

    with pytest.raises(LedgrError):
        await ledger_service.post(
            repo,
            merchant_id=uuid4(),
            lines=[
                ledger_service.Line(LedgerAccount.PAYMENTS_CLEARING, LedgerDirection.DEBIT, 1000, "in"),
                ledger_service.Line(LedgerAccount.MERCHANT_BALANCE, LedgerDirection.CREDIT, 999, "in"),
            ],
        )

    assert repo.entries == []
