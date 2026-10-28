# STATUS

## What was built

`prompt-ab` — a local-first Python CLI for A/B testing two prompt variants
against any OpenAI-compatible endpoint (default Ollama at
`http://localhost:11434/v1`). It:

- Sends both prompts to the configured endpoint/model
- Prints a side-by-side terminal comparison
- Writes a Markdown report with parameters, endpoint, model, a side-by-side
  table, and the full text of each variant
- Requires no API keys and no external Python dependencies (stdlib only)
- Includes a mocked endpoint for tests, so nothing external is needed to verify

Project files:

- `pyproject.toml` — packaging + `prompt-ab` console script entry point
- `src/prompt_ab/__init__.py` — version
- `src/prompt_ab/client.py` — `ABClient` (stdlib `urllib`, OpenAI-compatible
  `/chat/completions`)
- `src/prompt_ab/reporter.py` — side-by-side printing + Markdown rendering
- `src/prompt_ab/cli.py` — argparse CLI, error handling, report writing
- `tests/conftest.py` — `mock_urlopen` fixture (patches `urllib.request.urlopen`)
- `tests/test_client.py` — client, payload forwarding, error handling tests
- `tests/test_cli.py` — CLI report writing, missing prompt, connection error tests
- `tests/test_reporter.py` — Markdown rendering tests
- `LICENSE` — MIT, Copyright (c) 2026 Asdale Dynamics, LLC
- `README.md` — install/usage guide, credits Asdale Dynamics, LLC
- `STATUS.md` — this file

## How to run it

```bash
# Install (no external deps; stdlib only)
pip install -e .

# Run an A/B test (Ollama default endpoint)
prompt-ab \
  --prompt-a "Explain quantum computing in one paragraph." \
  --prompt-b "Explain quantum computing like I'm five." \
  --model llama3 \
  --output comparison.md

# Read prompts from files
prompt-ab --file-a variant_a.txt --file-b variant_b.txt --temperature 0.2

# Use a different OpenAI-compatible endpoint
prompt-ab --endpoint http://localhost:8000/v1 --model my-model

# Options: --endpoint, --model, --api-key, --system, --temperature,
# --max-tokens, --seed, --output (default: prompt_ab_results.md)
```

Exit code is 0 on success, non-zero if the endpoint is unreachable or returns
an error, or if a prompt is missing.

## Verification results

- `pip install -e . --no-build-isolation --no-deps --break-system-packages` — succeeded
- `prompt-ab --help` — works, console script installed at `~/.local/bin/prompt-ab`
- `python3 -m pytest` — **9 passed** (client, CLI, reporter)
- Report rendering verified: header, side-by-side table, variant blocks,
  parameters block, Asdale Dynamics credit all present

## Known gaps

- No real Ollama/LLM endpoint available in this environment, so end-to-end
  testing against a live model was not possible; tests use a mocked endpoint
- No `.github/workflows` files (intentionally omitted per requirements)
- Packaging tested with `--break-system-packages` due to PEP 668 on this
  system; in a virtual environment, plain `pip install -e .` works normally
