"""
YT Studio API — Auth Middleware
Checks X-API-Key header against YT_STUDIO_API_KEY env var.
Add to FastAPI with: app.middleware("http")(verify_api_key)
"""

import hmac
import os
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


async def verify_api_key(request: Request, call_next):
    """Middleware: reject requests with missing or wrong X-API-Key.

    The expected key is read per request, not captured at import time, so a
    secret added after the process booted takes effect without a code change.
    Comparison is constant-time to avoid leaking the key byte by byte.
    """
    # Skip auth for health check
    if request.url.path in ("/health", "/"):
        return await call_next(request)

    expected_key = os.environ.get("YT_STUDIO_API_KEY", "")
    api_key = request.headers.get("X-API-Key", "")
    if not expected_key:
        # Key not configured — fail loudly so Don knows
        return JSONResponse(
            status_code=500,
            content={"error": "YT_STUDIO_API_KEY env var not set on server"}
        )
    if not hmac.compare_digest(api_key, expected_key):
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid or missing X-API-Key header"}
        )
    return await call_next(request)
