"""
File-backed job store.

Replaces the module-level `jobs: dict = {}` that the first version used. That
dict lived only in one process's memory, which breaks in two ways on Replit
Autoscale:

  1. Autoscale sleeps idle containers. The n8n video pipeline polls
     `GET /api/video/:job_id` every 30s; if the container slept between the
     submit and the poll, the dict is empty and the poll 404s forever.
  2. Autoscale can run more than one instance. A poll routed to instance B
     cannot see a job submitted to instance A.

This store writes one JSON file per job so state survives a restart.

**Deploy requirement:** set Autoscale **max instances = 1** for both services.
A file store fixes restarts, not cross-instance routing — renders happen in a
local thread and write to local disk, so the job and its output file must stay
on the same machine. If you later need real horizontal scale, move to Redis or
object storage; the interface below is deliberately small enough to swap.

Set `JOB_STORE_DIR` to a path that persists across restarts. Anything under
`/tmp` is wiped when the container recycles.
"""

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional

_LOCK = threading.Lock()

JOB_STORE_DIR = Path(os.environ.get("JOB_STORE_DIR", "/tmp/jobs"))
JOB_STORE_DIR.mkdir(parents=True, exist_ok=True)

# Jobs older than this are pruned on read so the directory doesn't grow forever.
MAX_JOB_AGE_SEC = int(os.environ.get("JOB_MAX_AGE_SEC", 7 * 24 * 3600))


def _path(job_id: str) -> Path:
    # Guard against traversal — job_id comes off the URL.
    safe = "".join(c for c in job_id if c.isalnum() or c in "-_")
    if not safe:
        raise ValueError("invalid job_id")
    return JOB_STORE_DIR / f"{safe}.json"


def _write_atomic(path: Path, data: dict) -> None:
    """Write via temp file + rename so a poll never reads a half-written file."""
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def create(job_id: str, **fields) -> dict:
    """Register a new job in the 'queued' state."""
    record = {
        "job_id": job_id,
        "status": "queued",
        "video_url": None,
        "error": None,
        "started_at": time.time(),
    }
    record.update(fields)
    with _LOCK:
        _write_atomic(_path(job_id), record)
    return record


def get(job_id: str) -> Optional[dict]:
    """Return the job record, or None if unknown."""
    path = _path(job_id)
    with _LOCK:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None


def exists(job_id: str) -> bool:
    return get(job_id) is not None


def update(job_id: str, fields: dict) -> Optional[dict]:
    """Merge `fields` into the stored record and persist it."""
    path = _path(job_id)
    with _LOCK:
        if not path.exists():
            return None
        try:
            record = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None
        record.update(fields)
        _write_atomic(path, record)
        return record


def count() -> int:
    return len(list(JOB_STORE_DIR.glob("*.json")))


def prune(max_age_sec: int = MAX_JOB_AGE_SEC) -> int:
    """Delete job records older than max_age_sec. Returns how many were removed."""
    cutoff = time.time() - max_age_sec
    removed = 0
    with _LOCK:
        for path in JOB_STORE_DIR.glob("*.json"):
            try:
                if path.stat().st_mtime < cutoff:
                    path.unlink()
                    removed += 1
            except OSError:
                continue
    return removed
