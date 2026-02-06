from __future__ import annotations

from pathlib import Path

from rich.console import Console

HOOK_MARKER_START = "# >>> dev-tip hook >>>"
HOOK_MARKER_END = "# <<< dev-tip hook <<<"

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
) -> str:
    """Build the dev-tip command for the shell hook."""
    parts = ["dev-tip"]
    if provider:
        parts.append(f"--provider {provider}")
    if topic:
        parts.append(f"--topic {topic}")
    if level:
        parts.append(f"--level {level}")
    return " ".join(parts)


def enable(
    provider: str | None = None,
    key: str | None = None,
    topic: str | None = None,
    level: str | None = None,
) -> None:
    """Install the shell hook into the user's rc file."""
    # Save AI config if provided
    if provider or key or topic or level:
        from dev_tip.config import save_config

        updates = {}
        if provider:
            updates["ai_provider"] = provider
        if key:
            updates["ai_key"] = key
        if topic:
            updates["topic"] = topic
        if level:
            updates["level"] = level
        save_config(updates)

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

    cmd = _build_hook_command(provider, topic, level)
    hook_block = f"{HOOK_MARKER_START}\n{cmd} 2>/dev/null\n{HOOK_MARKER_END}\n"
    content = content.rstrip() + "\n\n" + hook_block
    rc_file.write_text(content)

    console.print(f"[green]Hook installed in {rc_file}[/green]")
    console.print("A tip will appear every time you open a new terminal.")
    console.print(f"Restart your {shell} or run: [bold]source {rc_file}[/bold]")


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
