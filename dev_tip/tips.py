from __future__ import annotations

import random
from importlib.resources import files
from typing import Optional

import yaml


def load_tips() -> list[dict]:
    """Load all tips from the bundled YAML file."""
    tip_file = files("dev_tip.data").joinpath("tips.yaml")
    return yaml.safe_load(tip_file.read_text())


def filter_tips(
    tips: list[dict],
    topic: Optional[str] = None,
    level: Optional[str] = None,
) -> list[dict]:
    """Filter tips by topic and/or level."""
    filtered = tips
    if topic:
        filtered = [t for t in filtered if t["topic"] == topic]
    if level:
        filtered = [t for t in filtered if t["level"] == level]
    return filtered


def get_random_tip(
    tips: list[dict],
    topic: Optional[str] = None,
    level: Optional[str] = None,
) -> Optional[dict]:
    """Return a random tip matching the given filters, or None if no match."""
    filtered = filter_tips(tips, topic=topic, level=level)
    if not filtered:
        return None
    return random.choice(filtered)
