from __future__ import annotations

import json
import re
import secrets


def build_prompt(topic: str | None, level: str | None, count: int) -> str:
    """Build a prompt requesting a JSON array of developer tips."""
    constraints = []
    if topic:
        constraints.append(f'- Topic must be "{topic}"')
    if level:
        constraints.append(f'- Level must be "{level}" (beginner, intermediate, or advanced)')

    constraint_block = "\n".join(constraints) if constraints else "- Any topic and level"

    return f"""\
Generate {count} concise, practical developer tips as a JSON array.

Constraints:
{constraint_block}

Each tip must be a JSON object with exactly these keys:
- "topic": lowercase topic name (e.g. "python", "git", "docker", "sql", "linux", "kubernetes")
- "title": short title (under 60 chars)
- "body": 1-3 sentence explanation
- "example": a short code snippet or command example (can be empty string)
- "level": one of "beginner", "intermediate", "advanced"
- "source": "ai"

Respond with ONLY a JSON array, no markdown fencing or extra text."""


def parse_response(text: str) -> list[dict]:
    """Parse an AI response into a list of validated tip dicts."""
    # Strip markdown code fencing if present
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    tips = json.loads(cleaned)
    if not isinstance(tips, list):
        raise ValueError("Expected a JSON array of tips")

    required_keys = {"topic", "title", "body", "level"}
    validated = []
    for tip in tips:
        if not isinstance(tip, dict):
            continue
        if not required_keys.issubset(tip.keys()):
            continue
        tip["id"] = f"ai-{secrets.token_hex(4)}"
        tip["source"] = "ai"
        tip.setdefault("example", "")
        validated.append(tip)

    if not validated:
        raise ValueError("No valid tips found in response")

    return validated
