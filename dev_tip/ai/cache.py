from __future__ import annotations

import json
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".dev-tip"
CACHE_FILE = CACHE_DIR / "ai_cache.json"
COOLDOWN_SECONDS = 5 * 60  # 5 min backoff after API failure


def _cache_key(topic: str | None, level: str | None) -> str:
    """Build a cache key like 'python:beginner' or 'None:None'."""
    return f"{topic}:{level}"


def _load_all() -> dict:
    """Load full cache, auto-migrating v1 single-key format to v2."""
    if not CACHE_FILE.exists():
        return {"version": 2, "keys": {}}

    data = json.loads(CACHE_FILE.read_text())

    # v1 migration: old format had top-level topic/level/tips/generated_at
    if "version" not in data and "tips" in data:
        key = _cache_key(data.get("topic"), data.get("level"))
        migrated = {
            "version": 2,
            "keys": {
                key: {
                    "generated_at": data.get("generated_at", 0.0),
                    "tips": data.get("tips", []),
                }
            },
        }
        _save_all(migrated)
        return migrated

    return data


def _save_all(data: dict) -> None:
    """Write full cache to disk."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(data, indent=2))


def load_cache(topic: str | None, level: str | None) -> list[dict]:
    """Return all cached tips for a topic+level combo (never expires)."""
    data = _load_all()
    key = _cache_key(topic, level)
    entry = data.get("keys", {}).get(key)
    if not entry:
        return []
    return entry.get("tips", [])


def save_cache(tips: list[dict], topic: str | None, level: str | None) -> None:
    """Merge tips into the multi-key cache structure."""
    data = _load_all()
    key = _cache_key(topic, level)
    existing = data.get("keys", {}).get(key, {}).get("tips", [])

    # Deduplicate by tip id
    seen_ids = {t["id"] for t in existing}
    merged = existing + [t for t in tips if t["id"] not in seen_ids]

    data.setdefault("keys", {})[key] = {
        "generated_at": time.time(),
        "tips": merged,
    }
    data["version"] = 2
    _save_all(data)


def cache_needs_refill(topic: str | None, level: str | None, unseen_count: int) -> bool:
    """Return True when unseen tips are running low and cache entry exists."""
    if unseen_count > 3:
        return False
    data = _load_all()
    key = _cache_key(topic, level)
    return key in data.get("keys", {})


def is_on_cooldown() -> bool:
    """Return True if a recent API failure means we should skip retrying."""
    data = _load_all()
    failed_at = data.get("last_failure", 0)
    return time.time() - failed_at < COOLDOWN_SECONDS


def mark_failure() -> None:
    """Record an API failure timestamp for cooldown backoff."""
    data = _load_all()
    data["last_failure"] = time.time()
    _save_all(data)


def clear_cache() -> None:
    """Delete the AI cache file."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()


def get_cache_stats() -> dict:
    """Return cache statistics for the status command."""
    data = _load_all()
    keys = data.get("keys", {})
    total_tips = sum(len(entry.get("tips", [])) for entry in keys.values())
    return {
        "keys": len(keys),
        "total_tips": total_tips,
        "cooldown_active": is_on_cooldown(),
    }
