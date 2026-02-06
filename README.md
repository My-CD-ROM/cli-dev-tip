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
uv tool install dev-tip
```

This makes `dev-tip` available globally from any terminal. No extra packages needed.

## Quick start

Show a tip on every new terminal session:

```bash
# Static tips (125 built in, works offline)
dev-tip enable

# With AI — fresh tips generated via Gemini (free)
dev-tip enable --provider gemini --key YOUR_GEMINI_API_KEY

# With AI + filters
dev-tip enable --provider gemini --key YOUR_KEY --topic python --level advanced

# Disable
dev-tip disable
```

Get a free Gemini API key at https://aistudio.google.com or a free OpenRouter key at https://openrouter.ai/keys.

## Usage

One-off tips from the command line:

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

# Use AI provider for a one-off tip
dev-tip --provider gemini --key YOUR_KEY --topic kubernetes
```

### Options

| Option | Short | Description | Default |
|---|---|---|---|
| `--topic` | `-t` | Filter tips by topic | All topics |
| `--level` | `-l` | Filter tips by difficulty | All levels |
| `--provider` | `-p` | AI provider (gemini, openrouter) | None |
| `--key` | `-k` | API key for the AI provider | Config or env var |

### Available topics

| Topic | Count |
|---|---|
| `python` | 15 |
| `git` | 15 |
| `docker` | 15 |
| `sql` | 15 |
| `linux` | 15 |
| `kubernetes` | 10 |
| `vim` | 10 |
| `javascript` | 10 |
| `terraform` | 10 |
| `rust` | 10 |

125 tips built in. With AI enabled, any topic works and tips are generated fresh.

### Difficulty levels

| Level | Description |
|---|---|
| `beginner` | Fundamentals and common patterns |
| `intermediate` | Deeper concepts and useful tricks |
| `advanced` | Expert techniques and edge cases |

## AI-powered tips

Generate fresh tips dynamically instead of using the built-in collection. Both providers are free.

| Provider | Default model | Free key |
|---|---|---|
| `gemini` | `gemini-2.0-flash` | https://aistudio.google.com |
| `openrouter` | `google/gemini-2.0-flash-exp:free` | https://openrouter.ai/keys |

### How it works

- Generates 10 tips per API call and caches them locally (`~/.dev-tip/ai_cache.json`)
- Cache lasts 24 hours, then refreshes on next run
- Cache invalidates when you change topic or level filters
- Falls back to static tips silently on any error (bad key, network failure, rate limit)

## Status

Early development — not yet published to PyPI.
