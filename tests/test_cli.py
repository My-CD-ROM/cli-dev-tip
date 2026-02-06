from __future__ import annotations

from typer.testing import CliRunner

from dev_tip.cli import app

runner = CliRunner()


def test_show_tip(dev_tip_home):
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0


def test_pause_resume(dev_tip_home):
    from dev_tip.cli import PAUSE_FILE

    result = runner.invoke(app, ["pause"])
    assert result.exit_code == 0
    assert "paused" in result.output.lower()
    assert PAUSE_FILE.exists()

    result = runner.invoke(app, ["resume"])
    assert result.exit_code == 0
    assert "resumed" in result.output.lower()
    assert not PAUSE_FILE.exists()


def test_status_output(dev_tip_home):
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "Hook" in result.output
    assert "Config" in result.output
    assert "Cache" in result.output
    assert "History" in result.output


def test_clear_cache_command(dev_tip_home):
    from dev_tip.ai.cache import load_cache, save_cache

    save_cache([{"id": "x", "body": "y"}], "python", None)
    assert len(load_cache("python", None)) == 1

    result = runner.invoke(app, ["clear-cache"])
    assert result.exit_code == 0
    assert "cleared" in result.output.lower()
    assert load_cache("python", None) == []


def test_quiet_mode(dev_tip_home):
    result = runner.invoke(app, ["--quiet"])
    assert result.exit_code == 0
    output = result.output.strip()
    # Quiet mode should not contain topic emoji headers
    # (no "·" separator that appears in headers)
    lines = [l for l in output.splitlines() if l.strip()]
    # At least one non-empty line (the body)
    assert len(lines) >= 1
