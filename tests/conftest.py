from __future__ import annotations

import pytest
from pathlib import Path


@pytest.fixture()
def dev_tip_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect all dev-tip file I/O to a temp directory."""
    home = tmp_path / "home"
    home.mkdir()
    config_dir = home / ".dev-tip"
    config_dir.mkdir()

    monkeypatch.setattr("dev_tip.config.CONFIG_DIR", config_dir)
    monkeypatch.setattr("dev_tip.config.CONFIG_FILE", config_dir / "config.toml")
    monkeypatch.setattr("dev_tip.history.HISTORY_DIR", config_dir)
    monkeypatch.setattr("dev_tip.history.HISTORY_FILE", config_dir / "history.json")
    monkeypatch.setattr("dev_tip.ai.cache.CACHE_DIR", config_dir)
    monkeypatch.setattr("dev_tip.ai.cache.CACHE_FILE", config_dir / "ai_cache.json")
    monkeypatch.setattr("dev_tip.hook.PAUSE_FILE", config_dir / ".paused")
    monkeypatch.setattr("dev_tip.cli.PAUSE_FILE", config_dir / ".paused")
    return config_dir
