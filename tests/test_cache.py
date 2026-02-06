from __future__ import annotations

import time

from dev_tip.ai.cache import (
    clear_cache,
    get_cache_stats,
    is_on_cooldown,
    load_cache,
    mark_failure,
    save_cache,
)


def test_save_load_roundtrip(dev_tip_home):
    tips = [{"id": "t1", "body": "tip one"}, {"id": "t2", "body": "tip two"}]
    save_cache(tips, "python", "beginner")
    loaded = load_cache("python", "beginner")
    assert len(loaded) == 2
    assert loaded[0]["id"] == "t1"


def test_cache_never_expires(dev_tip_home):
    tips = [{"id": "t1", "body": "old"}]
    save_cache(tips, None, None)
    loaded = load_cache(None, None)
    assert len(loaded) == 1


def test_cooldown_backoff(dev_tip_home):
    assert not is_on_cooldown()
    mark_failure()
    assert is_on_cooldown()


def test_clear_cache(dev_tip_home):
    tips = [{"id": "t1", "body": "data"}]
    save_cache(tips, "git", None)
    assert len(load_cache("git", None)) == 1
    clear_cache()
    assert load_cache("git", None) == []


def test_dedup_on_save(dev_tip_home):
    tips = [{"id": "t1", "body": "first"}]
    save_cache(tips, "sql", None)
    save_cache(tips, "sql", None)  # duplicate
    loaded = load_cache("sql", None)
    assert len(loaded) == 1


def test_get_cache_stats_empty(dev_tip_home):
    stats = get_cache_stats()
    assert stats["keys"] == 0
    assert stats["total_tips"] == 0
    assert stats["cooldown_active"] is False


def test_get_cache_stats_with_data(dev_tip_home):
    save_cache([{"id": "a", "body": "x"}], "python", None)
    save_cache([{"id": "b", "body": "y"}], "git", "beginner")
    stats = get_cache_stats()
    assert stats["keys"] == 2
    assert stats["total_tips"] == 2
