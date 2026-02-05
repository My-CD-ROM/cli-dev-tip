# dev-tip

A terminal tool that helps developers learn continuously by showing bite-sized technical tips - right in the terminal, between commands.

## What it does

- Shows random developer tips on topics like Python, Git, Docker, SQL, and more
- Filters by topic or difficulty level
- Remembers what you've seen so you don't get repeats
- Hooks into your shell to show tips automatically every N commands
- Stays out of the way - never interrupts what you're doing

## Usage

```bash
# Show a random tip
dev-tip

# Filter by topic
dev-tip --topic python

# Filter by difficulty
dev-tip --level beginner

# Auto-show a tip every 20 commands
dev-tip hook install --every 20
```

## Installation

```bash
pip install dev-tip
# or
pipx install dev-tip
```

## Status

Early development - not yet published to PyPI.
