class FixedWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, tuple[float, int]] = {}

    def check(self, key: str, now: float) -> tuple[bool, int]:
        window_start, count = self._hits.get(key, (now, 0))
        if now - window_start >= self.window:
            window_start, count = now, 0
        count += 1
        self._hits[key] = (window_start, count)
        retry_after = max(1, int(self.window - (now - window_start)))
        return count <= self.limit, retry_after
