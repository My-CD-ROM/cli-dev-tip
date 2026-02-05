from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".dev-tip"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG = {
    "topic": None,
    "level": None,
}

_TEMPLATE = """\
# dev-tip configuration

# Default topic filter (python, git, docker, sql, linux)
# topic = "python"

# Default level filter (beginner, intermediate, advanced)
# level = "beginner"
"""


def load_config() -> dict[str, Any]:
    """Load config from ~/.dev-tip/config.toml, creating it if missing."""
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(_TEMPLATE)
        return dict(DEFAULT_CONFIG)

    with open(CONFIG_FILE, "rb") as f:
        raw = tomllib.load(f)

    config = dict(DEFAULT_CONFIG)
    for key in DEFAULT_CONFIG:
        if key in raw:
            config[key] = raw[key]
    return config
