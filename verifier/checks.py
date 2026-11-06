"""Shared pure helpers used by all verifier modules."""

from pathlib import Path


def result(valid: bool, message: str, *, score: float | None = None, **details) -> dict:
    return {
        "valid": valid,
        "score": float(valid) if score is None else score,
        "message": message,
        "details": details,
    }


def path_problem(file_path: str) -> str | None:
    """return a reason string if file_path is unsafe or empty, else None"""
    p = Path(file_path)
    if p.is_absolute():
        return "file_path must be relative to the workspace, not absolute"
    if ".." in p.parts:
        return "file_path must not escape the workspace with '..'"
    if not p.parts:
        return "file_path must not be empty"
    return None


def expected_count(workspace: Path, file_path: str, target: str) -> int | None:
    """return exact substring count for target in the file, or None if file missing"""
    path = workspace / file_path
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8").count(target)
