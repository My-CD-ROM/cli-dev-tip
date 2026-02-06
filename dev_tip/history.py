from __future__ import annotations

import json
from pathlib import Path

HISTORY_DIR = Path.home() / ".dev-tip"
HISTORY_FILE = HISTORY_DIR / "history.json"


def _load_history() -> list[str]:
    """Load the list of seen tip IDs from disk."""
    if not HISTORY_FILE.exists():
        return []
    return json.loads(HISTORY_FILE.read_text())


def _save_history(seen: list[str]) -> None:
    """Save the list of seen tip IDs to disk."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(seen))


def get_unseen(tips: list[dict]) -> list[dict]:
    """Filter out already-seen tips. If all are seen, reset history."""
    seen = set(_load_history())
    unseen = [t for t in tips if t["id"] not in seen]
    if not unseen:
        _save_history([])
        return tips
    return unseen


def all_seen(tips: list[dict]) -> bool:
    """Check if every tip has been seen."""
    seen = set(_load_history())
    return all(t["id"] in seen for t in tips)


def mark_seen(tip_id: str) -> None:
    """Append a tip ID to the history file."""
    seen = _load_history()
    if tip_id not in seen:
        seen.append(tip_id)
        _save_history(seen)
