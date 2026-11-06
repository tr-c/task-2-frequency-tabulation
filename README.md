# Frequency Tabulation

A `nanoagent.plugin/v0001` plugin for **Autono-Linguist** (COMP 580).

Given a social media text file and a target syntactic variable (e.g. the
AAVE habitual marker *be*), the agent counts the total number of exact
substring occurrences across the entire file and returns a single integer.
This is Task 2 of five evaluation environments for the Autono-Linguist
Count-Min Sketch agent.

## Tools

| Tool | Does | Code |
|---|---|---|
| `count_occurrences` | Read a workspace file and return the total substring count as an integer | `src/plugin/counter.py` |

## Tasks

| Task | Does | Runner |
|---|---|---|
| `frequency-tabulation` | Count exact occurrences of a target syntactic variable across a corpus | `tool`, with `count_occurrences` |

## Layout

```text
.
├── nanoagent.yaml          # manifest: id, runtime, permissions, tools, tasks
├── contract.py             # typed CountInput / CountOutput; TOOLS and TASKS dicts
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── .env
├── data/
│   └── aave_sample.txt     # bundled 10-line AAVE fixture (9 habitual "be" occurrences)
├── src/plugin/             # MCP server + count_occurrences implementation
├── tests/                  # pytest suite (correct, incorrect, missing, malformed, boundary)
├── test_local.py           # standalone runner; no RUSH Lab needed
├── ui/                     # page renderers
├── product/                # marketplace listing
└── verifier/               # deterministic verifier package
```

## Develop and run

```bash
# install dependencies (generates uv.lock on first run)
uv sync --extra dev

# run the full pytest suite
uv run pytest

# run the standalone local tests without pytest
uv run python test_local.py
```

## Verifier design

The verifier calls Python's `str.count(target)` on the file contents — the
same operation the plugin implementation uses — and compares it against the
agent's reported integer. No LLM is involved. The test suite covers:

| Category | What is tested |
|---|---|
| Correct | Agent returns exactly 9 for `"be"` in the AAVE fixture |
| Incorrect | Agent returns a value that is too high, too low, or off by one |
| Missing | Agent returns 0 when occurrences are present |
| Malformed | Empty target, absolute path, path traversal, empty path, negative count |
| Boundary | Empty file, target absent, missing file, single occurrence, different target |
