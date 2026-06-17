import hashlib
import hmac

from app.service import webhook as webhook_service


def test_generate_secret_format():
    secret = webhook_service.generate_secret()
    assert secret.startswith("whsec_")
    assert len(secret) > 20


def test_signature_is_verifiable():
    secret = "whsec_test"
    timestamp = 1718000000
    body = b'{"hello":"world"}'

    header = webhook_service.sign(secret, timestamp, body)

    parts = dict(p.split("=", 1) for p in header.split(","))
    expected = hmac.new(
        secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256
    ).hexdigest()

    assert parts["t"] == str(timestamp)
    assert parts["v1"] == expected


def test_signature_changes_with_body():
    secret = "whsec_test"
    a = webhook_service.sign(secret, 1, b"a")
    b = webhook_service.sign(secret, 1, b"b")
    assert a != b


def test_backoff_schedule_matches_spec():
    assert webhook_service.BACKOFF_SECONDS == [60, 300, 1800, 7200, 43200]
    assert webhook_service.MAX_ATTEMPTS == 5
