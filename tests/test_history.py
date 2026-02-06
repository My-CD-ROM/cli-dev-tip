from __future__ import annotations

from dev_tip.history import _load_history, get_unseen, mark_seen


def test_mark_seen_and_unseen(dev_tip_home):
    tips = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    mark_seen("a")
    unseen = get_unseen(tips)
    ids = {t["id"] for t in unseen}
    assert "a" not in ids
    assert "b" in ids
    assert "c" in ids


def test_all_seen_resets(dev_tip_home):
    tips = [{"id": "a"}, {"id": "b"}]
    mark_seen("a")
    mark_seen("b")
    unseen = get_unseen(tips)
    # Reset keeps last tip, so only "a" should be unseen
    assert len(unseen) == 1
    assert unseen[0]["id"] == "a"


def test_no_duplicate_marks(dev_tip_home):
    mark_seen("x")
    mark_seen("x")
    history = _load_history()
    assert history.count("x") == 1
