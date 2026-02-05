from __future__ import annotations

from pathlib import Path

from rich.console import Console

HOOK_MARKER_START = "# >>> dev-tip hook >>>"
HOOK_MARKER_END = "# <<< dev-tip hook <<<"

HOOK_BLOCK = """\
# >>> dev-tip hook >>>
dev-tip 2>/dev/null
# <<< dev-tip hook <<<
"""

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


def enable() -> None:
    """Install the shell hook into the user's rc file."""
    rc_file = _get_rc_file()
    shell = _detect_shell()

    if rc_file.exists():
        content = rc_file.read_text()
        if HOOK_MARKER_START in content:
            console.print(
                f"[yellow]Hook already installed in {rc_file}. "
                "Run 'dev-tip disable' first to reinstall.[/yellow]"
            )
            return
    else:
        content = ""

    content = content.rstrip() + "\n\n" + HOOK_BLOCK
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
