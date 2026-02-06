from __future__ import annotations

import os
import random

from dev_tip.ai.cache import load_cache, save_cache
from dev_tip.ai.provider import create_provider
from dev_tip.history import get_unseen

_ENV_KEYS = {
    "gemini": "GEMINI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

BATCH_SIZE = 10


def get_ai_tip(topic: str | None, level: str | None, config: dict) -> dict | None:
    """Return an AI-generated tip, or None on any failure."""
    try:
        provider_name = config.get("ai_provider")
        if not provider_name:
            return None

        api_key = config.get("ai_key")
        if not api_key:
            env_var = _ENV_KEYS.get(provider_name)
            if env_var:
                api_key = os.environ.get(env_var)
        if not api_key:
            return None

        # Try cache first
        tips = load_cache(topic, level)

        if not tips:
            provider = create_provider(
                provider_name, api_key, model=config.get("ai_model")
            )
            tips = provider.generate_tips(topic, level, BATCH_SIZE)
            save_cache(tips, topic, level)

        unseen = get_unseen(tips)
        return random.choice(unseen)

    except Exception:
        return None
