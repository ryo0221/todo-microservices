import time
from typing import Dict, List


class InMemoryRateLimiter:
    """
    Keeps track of per-client request timestamps.
    Simple, single-process in-memory implementation.
    """

    def __init__(self, limit: int = 10, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = {}

    def is_allowed(self, client_ip: str) -> bool:
        now = time.monotonic()
        timestamps = self._requests.get(client_ip, [])
        # Remove expired timestamps
        timestamps = [t for t in timestamps if now - t < self.window_seconds]

        allowed = len(timestamps) < self.limit
        if allowed:
            timestamps.append(now)
        self._requests[client_ip] = timestamps
        return allowed
