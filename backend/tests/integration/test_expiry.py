from datetime import datetime, timedelta, timezone

from app.repository.payment import PaymentRepository


def auth(token):
    return {"Authorization": f"Bearer {token}"}


async def test_stale_created_payment_expires(client, session, merchant_token):
    res = await client.post(
        "/api/v1/payments",
        headers=auth(merchant_token),
        json={"amount": 500, "currency": "INR"},
    )
    pid = res.json()["id"]

    cutoff = datetime.now(timezone.utc) + timedelta(minutes=1)
    expired = await PaymentRepository(session).expire_stale(cutoff)
    assert expired >= 1

    res = await client.get(f"/api/v1/payments/{pid}", headers=auth(merchant_token))
    assert res.json()["status"] == "expired"

    res = await client.post(f"/api/v1/payments/{pid}/confirm", headers=auth(merchant_token))
    assert res.status_code == 409
