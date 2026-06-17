from uuid import UUID

from app.repository.audit import AuditRepository


def auth(token):
    return {"Authorization": f"Bearer {token}"}


async def test_audit_logs_are_scoped_and_listed(client, session, merchant_token):
    me = await client.get("/api/v1/merchants/me", headers=auth(merchant_token))
    merchant_id = UUID(me.json()["id"])

    repo = AuditRepository(session)
    await repo.record(merchant_id, "POST", "/api/v1/payments", 201)
    await repo.record(merchant_id, "GET", "/api/v1/ledger", 200)
    await repo.record(None, "POST", "/api/v1/auth/login", 200)

    res = await client.get("/api/v1/audit-logs", headers=auth(merchant_token))
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 2
    assert {item["path"] for item in body["items"]} == {
        "/api/v1/payments",
        "/api/v1/ledger",
    }
