from __future__ import annotations

import random
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from dev_tip.config import CONFIG_DIR, load_config
from dev_tip.history import all_seen, get_unseen, mark_seen
from dev_tip.hook import disable as hook_disable
from dev_tip.hook import enable as hook_enable
from dev_tip.tips import filter_tips, load_tips

app = typer.Typer(invoke_without_command=True, add_completion=False)
console = Console()

PAUSE_FILE = CONFIG_DIR / ".paused"

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


def _render_tip(tip: dict, quiet: bool = False) -> None:
    """Display a tip as a compact, dim, right-floated block."""
    console.print()  # breathing room between shell output and tip

    body = tip["body"].strip()
    wrap_width = min(console.width, 60)
    term_w = console.width
    pad = term_w - wrap_width

    if quiet:
        body_lines = textwrap.wrap(body, width=wrap_width)
        for line in body_lines:
            console.print(" " * max(pad, 0) + line, style="dim", highlight=False)
        return

    topic = tip["topic"]
    emoji = TOPIC_EMOJI.get(topic, "\U0001f4a1")
    header = f"{emoji} {topic} \u00b7 {tip['level']} \u00b7 {tip['title']}"

    header_lines = textwrap.wrap(header, width=wrap_width)
    body_lines = textwrap.wrap(body, width=wrap_width)

    block = header_lines + [""] + body_lines
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
    quiet: Optional[bool] = typer.Option(False, "--quiet", "-q", help="Show tip body only, no header"),
) -> None:
    """Show a random developer tip."""
    if ctx.invoked_subcommand is not None:
        return

    config = load_config()
    topic = topic or config.get("topic")
    level = level or config.get("level")
    quiet = quiet or config.get("quiet", False)
    if provider:
        config["ai_provider"] = provider
    if key:
        config["ai_key"] = key

    ai_provider = config.get("ai_provider")

    # Validate topic/level
    from dev_tip.tips import VALID_LEVELS, VALID_TOPICS

    if topic and topic not in VALID_TOPICS and not ai_provider:
        console.print(
            f"[yellow]Unknown topic '{topic}'. "
            f"Available: {', '.join(sorted(VALID_TOPICS))}[/yellow]"
        )
    if level and level not in VALID_LEVELS:
        console.print(
            f"[yellow]Unknown level '{level}'. "
            f"Available: {', '.join(sorted(VALID_LEVELS))}[/yellow]"
        )

    if ai_provider:
        from dev_tip.ai import get_ai_tip

        tip, unseen_count = get_ai_tip(topic=topic, level=level, config=config)
        if tip is not None:
            mark_seen(tip["id"])
            _render_tip(tip, quiet=quiet)
            _maybe_prefetch(topic, level, unseen_count)
            return

    tips = load_tips()
    filtered = filter_tips(tips, topic=topic, level=level)

    if not filtered:
        # Topic may only exist for AI — drop topic filter, keep level
        filtered = filter_tips(tips, level=level)

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
    _render_tip(tip, quiet=quiet)


@app.command()
def enable(
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI provider (gemini, openrouter)"),
    key: Optional[str] = typer.Option(None, "--key", "-k", help="API key for the AI provider"),
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Default topic filter"),
    level: Optional[str] = typer.Option(None, "--level", "-l", help="Default level filter"),
    every_commands: Optional[int] = typer.Option(None, "--every-commands", help="Show tip every N commands (default: 15)"),
    every_minutes: Optional[int] = typer.Option(None, "--every-minutes", help="Show tip every N minutes (default: 30)"),
    quiet: Optional[bool] = typer.Option(False, "--quiet", "-q", help="Show tip body only, no header"),
) -> None:
    """Enable the shell hook (show a tip on every new terminal)."""
    hook_enable(
        provider=provider,
        key=key,
        topic=topic,
        level=level,
        every_commands=every_commands,
        every_minutes=every_minutes,
        quiet=quiet or False,
    )


@app.command()
def disable() -> None:
    """Disable the shell hook."""
    hook_disable()


@app.command()
def pause() -> None:
    """Pause tips (keeps hook installed, stops showing tips)."""
    PAUSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    PAUSE_FILE.touch()
    console.print("[yellow]Tips paused.[/yellow] Run [bold]dev-tip resume[/bold] to continue.")


@app.command()
def resume() -> None:
    """Resume showing tips."""
    PAUSE_FILE.unlink(missing_ok=True)
    console.print("[green]Tips resumed.[/green]")


@app.command("clear-cache")
def clear_cache() -> None:
    """Clear cached AI tips (forces fresh generation on next run)."""
    from dev_tip.ai.cache import clear_cache as do_clear

    do_clear()
    console.print("[green]AI cache cleared.[/green]")


@app.command()
def status() -> None:
    """Show current dev-tip configuration and status."""
    from dev_tip.ai.cache import get_cache_stats
    from dev_tip.history import _load_history
    from dev_tip.hook import HOOK_MARKER_START, PAUSE_FILE, _get_rc_file

    config = load_config()
    rc_file = _get_rc_file()

    # Hook status
    hook_installed = False
    if rc_file.exists():
        hook_installed = HOOK_MARKER_START in rc_file.read_text()

    paused = PAUSE_FILE.exists()

    console.print("[bold]dev-tip status[/bold]\n")

    # Hook
    hook_label = "[green]installed[/green]" if hook_installed else "[yellow]not installed[/yellow]"
    console.print(f"  Hook:    {hook_label} ({rc_file.name})")

    # Paused
    paused_label = "[yellow]yes[/yellow]" if paused else "[green]no[/green]"
    console.print(f"  Paused:  {paused_label}")

    # Config
    console.print()
    console.print("[bold]  Config[/bold]")
    console.print(f"    topic:          {config.get('topic') or '[dim]any[/dim]'}")
    console.print(f"    level:          {config.get('level') or '[dim]any[/dim]'}")
    console.print(f"    every_commands: {config.get('every_commands')}")
    console.print(f"    every_minutes:  {config.get('every_minutes')}")
    console.print(f"    quiet:          {config.get('quiet', False)}")

    # AI
    ai_provider = config.get("ai_provider")
    console.print()
    console.print("[bold]  AI[/bold]")
    if ai_provider:
        console.print(f"    provider: {ai_provider}")
        console.print(f"    model:    {config.get('ai_model') or '[dim]default[/dim]'}")
        ai_key = config.get("ai_key")
        if ai_key:
            masked = ai_key[:4] + "..." + ai_key[-4:] if len(ai_key) > 8 else "***"
            console.print(f"    key:      {masked}")
        else:
            console.print("    key:      [dim]from env var[/dim]")
    else:
        console.print("    [dim]not configured (using static tips)[/dim]")

    # Cache
    stats = get_cache_stats()
    console.print()
    console.print("[bold]  Cache[/bold]")
    console.print(f"    cached keys:  {stats['keys']}")
    console.print(f"    total tips:   {stats['total_tips']}")
    cooldown = "[yellow]yes[/yellow]" if stats["cooldown_active"] else "no"
    console.print(f"    cooldown:     {cooldown}")

    # History
    history = _load_history()
    console.print()
    console.print("[bold]  History[/bold]")
    console.print(f"    tips seen: {len(history)}")
