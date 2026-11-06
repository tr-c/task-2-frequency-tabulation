"""Pytest tests covering correct, incorrect, missing, malformed, and boundary verifier cases."""

from __future__ import annotations

from pathlib import Path

import verifier
from contract import CountInput, CountOutput

# fixture text — mirrors data/aave_sample.txt exactly
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

# ground-truth counts verified offline with str.count()
TARGET = "be"
EXPECTED_COUNT = 9   # "be" appears 9 times in SAMPLE_TEXT
EVERY_COUNT = 2      # "every" appears on lines 1 and 7
THE_COUNT = 7        # "the" appears 7 times (incl. inside "they" x2)


def _make_workspace(tmp_path: Path, text: str | None = None, filename: str = "aave_sample.txt") -> Path:
    """write text into tmp_path/<filename> and return the workspace path"""
    (tmp_path / filename).write_text(text if text is not None else SAMPLE_TEXT, encoding="utf-8")
    return tmp_path


def _args(file_path: str = "aave_sample.txt", target: str = TARGET) -> CountInput:
    return CountInput(file_path=file_path, target=target)


def _out(count: int) -> CountOutput:
    return CountOutput(count=count)


# ── correct case ──────────────────────────────────────────────────────────────

def test_approves_exact_count(tmp_path: Path) -> None:
    ws = _make_workspace(tmp_path)
    r = verifier.verify_task("frequency-tabulation", _args(), _out(EXPECTED_COUNT), None, str(ws))
    assert r["valid"] is True
    assert r["score"] == 1.0
    assert "correct" in r["message"]
    assert r["details"]["count"] == EXPECTED_COUNT


# ── incorrect cases ───────────────────────────────────────────────────────────

def test_refuses_count_too_high(tmp_path: Path) -> None:
    ws = _make_workspace(tmp_path)
    r = verifier.verify_task("frequency-tabulation", _args(), _out(EXPECTED_COUNT + 3), None, str(ws))
    assert r["valid"] is False
    assert r["details"]["expected"] == EXPECTED_COUNT
    assert r["details"]["got"] == EXPECTED_COUNT + 3


def test_refuses_count_too_low(tmp_path: Path) -> None:
    ws = _make_workspace(tmp_path)
    r = verifier.verify_task("frequency-tabulation", _args(), _out(EXPECTED_COUNT - 4), None, str(ws))
    assert r["valid"] is False
    assert r["details"]["expected"] == EXPECTED_COUNT


def test_refuses_off_by_one(tmp_path: Path) -> None:
    # agent is one short — still wrong
    ws = _make_workspace(tmp_path)
    r = verifier.verify_task("frequency-tabulation", _args(), _out(EXPECTED_COUNT - 1), None, str(ws))
    assert r["valid"] is False
    assert r["details"]["got"] == EXPECTED_COUNT - 1


# ── missing case ──────────────────────────────────────────────────────────────

def test_refuses_zero_when_matches_exist(tmp_path: Path) -> None:
    # agent returned 0 even though "be" appears 9 times
    ws = _make_workspace(tmp_path)
    r = verifier.verify_task("frequency-tabulation", _args(), _out(0), None, str(ws))
    assert r["valid"] is False
    assert r["details"]["expected"] == EXPECTED_COUNT
    assert r["details"]["got"] == 0


# ── malformed input cases ─────────────────────────────────────────────────────

def test_refuses_empty_target() -> None:
    # empty target would match everywhere; must be rejected before workspace access
    r = verifier.verify_input("count_occurrences", _args(target=""))
    assert r["valid"] is False
    assert "non-empty" in r["message"]


def test_refuses_absolute_file_path() -> None:
    r = verifier.verify_input("count_occurrences", _args(file_path="/etc/passwd"))
    assert r["valid"] is False
    assert "absolute" in r["message"]


def test_refuses_path_traversal() -> None:
    r = verifier.verify_input("count_occurrences", _args(file_path="../secret.txt"))
    assert r["valid"] is False
    assert ".." in r["message"]


def test_refuses_empty_file_path() -> None:
    r = verifier.verify_input("count_occurrences", _args(file_path=""))
    assert r["valid"] is False


def test_refuses_negative_count(tmp_path: Path) -> None:
    # negative frequency is physically impossible
    ws = _make_workspace(tmp_path)
    r = verifier.verify_output("count_occurrences", _args(), _out(-1), str(ws))
    assert r["valid"] is False
    assert "non-negative" in r["message"]


# ── boundary cases ─────────────────────────────────────────────────────────────

def test_approves_zero_for_empty_file(tmp_path: Path) -> None:
    # empty file → 0 occurrences of anything → correct answer is 0
    _make_workspace(tmp_path, text="")
    r = verifier.verify_task("frequency-tabulation", _args(), _out(0), None, str(tmp_path))
    assert r["valid"] is True
    assert r["details"]["count"] == 0


def test_approves_zero_when_target_absent(tmp_path: Path) -> None:
    # file has content but the target never appears
    _make_workspace(tmp_path, text="totally neutral text\nnothing interesting here")
    r = verifier.verify_task("frequency-tabulation", _args(), _out(0), None, str(tmp_path))
    assert r["valid"] is True
    assert r["details"]["count"] == 0


def test_refuses_when_file_missing_from_workspace(tmp_path: Path) -> None:
    # workspace dir exists but the requested file was never written
    r = verifier.verify_task("frequency-tabulation", _args(), _out(0), None, str(tmp_path))
    assert r["valid"] is False
    assert "not found" in r["message"]


def test_approves_single_occurrence(tmp_path: Path) -> None:
    # boundary: exactly one occurrence
    _make_workspace(tmp_path, text="she be here")
    r = verifier.verify_task("frequency-tabulation", _args(), _out(1), None, str(tmp_path))
    assert r["valid"] is True
    assert r["details"]["count"] == 1


def test_approves_different_target(tmp_path: Path) -> None:
    # verifier is not hardcoded to "be"; works for any target
    ws = _make_workspace(tmp_path)
    r = verifier.verify_task("frequency-tabulation", _args(target="every"), _out(EVERY_COUNT), None, str(ws))
    assert r["valid"] is True
    assert r["details"]["count"] == EVERY_COUNT
