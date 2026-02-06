from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from textwrap import dedent

from rich.console import Console

from dev_tip.config import CONFIG_DIR, DEFAULT_CONFIG

HOOK_MARKER_START = "# >>> dev-tip hook >>>"
HOOK_MARKER_END = "# <<< dev-tip hook <<<"
PAUSE_FILE = CONFIG_DIR / ".paused"

console = Console()


def _detect_shell() -> str:
    """Detect whether user is running zsh or bash."""
    import os

    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    return "bash"


def _get_rc_file() -> Path:
    """Detect the user's shell rc file."""
    shell = _detect_shell()
    if shell == "zsh":
        return Path.home() / ".zshrc"
    return Path.home() / ".bashrc"


def _build_hook_command(
    provider: str | None = None,
    topic: str | None = None,
    level: str | None = None,
    quiet: bool = False,
) -> str:
    """Build the dev-tip command for the shell hook."""
    parts = ["dev-tip"]
    if provider:
        parts.append(f"--provider {provider}")
    if topic:
        parts.append(f"--topic {topic}")
    if level:
        parts.append(f"--level {level}")
    if quiet:
        parts.append("--quiet")
    return " ".join(parts)


def _build_hook_block(
    shell: str,
    cmd: str,
    every_commands: int,
    every_minutes: int,
) -> str:
    """Wrap the dev-tip command in a periodic shell function."""
    pause_path = PAUSE_FILE
    if shell == "zsh":
        return dedent(f"""\
            {HOOK_MARKER_START}
            _DEV_TIP_CMD_COUNT={every_commands}
            _DEV_TIP_LAST_SEC=$SECONDS
            _dev_tip_precmd() {{
                [ -f {pause_path} ] && return
                _DEV_TIP_CMD_COUNT=$((_DEV_TIP_CMD_COUNT + 1))
                if (( _DEV_TIP_CMD_COUNT >= {every_commands} || (SECONDS - _DEV_TIP_LAST_SEC) / 60 >= {every_minutes} )); then
                    {cmd} 2>/dev/null
                    _DEV_TIP_CMD_COUNT=0
                    _DEV_TIP_LAST_SEC=$SECONDS
                fi
            }}
            autoload -Uz add-zsh-hook
            add-zsh-hook precmd _dev_tip_precmd
            {HOOK_MARKER_END}
        """)
    # bash
    return dedent(f"""\
        {HOOK_MARKER_START}
        _DEV_TIP_CMD_COUNT={every_commands}
        _DEV_TIP_LAST_SEC=$SECONDS
        _dev_tip_prompt() {{
            [ -f {pause_path} ] && return
            _DEV_TIP_CMD_COUNT=$((_DEV_TIP_CMD_COUNT + 1))
            if (( _DEV_TIP_CMD_COUNT >= {every_commands} || (SECONDS - _DEV_TIP_LAST_SEC) / 60 >= {every_minutes} )); then
                {cmd} 2>/dev/null
                _DEV_TIP_CMD_COUNT=0
                _DEV_TIP_LAST_SEC=$SECONDS
            fi
        }}
        PROMPT_COMMAND="_dev_tip_prompt${{PROMPT_COMMAND:+;$PROMPT_COMMAND}}"
        {HOOK_MARKER_END}
    """)


def enable(
    provider: str | None = None,
    key: str | None = None,
    topic: str | None = None,
    level: str | None = None,
    every_commands: int | None = None,
    every_minutes: int | None = None,
    quiet: bool = False,
) -> None:
    """Install the shell hook into the user's rc file."""
    from dev_tip.config import save_config

    every_commands = every_commands or DEFAULT_CONFIG["every_commands"]
    every_minutes = every_minutes or DEFAULT_CONFIG["every_minutes"]

    # Save config if anything provided
    updates: dict = {}
    if provider:
        updates["ai_provider"] = provider
    if key:
        updates["ai_key"] = key
    if topic:
        updates["topic"] = topic
    if level:
        updates["level"] = level
    updates["every_commands"] = every_commands
    updates["every_minutes"] = every_minutes
    if quiet:
        updates["quiet"] = True
    save_config(updates)

    # Pre-cache AI tips so the first shell prompt is instant
    if provider and key:
        topic_arg = str(topic) if topic is not None else "null"
        level_arg = str(level) if level is not None else "null"
        try:
            subprocess.Popen(
                [sys.executable, "-m", "dev_tip.prefetch", topic_arg, level_arg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
            console.print("[dim]Pre-caching AI tips in the background...[/dim]")
        except OSError:
            pass

    rc_file = _get_rc_file()
    shell = _detect_shell()

    # Remove existing hook first (so re-running enable updates it)
    if rc_file.exists():
        content = rc_file.read_text()
        if HOOK_MARKER_START in content:
            start = content.index(HOOK_MARKER_START)
            end = content.index(HOOK_MARKER_END) + len(HOOK_MARKER_END)
            content = content[:start].rstrip() + content[end:].lstrip("\n")
    else:
        content = ""

    cmd = _build_hook_command(provider, topic, level, quiet=quiet)
    hook_block = _build_hook_block(shell, cmd, every_commands, every_minutes)
    content = content.rstrip() + "\n\n" + hook_block
    rc_file.write_text(content)

    console.print(f"[green]Hook installed in {rc_file}[/green]")
    console.print(
        f"Tips will appear every {every_commands} commands "
        f"or {every_minutes} minutes."
    )
    console.print(f"Reload your shell: [bold]exec {shell}[/bold]")


def disable() -> None:
    """Remove the shell hook from the user's rc file."""
    rc_file = _get_rc_file()

    if not rc_file.exists():
        console.print("[yellow]No rc file found.[/yellow]")
        return

    content = rc_file.read_text()
    if HOOK_MARKER_START not in content:
        console.print("[yellow]Hook not found — nothing to remove.[/yellow]")
        return

    start = content.index(HOOK_MARKER_START)
    end = content.index(HOOK_MARKER_END) + len(HOOK_MARKER_END)
    cleaned = content[:start].rstrip() + content[end:].lstrip("\n")
    rc_file.write_text(cleaned)

    console.print(f"[green]Hook removed from {rc_file}[/green]")
