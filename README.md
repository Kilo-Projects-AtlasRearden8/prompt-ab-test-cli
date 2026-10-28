# prompt-ab

Local-first CLI to A/B test two prompt variants against an OpenAI-compatible
endpoint (default Ollama), compare the outputs side by side, and save the
results as Markdown. No API keys required; everything runs against your own
endpoint.

Built and maintained by **Asdale Dynamics, LLC** — beginner-friendly AI
education, books, and practical tools (Indiana, formed October 2026).

## Install

```bash
pip install -e .
```

This provides the `prompt-ab` command. No external dependencies are required
(the client uses only the Python standard library).

## Usage

```bash
prompt-ab \
  --prompt-a "Explain quantum computing in one paragraph." \
  --prompt-b "Explain quantum computing like I'm five." \
  --model llama3 \
  --output comparison.md
```

Prompts can also be read from files:

```bash
prompt-ab --file-a variant_a.txt --file-b variant_b.txt --temperature 0.2
```

Options:

- `--endpoint` — OpenAI-compatible base URL (default: `http://localhost:11434/v1`, i.e. Ollama)
- `--model` — model name (default: `llama3`)
- `--api-key` — only if your endpoint requires one; never stored or logged
- `--system` — optional system message applied to both variants
- `--temperature`, `--max-tokens`, `--seed` — sampling controls
- `--output` — Markdown report path (default: `prompt_ab_results.md`)

Exit code is 0 on success, non-zero if the endpoint cannot be reached or
returns an error.

## Example report

Running the CLI prints a side-by-side comparison to the terminal and writes a
Markdown report with the generation parameters, endpoint, a side-by-side
table, and the full output of each variant.

## Local-first

No keys, no telemetry, no cloud dependency beyond the endpoint you configure.
Tests run against a bundled mock endpoint, so nothing external is required to
verify the tool.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.
