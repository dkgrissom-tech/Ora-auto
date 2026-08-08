"""
YT Studio API — FastAPI entry point
Deploy on Replit: run this file, Autoscale subdomain: yt-studio-grissom

Required env vars (set in Replit Secrets):
  ANTHROPIC_API_KEY
  ELEVENLABS_API_KEY
  YT_STUDIO_API_KEY   (generate any UUID, mirror to n8n)
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.auth import verify_api_key
from api import research, scripts, voice, video, thumbnail

app = FastAPI(title="YT Studio API", version="1.0.0")

# Auth middleware — runs on every request except /health
app.middleware("http")(verify_api_key)

# CORS — allow n8n Railway domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://n8n-production-b205b.up.railway.app",
        "https://*.replit.app",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router, prefix="/api")
app.include_router(scripts.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(video.router, prefix="/api")
app.include_router(thumbnail.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok", "service": "yt-studio-api"}


@app.get("/")
def root():
    return {"service": "YT Studio API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
