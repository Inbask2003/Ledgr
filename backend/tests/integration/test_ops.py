async def test_healthz_reports_db_up(client):
    res = await client.get("/healthz")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["database"] == "up"
