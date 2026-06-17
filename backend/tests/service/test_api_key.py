from uuid import uuid4

from app.model.merchant import Merchant
from app.service import api_key as api_key_service


class FakeApiKeyRepo:
    def __init__(self):
        self.rows = []

    async def add(self, api_key):
        self.rows.append(api_key)
        return api_key

    async def get_active_by_prefix(self, prefix):
        for row in self.rows:
            if row.prefix == prefix and row.revoked_at is None:
                return row
        return None


def _merchant():
    m = Merchant(email="a@b.com", business_name="Acme", password_hash="x")
    m.id = uuid4()
    return m


async def test_create_then_resolve_roundtrip():
    repo = FakeApiKeyRepo()
    merchant = _merchant()

    api_key, full_key = await api_key_service.create_api_key(repo, merchant, "default")

    assert full_key.startswith("sk_")
    assert api_key.last4 == full_key[-4:]
    assert api_key.key_hash != full_key

    resolved = await api_key_service.resolve_api_key(repo, full_key)
    assert resolved is api_key


async def test_resolve_rejects_tampered_key():
    repo = FakeApiKeyRepo()
    _, full_key = await api_key_service.create_api_key(repo, _merchant(), "default")

    tampered = full_key[:-1] + ("0" if full_key[-1] != "0" else "1")
    assert await api_key_service.resolve_api_key(repo, tampered) is None


async def test_resolve_rejects_garbage():
    repo = FakeApiKeyRepo()
    assert await api_key_service.resolve_api_key(repo, "not-a-key") is None
