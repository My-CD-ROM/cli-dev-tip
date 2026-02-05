from __future__ import annotations

import json
import urllib.request

from dev_tip.ai.prompt import build_prompt, parse_response
from dev_tip.ai.provider import AIProvider

DEFAULT_MODEL = "google/gemini-2.0-flash-exp:free"
_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterProvider(AIProvider):
    def __init__(self, api_key: str, model: str | None = None) -> None:
        self._api_key = api_key
        self._model = model or DEFAULT_MODEL

    def generate_tips(self, topic: str | None, level: str | None, count: int) -> list[dict]:
        prompt = build_prompt(topic, level, count)
        body = json.dumps({
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()
        req = urllib.request.Request(
            _ENDPOINT,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
                "HTTP-Referer": "https://github.com/dev-tip/cli",
                "X-Title": "dev-tip",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        text = data["choices"][0]["message"]["content"]
        return parse_response(text)
