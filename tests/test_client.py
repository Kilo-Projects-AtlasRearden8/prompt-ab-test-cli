from __future__ import annotations

from prompt_ab.client import ABClient, ABClientError, CompletionResult
from urllib.error import URLError


def test_chat_returns_content(mock_urlopen):
    _, state = mock_urlopen
    state["response_text"] = "hello from variant A"

    client = ABClient("http://example.com/v1", "test-model")
    result = client.chat("say hello", system="be brief", temperature=0.5)

    assert result.text == "hello from variant A"
    assert result.model == "test-model"
    assert result.prompt == "say hello"
    assert result.endpoint == "http://example.com/v1"
    assert result.raw["choices"][0]["message"]["content"] == "hello from variant A"


def test_chat_forwards_payload(mock_urlopen):
    _, state = mock_urlopen
    state["response_text"] = "ok"

    client = ABClient("http://example.com/v1", "m", api_key="sk-test")
    client.chat("prompt text", system="sys", temperature=0.9, seed=7, max_tokens=10)

    body = state["body"]
    assert state["url"] == "http://example.com/v1/chat/completions"
    assert state["method"] == "POST"
    assert state["headers"]["Authorization"] == "Bearer sk-test"
    assert body["model"] == "m"
    assert body["temperature"] == 0.9
    assert body["seed"] == 7
    assert body["max_tokens"] == 10
    assert body["stream"] is False
    assert body["messages"] == [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "prompt text"},
    ]


def test_chat_http_error_raises(mock_urlopen):
    _, state = mock_urlopen
    state["status"] = 500

    client = ABClient("http://example.com/v1", "m")
    try:
        client.chat("prompt")
        assert False, "expected ABClientError"
    except ABClientError as exc:
        assert "HTTP 500" in str(exc)


def test_connection_refused_raises(mock_urlopen):
    _, state = mock_urlopen
    state["raise"] = URLError
    state["raise_message"] = "connection refused"

    client = ABClient("http://127.0.0.1:9", "model")
    try:
        client.chat("prompt")
        assert False, "expected ABClientError"
    except ABClientError as exc:
        assert "Could not reach" in str(exc)


def test_completion_result_dataclass():
    r = CompletionResult(
        text="hi",
        model="m",
        endpoint="http://x",
        prompt="p",
        raw={"choices": [{"message": {"content": "hi"}}]},
    )
    assert r.text == "hi"
    assert r.model == "m"
    assert r.endpoint == "http://x"
