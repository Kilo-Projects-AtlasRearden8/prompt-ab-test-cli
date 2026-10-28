from __future__ import annotations

import json
from urllib.error import URLError
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_urlopen():
    """Patch urllib.request.urlopen to return canned chat/completions responses."""

    class _Response:
        def __init__(self, payload: dict, status: int = 200):
            self._payload = json.dumps(payload).encode("utf-8")
            self.status = status

        def read(self):
            return self._payload

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    state: dict = {}

    def fake_urlopen(req, timeout=None):
        # Allow tests to inject a connection error
        if state.get("raise") is not None:
            raise state["raise"](state.get("raise_message", "connection failed"))

        body = json.loads(req.data.decode("utf-8")) if req.data else {}
        state["url"] = req.full_url
        state["method"] = req.method
        state["headers"] = dict(req.headers)
        state["body"] = body

        prompt = ""
        for msg in body.get("messages", []):
            if msg.get("role") == "user":
                prompt = msg.get("content", "")

        text = state.get("response_text", f"mock response to: {prompt}")
        status = state.get("status", 200)

        if status >= 400:
            from urllib.error import HTTPError

            raise HTTPError(req.full_url, status, "error", {}, None)

        return _Response(
            {
                "model": body.get("model", "mock-model"),
                "choices": [{"message": {"role": "assistant", "content": text}}],
            },
            status=status,
        )

    with patch("urllib.request.urlopen", side_effect=fake_urlopen) as m:
        yield m, state
