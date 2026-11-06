"""
Standalone local test runner — no RUSH Lab access required.

Mocks agent output directly and runs every verifier branch.
Run from the plugin root:

    uv run python test_local.py

Each test prints PASS or FAIL and exits with code 1 on any failure.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import verifier
from contract import CountInput, CountOutput

# ── fixture data (mirrors data/aave_sample.txt) ──────────────────────────────

SAMPLE_LINES = [
    "she be working late every night",
    "they be saying all kinds of things",
    "he be at the park on weekends",
    "the team be winning when focused",
    "i be thinking about this all the time",
    "she be tired after her shift",
    "they be out here grinding every day",
    "the kids be playing loud after school",
    "he be knowing the answers already",
    "we all doing our part out here",
]
SAMPLE_TEXT = "\n".join(SAMPLE_LINES)

TARGET = "be"
EXPECTED_COUNT = 9   # verified: "be".count in SAMPLE_TEXT == 9
EVERY_COUNT = 2      # "every" appears on lines 1 and 7

FAILURES: list[str] = []


# ── helpers ───────────────────────────────────────────────────────────────────

def make_workspace(text: str | None = None, filename: str = "aave_sample.txt") -> str:
    """write text into a temp dir and return the dir path as str"""
    d = tempfile.mkdtemp()
    content = text if text is not None else SAMPLE_TEXT
    (Path(d) / filename).write_text(content, encoding="utf-8")
    return d


def run(name: str, valid: bool, result: dict) -> None:
    """assert the expected validity and print PASS / FAIL"""
    ok = result["valid"] is valid
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}: {result['message']}")
    if not ok:
        FAILURES.append(name)


def check_task(workspace: str, count: int, target: str = TARGET) -> dict:
    args = CountInput(file_path="aave_sample.txt", target=target)
    out = CountOutput(count=count)
    return verifier.verify_task("frequency-tabulation", args, out, None, workspace)


def check_input(file_path: str = "aave_sample.txt", target: str = TARGET) -> dict:
    return verifier.verify_input("count_occurrences", CountInput(file_path=file_path, target=target))


def check_output(workspace: str, count: int, target: str = TARGET) -> dict:
    args = CountInput(file_path="aave_sample.txt", target=target)
    out = CountOutput(count=count)
    return verifier.verify_output("count_occurrences", args, out, workspace)


# ── correct case ──────────────────────────────────────────────────────────────

def test_correct_count() -> None:
    ws = make_workspace()
    run("correct count (9)", True, check_task(ws, EXPECTED_COUNT))


# ── incorrect cases ───────────────────────────────────────────────────────────

def test_count_too_high() -> None:
    ws = make_workspace()
    run("count too high (12)", False, check_task(ws, 12))


def test_count_too_low() -> None:
    ws = make_workspace()
    run("count too low (5)", False, check_task(ws, 5))


def test_off_by_one() -> None:
    ws = make_workspace()
    # agent counted 8 instead of 9 — still rejected
    run("off by one (8)", False, check_task(ws, EXPECTED_COUNT - 1))


# ── missing case ──────────────────────────────────────────────────────────────

def test_zero_when_matches_exist() -> None:
    ws = make_workspace()
    run("zero returned when count is 9", False, check_task(ws, 0))


# ── malformed input cases ─────────────────────────────────────────────────────

def test_empty_target() -> None:
    run("empty target", False, check_input(target=""))


def test_absolute_path() -> None:
    run("absolute file_path", False, check_input(file_path="/etc/passwd"))


def test_path_traversal() -> None:
    run("path traversal", False, check_input(file_path="../secret.txt"))


def test_empty_file_path() -> None:
    run("empty file_path", False, check_input(file_path=""))


def test_negative_count() -> None:
    ws = make_workspace()
    run("negative count (-1)", False, check_output(ws, -1))


# ── boundary cases ─────────────────────────────────────────────────────────────

def test_empty_file() -> None:
    # empty file → 0 occurrences of anything → correct answer is 0
    ws = make_workspace(text="")
    run("empty file → count 0", True, check_task(ws, 0))


def test_target_absent_in_file() -> None:
    # file has content but the target never appears
    ws = make_workspace(text="totally neutral text\nnothing interesting here")
    run("target absent → count 0", True, check_task(ws, 0))


def test_missing_file_in_workspace() -> None:
    # workspace dir exists but the requested file was never written
    d = tempfile.mkdtemp()
    args = CountInput(file_path="aave_sample.txt", target=TARGET)
    out = CountOutput(count=0)
    r = verifier.verify_task("frequency-tabulation", args, out, None, d)
    run("missing file in workspace", False, r)


def test_single_occurrence() -> None:
    # boundary: exactly one occurrence in the file
    ws = make_workspace(text="she be here")
    run("single occurrence → count 1", True, check_task(ws, 1))


def test_different_target() -> None:
    # verifier is not hardcoded to "be"; must work for any target
    ws = make_workspace()
    run(f'different target "every" → count {EVERY_COUNT}', True, check_task(ws, EVERY_COUNT, target="every"))


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n── Frequency Tabulation — local verifier tests ──\n")

    print("Correct:")
    test_correct_count()

    print("\nIncorrect:")
    test_count_too_high()
    test_count_too_low()
    test_off_by_one()

    print("\nMissing:")
    test_zero_when_matches_exist()

    print("\nMalformed input:")
    test_empty_target()
    test_absolute_path()
    test_path_traversal()
    test_empty_file_path()
    test_negative_count()

    print("\nBoundary:")
    test_empty_file()
    test_target_absent_in_file()
    test_missing_file_in_workspace()
    test_single_occurrence()
    test_different_target()

    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} test(s) — {', '.join(FAILURES)}")
        sys.exit(1)
    else:
        print(f"All 15 tests passed.")
