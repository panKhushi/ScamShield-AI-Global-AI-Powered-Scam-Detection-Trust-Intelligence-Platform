import time
from collections import defaultdict
from fastapi import Request, HTTPException

_request_log: dict[str, list[float]] = defaultdict(list)


def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    def dependency(request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        _request_log[client_ip] = [
            t for t in _request_log[client_ip] if now - t < window_seconds
        ]

        if len(_request_log[client_ip]) >= max_requests:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: max {max_requests} requests per {window_seconds} seconds",
            )

        _request_log[client_ip].append(now)

    return dependency