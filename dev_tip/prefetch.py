"""Background prefetch worker: python -m dev_tip.prefetch <topic> <level>

Fetches a fresh batch of AI tips and appends them to the cache.
Uses a lock file to prevent concurrent prefetch processes.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

LOCK_FILE = Path.home() / ".dev-tip" / ".prefetch.lock"
LOCK_MAX_AGE = 120  # seconds


def _acquire_lock() -> bool:
    """Try to acquire the lock file. Return True on success."""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    if LOCK_FILE.exists():
        try:
            info = json.loads(LOCK_FILE.read_text())
            pid = info.get("pid", 0)
            ts = info.get("time", 0)

            # Check if lock is stale
            if time.time() - ts < LOCK_MAX_AGE:
                # Check if process is still alive
                try:
                    os.kill(pid, 0)
                    return False  # Process alive, lock held
                except OSError:
                    pass  # Process dead, stale lock
        except (json.JSONDecodeError, KeyError):
            pass  # Corrupt lock file, take over

    LOCK_FILE.write_text(json.dumps({"pid": os.getpid(), "time": time.time()}))
    return True


def _release_lock() -> None:
    """Remove the lock file."""
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def main() -> None:
    args = sys.argv[1:]
    if len(args) != 2:
        return

    topic = None if args[0] == "null" else args[0]
    level = None if args[1] == "null" else args[1]

    if not _acquire_lock():
        return

    try:
        from dev_tip.ai.cache import is_on_cooldown, mark_failure, save_cache
        from dev_tip.ai.provider import create_provider
        from dev_tip.config import load_config

        if is_on_cooldown():
            return

        config = load_config()
        provider_name = config.get("ai_provider")
        if not provider_name:
            return

        api_key = config.get("ai_key")
        if not api_key:
            env_keys = {"gemini": "GEMINI_API_KEY", "openrouter": "OPENROUTER_API_KEY"}
            env_var = env_keys.get(provider_name)
            if env_var:
                api_key = os.environ.get(env_var)
        if not api_key:
            return

        provider = create_provider(provider_name, api_key, model=config.get("ai_model"))
        try:
            new_tips = provider.generate_tips(topic, level, 10)
        except Exception:
            mark_failure()
            return

        # save_cache merges and deduplicates automatically
        save_cache(new_tips, topic, level)
    finally:
        _release_lock()


if __name__ == "__main__":
    main()
