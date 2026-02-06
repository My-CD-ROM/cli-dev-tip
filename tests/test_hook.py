from __future__ import annotations

from pathlib import Path

from dev_tip.hook import (
    HOOK_MARKER_END,
    HOOK_MARKER_START,
    _build_hook_block,
    _build_hook_command,
)


def test_build_hook_command_no_args():
    assert _build_hook_command() == "dev-tip"


def test_build_hook_command_all_args():
    cmd = _build_hook_command(provider="gemini", topic="python", level="advanced", quiet=True)
    assert "--provider gemini" in cmd
    assert "--topic python" in cmd
    assert "--level advanced" in cmd
    assert "--quiet" in cmd


def test_build_hook_block_zsh():
    block = _build_hook_block("zsh", "dev-tip", 15, 30)
    assert "precmd" in block
    assert "add-zsh-hook" in block
    assert "[ -f" in block
    assert ".paused" in block
    assert HOOK_MARKER_START in block
    assert HOOK_MARKER_END in block


def test_build_hook_block_bash():
    block = _build_hook_block("bash", "dev-tip", 15, 30)
    assert "PROMPT_COMMAND" in block
    assert "[ -f" in block
    assert ".paused" in block
    assert HOOK_MARKER_START in block
    assert HOOK_MARKER_END in block


def test_build_hook_block_embeds_values():
    block = _build_hook_block("zsh", "dev-tip --quiet", 5, 10)
    assert "_DEV_TIP_CMD_COUNT=5" in block
    assert ">= 5" in block
    assert ">= 10" in block
    assert "dev-tip --quiet" in block


def test_enable_disable_roundtrip(dev_tip_home, monkeypatch):
    from dev_tip.hook import disable, enable

    rc_file = dev_tip_home.parent / ".zshrc"
    rc_file.write_text("# existing content\n")
    monkeypatch.setattr("dev_tip.hook._get_rc_file", lambda: rc_file)
    monkeypatch.setattr("dev_tip.hook._detect_shell", lambda: "zsh")

    enable()
    content = rc_file.read_text()
    assert HOOK_MARKER_START in content
    assert "# existing content" in content

    disable()
    content = rc_file.read_text()
    assert HOOK_MARKER_START not in content
    assert "# existing content" in content
