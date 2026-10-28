from __future__ import annotations

from prompt_ab.client import CompletionResult
from prompt_ab.reporter import render_markdown


def test_render_markdown_contains_both_variants():
    a = CompletionResult(text="output A text", model="m", endpoint="http://x", prompt="p a", raw={})
    b = CompletionResult(text="output B text", model="m", endpoint="http://x", prompt="p b", raw={})
    md = render_markdown(a, b, "http://x", "m", 0.7, None, None)

    assert "output A text" in md
    assert "output B text" in md
    assert "| Variant A | Variant B |" in md
    assert "## Variant A" in md
    assert "## Variant B" in md
    assert "Asdale Dynamics, LLC" in md
