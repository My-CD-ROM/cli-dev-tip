from __future__ import annotations

from dev_tip.config import _format_value, load_config, save_config


def test_load_default_config(dev_tip_home):
    """Loading config when no file exists creates template and returns defaults."""
    config = load_config()
    assert config["every_commands"] == 15
    assert config["every_minutes"] == 30
    assert config["quiet"] is False
    assert config["topic"] is None
    # Template file should exist now
    assert (dev_tip_home / "config.toml").exists()


def test_save_and_load_roundtrip(dev_tip_home):
    """Saved values survive a load roundtrip."""
    save_config({"topic": "python", "every_commands": 5, "quiet": True})
    config = load_config()
    assert config["topic"] == "python"
    assert config["every_commands"] == 5
    assert config["quiet"] is True


def test_save_preserves_comments(dev_tip_home):
    """Comments in the config template survive save_config."""
    load_config()  # creates template
    save_config({"topic": "git"})
    text = (dev_tip_home / "config.toml").read_text()
    assert "# dev-tip configuration" in text
    assert 'topic = "git"' in text


def test_format_value_types():
    """_format_value handles bool, int, and string correctly."""
    assert _format_value("quiet", True) == "quiet = true"
    assert _format_value("quiet", False) == "quiet = false"
    assert _format_value("every_commands", 10) == "every_commands = 10"
    assert _format_value("topic", "python") == 'topic = "python"'
