from __future__ import annotations

from dev_tip.tips import VALID_LEVELS, VALID_TOPICS, filter_tips, load_tips


def test_load_tips_returns_list():
    tips = load_tips()
    assert isinstance(tips, list)
    assert len(tips) > 0
    assert "id" in tips[0]


def test_filter_by_topic():
    tips = load_tips()
    python_tips = filter_tips(tips, topic="python")
    assert all(t["topic"] == "python" for t in python_tips)
    assert len(python_tips) > 0


def test_filter_by_level():
    tips = load_tips()
    beginner = filter_tips(tips, level="beginner")
    assert all(t["level"] == "beginner" for t in beginner)
    assert len(beginner) > 0


def test_filter_no_match():
    tips = load_tips()
    result = filter_tips(tips, topic="nonexistent")
    assert result == []


def test_valid_topics_constant():
    """VALID_TOPICS should match the actual topics in bundled tips."""
    tips = load_tips()
    actual_topics = {t["topic"] for t in tips}
    assert actual_topics == VALID_TOPICS


def test_valid_levels_constant():
    assert VALID_LEVELS == {"beginner", "intermediate", "advanced"}
