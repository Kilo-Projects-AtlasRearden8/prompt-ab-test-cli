from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


class ABClientError(RuntimeError):
    """Raised when the OpenAI-compatible endpoint cannot be used."""


@dataclass
class CompletionResult:
    text: str
    model: str
    endpoint: str
    prompt: str
    raw: dict


class ABClient:
    """Tiny OpenAI-compatible chat client (stdlib only, no API keys required)."""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def chat(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        seed: int | None = None,
    ) -> CompletionResult:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        body: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if seed is not None:
            body["seed"] = seed

        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ABClientError(
                f"HTTP {exc.code} from {self.base_url}: {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise ABClientError(f"Could not reach {self.base_url}: {exc}") from exc

        try:
            text = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ABClientError(
                f"Unexpected response format from {self.base_url}: {payload!r}"
            ) from exc

        return CompletionResult(
            text=text or "",
            model=payload.get("model", self.model),
            endpoint=self.base_url,
            prompt=prompt,
            raw=payload,
        )
