from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .client import ABClient, ABClientError
from .reporter import print_side_by_side, render_markdown


def _read_prompt(value: str | None, path: str | None) -> str | None:
    if value is not None:
        return value
    if path is not None:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return fh.read()
        except OSError as exc:
            print(f"error: cannot read file {path}: {exc}", file=sys.stderr)
            return None
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prompt-ab",
        description=(
            "A/B test two prompt variants against an OpenAI-compatible "
            "endpoint (default Ollama at http://localhost:11434/v1), compare "
            "outputs side by side, and save results as Markdown."
        ),
    )
    parser.add_argument("--prompt-a", help="Prompt variant A text")
    parser.add_argument("--prompt-b", help="Prompt variant B text")
    parser.add_argument("--file-a", help="Read prompt variant A from this file")
    parser.add_argument("--file-b", help="Read prompt variant B from this file")
    parser.add_argument(
        "--endpoint",
        default="http://localhost:11434/v1",
        help="OpenAI-compatible base URL (default: http://localhost:11434/v1)",
    )
    parser.add_argument("--model", default="llama3", help="Model name (default: llama3)")
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key only if the endpoint requires one (never stored)",
    )
    parser.add_argument(
        "--system", default=None, help="Optional system message applied to both variants"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (default: 0.7)",
    )
    parser.add_argument(
        "--max-tokens", type=int, default=None, help="Max tokens per completion"
    )
    parser.add_argument("--seed", type=int, default=None, help="Optional sampling seed")
    parser.add_argument(
        "--output",
        default="prompt_ab_results.md",
        help="Markdown report output file (default: prompt_ab_results.md)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    prompt_a = _read_prompt(args.prompt_a, args.file_a)
    if prompt_a is None:
        print("error: a prompt is required (--prompt-a or --file-a)", file=sys.stderr)
        return 1
    prompt_b = _read_prompt(args.prompt_b, args.file_b)
    if prompt_b is None:
        print("error: b prompt is required (--prompt-b or --file-b)", file=sys.stderr)
        return 1

    client = ABClient(args.endpoint, args.model, api_key=args.api_key)
    try:
        result_a = client.chat(
            prompt_a,
            system=args.system,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            seed=args.seed,
        )
        result_b = client.chat(
            prompt_b,
            system=args.system,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            seed=args.seed,
        )
    except ABClientError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print_side_by_side(result_a, result_b)

    report = render_markdown(
        result_a,
        result_b,
        endpoint=args.endpoint,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        system=args.system,
    )
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(report)
    print(f"Report written to {args.output}")
    return 0