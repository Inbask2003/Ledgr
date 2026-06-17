from app.core.ratelimit import FixedWindowRateLimiter


def test_allows_up_to_limit_then_blocks():
    limiter = FixedWindowRateLimiter(limit=3, window_seconds=60)
    now = 1000.0

    assert limiter.check("k", now)[0] is True
    assert limiter.check("k", now)[0] is True
    assert limiter.check("k", now)[0] is True
    assert limiter.check("k", now)[0] is False


def test_window_resets():
    limiter = FixedWindowRateLimiter(limit=1, window_seconds=60)
    assert limiter.check("k", 1000.0)[0] is True
    assert limiter.check("k", 1000.0)[0] is False
    assert limiter.check("k", 1061.0)[0] is True


def test_keys_are_independent():
    limiter = FixedWindowRateLimiter(limit=1, window_seconds=60)
    assert limiter.check("a", 1000.0)[0] is True
    assert limiter.check("b", 1000.0)[0] is True
