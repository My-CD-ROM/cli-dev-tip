from __future__ import annotations

import random
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from dev_tip.config import load_config
from dev_tip.history import get_unseen, mark_seen
from dev_tip.hook import hook_app
from dev_tip.tips import filter_tips, load_tips

app = typer.Typer(invoke_without_command=True, add_completion=False)
app.add_typer(hook_app, name="hook")
console = Console()

TOPIC_EMOJI = {
    "python": "\U0001f40d",
    "git": "\U0001f500",
    "docker": "\U0001f433",
    "sql": "\U0001f4be",
    "linux": "\U0001f427",
}

LEVEL_STYLE = {
    "beginner": ("green", "Beginner"),
    "intermediate": ("yellow", "Intermediate"),
    "advanced": ("red", "Advanced"),
}


def _render_tip(tip: dict) -> None:
    """Display a tip with Rich formatting."""
    topic = tip["topic"]
    emoji = TOPIC_EMOJI.get(topic, "\U0001f4a1")
    color, level_label = LEVEL_STYLE.get(tip["level"], ("white", tip["level"]))

    title = Text()
    title.append(f"{emoji} ", style="bold")
    title.append(tip["title"], style="bold cyan")

    badge = Text(f" {level_label} ", style=f"bold white on {color}")

    body = tip["body"].strip()
    example = tip.get("example", "").strip()

    content = Text()
    content.append(body)
    if example:
        content.append("\n\n")
        content.append("Example:\n", style="bold")
        content.append(example, style="dim")

    panel = Panel(
        content,
        title=title,
        subtitle=badge,
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)


@app.callback()
def main(
    ctx: typer.Context,
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Filter by topic"),
    level: Optional[str] = typer.Option(None, "--level", "-l", help="Filter by level"),
) -> None:
    """Show a random developer tip."""
    if ctx.invoked_subcommand is not None:
        return

    config = load_config()
    topic = topic or config.get("topic")
    level = level or config.get("level")

    tips = load_tips()
    filtered = filter_tips(tips, topic=topic, level=level)

    if not filtered:
        console.print("[red]No tips found for the given filters.[/red]")
        raise typer.Exit(1)

    unseen = get_unseen(filtered)
    tip = random.choice(unseen)
    mark_seen(tip["id"])
    _render_tip(tip)
