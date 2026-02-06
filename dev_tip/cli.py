from __future__ import annotations

import random
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from dev_tip.config import load_config
from dev_tip.history import all_seen, get_unseen, mark_seen
from dev_tip.hook import disable as hook_disable
from dev_tip.hook import enable as hook_enable
from dev_tip.tips import filter_tips, load_tips

app = typer.Typer(invoke_without_command=True, add_completion=False)
console = Console()

TOPIC_EMOJI = {
    "python": "\U0001f40d",
    "git": "\U0001f500",
    "docker": "\U0001f433",
    "sql": "\U0001f4be",
    "linux": "\U0001f427",
    "kubernetes": "\u2638\ufe0f",
    "vim": "\U0001f4dd",
    "javascript": "\U0001f7e8",
    "terraform": "\U0001f3d7\ufe0f",
    "rust": "\U0001f980",
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
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI provider (gemini, openrouter)"),
    key: Optional[str] = typer.Option(None, "--key", "-k", help="API key for the AI provider"),
) -> None:
    """Show a random developer tip."""
    if ctx.invoked_subcommand is not None:
        return

    config = load_config()
    topic = topic or config.get("topic")
    level = level or config.get("level")
    if provider:
        config["ai_provider"] = provider
    if key:
        config["ai_key"] = key

    ai_provider = config.get("ai_provider")
    if ai_provider:
        from dev_tip.ai import get_ai_tip

        tip = get_ai_tip(topic=topic, level=level, config=config)
        if tip is not None:
            mark_seen(tip["id"])
            _render_tip(tip)
            return

    tips = load_tips()
    filtered = filter_tips(tips, topic=topic, level=level)

    if not filtered:
        console.print("[red]No tips found for the given filters.[/red]")
        raise typer.Exit(1)

    if not ai_provider and all_seen(filtered):
        console.print(
            "[dim]You've seen all tips! For unlimited fresh tips, set up free AI generation:"
            "\nhttps://aistudio.google.com[/dim]\n"
        )

    unseen = get_unseen(filtered)
    tip = random.choice(unseen)
    mark_seen(tip["id"])
    _render_tip(tip)


@app.command()
def enable(
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI provider (gemini, openrouter)"),
    key: Optional[str] = typer.Option(None, "--key", "-k", help="API key for the AI provider"),
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Default topic filter"),
    level: Optional[str] = typer.Option(None, "--level", "-l", help="Default level filter"),
) -> None:
    """Enable the shell hook (show a tip on every new terminal)."""
    hook_enable(provider=provider, key=key, topic=topic, level=level)


@app.command()
def disable() -> None:
    """Disable the shell hook."""
    hook_disable()
