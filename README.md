# dev-tip

A terminal tool that helps developers learn continuously by showing bite-sized technical tips — right in the terminal, between commands.

## What it does

- Shows random developer tips on topics like Python, Git, Docker, SQL, and Linux
- Filters by topic or difficulty level
- Remembers what you've seen so you don't get repeats
- Hooks into your shell to show tips on every new terminal
- Optional AI-powered tip generation via Gemini or OpenRouter (free, no extra packages needed)
- Stays out of the way — never interrupts what you're doing

## Installation

```bash
uv pip install dev-tip
```

No extra packages needed — AI support uses Python's built-in `urllib`.

## Usage

```bash
# Show a random tip (all topics, all levels)
dev-tip

# Filter by topic
dev-tip --topic python
dev-tip -t git

# Filter by difficulty level
dev-tip --level beginner
dev-tip -l advanced

# Combine filters
dev-tip --topic docker --level intermediate
```

### Options

| Option | Short | Description | Default |
|---|---|---|---|
| `--topic` | `-t` | Filter tips by topic | All topics |
| `--level` | `-l` | Filter tips by difficulty | All levels |

### Available topics (static tips)

| Topic | Count |
|---|---|
| `python` | 10 |
| `git` | 10 |
| `docker` | 10 |
| `sql` | 10 |
| `linux` | 10 |

With AI enabled, any topic works (e.g. `kubernetes`, `rust`, `terraform`).

### Difficulty levels

| Level | Description |
|---|---|
| `beginner` | Fundamentals and common patterns |
| `intermediate` | Deeper concepts and useful tricks |
| `advanced` | Expert techniques and edge cases |

## Shell hook

Show a tip automatically on every new terminal session:

```bash
# Enable
dev-tip enable

# Disable
dev-tip disable
```

## Configuration

Config file: `~/.dev-tip/config.toml` (auto-created on first run)

```toml
# Default topic filter
# topic = "python"

# Default level filter
# level = "beginner"

# AI-powered tip generation (free, requires API key in env var)
# ai_provider = "gemini"        # or "openrouter"
# ai_model = "gemini-2.0-flash"
```

## AI-powered tips

Generate fresh tips dynamically instead of using the static collection. Both providers are free.

### Setup

1. Set the provider in your config:

```toml
# ~/.dev-tip/config.toml
ai_provider = "gemini"   # or "openrouter"
```

2. Export your API key:

```bash
# Gemini (free from https://aistudio.google.com)
export GEMINI_API_KEY="your-key-here"

# OpenRouter (free, 50 req/day — https://openrouter.ai/keys)
export OPENROUTER_API_KEY="your-key-here"
```

### AI models

| Provider | Default model | Override via |
|---|---|---|
| `gemini` | `gemini-2.0-flash` | `ai_model` in config |
| `openrouter` | `google/gemini-2.0-flash-exp:free` | `ai_model` in config |

To use a different model:

```toml
ai_provider = "openrouter"
ai_model = "meta-llama/llama-3-8b-instruct:free"
```

### How it works

- Generates 10 tips per API call and caches them locally (`~/.dev-tip/ai_cache.json`)
- Cache lasts 24 hours, then refreshes on next run
- Cache invalidates when you change topic or level filters
- Falls back to static tips silently on any error (bad key, network failure, rate limit)

## Status

Early development — not yet published to PyPI.
