"""Core logic: read a workspace file and count exact substring occurrences."""

from pathlib import Path

from contract import CountInput, CountOutput


def count_occurrences(input: CountInput, workspace: Path) -> CountOutput:
    # resolve path inside workspace; raises FileNotFoundError if missing
    path = workspace / input.file_path
    text = path.read_text(encoding="utf-8")
    # str.count is exact, non-overlapping, and deterministic
    return CountOutput(count=text.count(input.target))
