from __future__ import annotations

import json
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".dev-tip"
CACHE_FILE = CACHE_DIR / "ai_cache.json"
TTL_SECONDS = 24 * 60 * 60  # 24 hours


def load_cache(topic: str | None, level: str | None) -> list[dict]:
    """Return cached tips if fresh and filters match, else empty list."""
    if not CACHE_FILE.exists():
        return []

    data = json.loads(CACHE_FILE.read_text())
    if data.get("topic") != topic or data.get("level") != level:
        return []
    if time.time() - data.get("generated_at", 0) > TTL_SECONDS:
        return []

    return data.get("tips", [])


def save_cache(tips: list[dict], topic: str | None, level: str | None) -> None:
    """Write tips to the cache file."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "generated_at": time.time(),
        "topic": topic,
        "level": level,
        "tips": tips,
    }
    CACHE_FILE.write_text(json.dumps(data, indent=2))
