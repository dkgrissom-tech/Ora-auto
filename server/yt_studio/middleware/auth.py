"""
YT Studio API — Auth Middleware
Checks X-API-Key header against YT_STUDIO_API_KEY env var.
Add to FastAPI with: app.middleware("http")(verify_api_key)
"""

import os
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

EXPECTED_KEY = os.environ.get("YT_STUDIO_API_KEY", "")


async def verify_api_key(request: Request, call_next):
    """Middleware: reject requests with missing or wrong X-API-Key."""
    # Skip auth for health check
    if request.url.path in ("/health", "/"):
        return await call_next(request)

    api_key = request.headers.get("X-API-Key", "")
    if not EXPECTED_KEY:
        # Key not configured — fail loudly so Don knows
        return JSONResponse(
            status_code=500,
            content={"error": "YT_STUDIO_API_KEY env var not set on server"}
        )
    if api_key != EXPECTED_KEY:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid or missing X-API-Key header"}
        )
    return await call_next(request)
