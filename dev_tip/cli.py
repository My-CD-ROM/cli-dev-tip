from __future__ import annotations

import random
import subprocess
import sys
import textwrap
from typing import Optional

import typer
from rich.console import Console

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

def _render_tip(tip: dict) -> None:
    """Display a tip as a compact, dim, right-floated block."""
    topic = tip["topic"]
    emoji = TOPIC_EMOJI.get(topic, "\U0001f4a1")
    header = f"{emoji} {topic} \u00b7 {tip['level']} \u00b7 {tip['title']}"

    body = tip["body"].strip()
    wrap_width = min(console.width, 60)
    lines = textwrap.wrap(body, width=wrap_width)

    # Fixed-width block, right-floated against terminal edge.
    term_w = console.width
    block = [header] + lines
    pad = term_w - wrap_width
    for line in block:
        console.print(" " * max(pad, 0) + line, style="dim", highlight=False)


def _maybe_prefetch(topic: str | None, level: str | None, unseen_count: int) -> None:
    """Spawn a background prefetch if the cache is running low."""
    from dev_tip.ai.cache import cache_needs_refill

    if not cache_needs_refill(topic, level, unseen_count):
        return

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
    except OSError:
        pass


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

        tip, unseen_count = get_ai_tip(topic=topic, level=level, config=config)
        if tip is not None:
            mark_seen(tip["id"])
            _render_tip(tip)
            _maybe_prefetch(topic, level, unseen_count)
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
