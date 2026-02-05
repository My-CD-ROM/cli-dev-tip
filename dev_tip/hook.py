from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from dev_tip.config import CONFIG_DIR, load_config

hook_app = typer.Typer(help="Manage shell hook")
console = Console()

COUNTER_FILE = CONFIG_DIR / ".counter"

HOOK_MARKER_START = "# >>> dev-tip hook >>>"
HOOK_MARKER_END = "# <<< dev-tip hook <<<"

HOOK_SCRIPT = """\
# >>> dev-tip hook >>>
__dev_tip_precmd() {
    local counter_file="$HOME/.dev-tip/.counter"
    local freq="${DEV_TIP_FREQUENCY:-__FREQUENCY__}"
    mkdir -p "$HOME/.dev-tip"
    local count=0
    [ -f "$counter_file" ] && count=$(cat "$counter_file")
    count=$((count + 1))
    if [ "$count" -ge "$freq" ]; then
        dev-tip 2>/dev/null
        count=0
    fi
    echo "$count" > "$counter_file"
}
"""

ZSH_HOOK = """\
precmd_functions+=(__dev_tip_precmd)
# <<< dev-tip hook <<<
"""

BASH_HOOK = """\
PROMPT_COMMAND="__dev_tip_precmd;${PROMPT_COMMAND}"
# <<< dev-tip hook <<<
"""


def _get_rc_file() -> Path:
    """Detect the user's shell rc file."""
    shell = _detect_shell()
    if shell == "zsh":
        return Path.home() / ".zshrc"
    return Path.home() / ".bashrc"


def _detect_shell() -> str:
    """Detect whether user is running zsh or bash."""
    import os

    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    return "bash"


def _build_hook_block(frequency: int) -> str:
    """Build the full hook block for the detected shell."""
    shell = _detect_shell()
    base = HOOK_SCRIPT.replace("__FREQUENCY__", str(frequency))
    if shell == "zsh":
        return base + ZSH_HOOK
    return base + BASH_HOOK


@hook_app.command("install")
def install(
    every: int = typer.Option(None, "--every", "-e", help="Show tip every N commands"),
) -> None:
    """Install the shell hook into your shell rc file."""
    config = load_config()
    frequency = every or config.get("hook_frequency", 20)

    rc_file = _get_rc_file()
    shell = _detect_shell()

    if rc_file.exists():
        content = rc_file.read_text()
        if HOOK_MARKER_START in content:
            console.print(
                f"[yellow]Hook already installed in {rc_file}. "
                "Run 'dev-tip hook uninstall' first to reinstall.[/yellow]"
            )
            return
    else:
        content = ""

    hook_block = _build_hook_block(frequency)
    content = content.rstrip() + "\n\n" + hook_block
    rc_file.write_text(content)

    console.print(f"[green]Hook installed in {rc_file}[/green]")
    console.print(f"A tip will appear every [bold]{frequency}[/bold] commands.")
    console.print(f"Restart your {shell} or run: [bold]source {rc_file}[/bold]")


@hook_app.command("uninstall")
def uninstall() -> None:
    """Remove the shell hook from your shell rc file."""
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

    # Clean up counter file
    if COUNTER_FILE.exists():
        COUNTER_FILE.unlink()

    console.print(f"[green]Hook removed from {rc_file}[/green]")
