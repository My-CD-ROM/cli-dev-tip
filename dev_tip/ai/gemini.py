from __future__ import annotations

import json
import urllib.request

from dev_tip.ai.prompt import build_prompt, parse_response
from dev_tip.ai.provider import AIProvider

DEFAULT_MODEL = "gemini-2.0-flash"
_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str | None = None) -> None:
        self._api_key = api_key
        self._model = model or DEFAULT_MODEL

    def generate_tips(self, topic: str | None, level: str | None, count: int) -> list[dict]:
        prompt = build_prompt(topic, level, count)
        url = _ENDPOINT.format(model=self._model, api_key=self._api_key)
        body = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
        }).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return parse_response(text)
