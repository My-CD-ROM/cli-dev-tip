from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".dev-tip"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG = {
    "topic": None,
    "level": None,
    "ai_provider": None,
    "ai_model": None,
    "ai_key": None,
    "every_commands": 15,
    "every_minutes": 30,
    "quiet": False,
}

_TEMPLATE = """\
# dev-tip configuration

# Default topic filter (python, git, docker, sql, linux)
# topic = "python"

# Default level filter (beginner, intermediate, advanced)
# level = "beginner"

# AI-powered tip generation (free, requires API key in env var)
# ai_provider = "gemini"        # or "openrouter"
# ai_model = "gemini-2.0-flash"

# Periodic tip frequency
# every_commands = 15    # show a tip every N commands
# every_minutes = 30     # or every M minutes, whichever comes first

# Quiet mode — show tip body only, no header
# quiet = false
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


def _format_value(key: str, value: Any) -> str:
    """Format a config key-value pair for TOML output."""
    if isinstance(value, bool):
        return f'{key} = {"true" if value else "false"}'
    if isinstance(value, int):
        return f"{key} = {value}"
    return f'{key} = "{value}"'


def save_config(updates: dict[str, Any]) -> None:
    """Update specific keys in the config file, preserving comments."""
    config = load_config()
    config.update(updates)

    if CONFIG_FILE.exists():
        lines = CONFIG_FILE.read_text().splitlines()
    else:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        lines = _TEMPLATE.splitlines()

    # Update existing keys or uncomment commented keys
    written_keys: set[str] = set()
    for i, line in enumerate(lines):
        stripped = line.lstrip("# ").strip()
        for key, value in config.items():
            if value is None:
                continue
            if stripped.startswith(f"{key} =") or stripped.startswith(f"{key}="):
                lines[i] = _format_value(key, value)
                written_keys.add(key)
                break

    # Append any keys not found in existing lines
    for key, value in config.items():
        if value is not None and key not in written_keys:
            lines.append(_format_value(key, value))

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text("\n".join(lines) + "\n")
