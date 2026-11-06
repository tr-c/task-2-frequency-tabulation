"""Deterministic checks for the count_occurrences tool and frequency-tabulation task."""

from pathlib import Path

from .checks import expected_count, path_problem, result


def verify_input(value) -> dict:
    # target must be a non-empty string (empty string matches everywhere, meaningless)
    if not value.target:
        return result(False, "target must be a non-empty string")
    # file_path must stay inside the workspace
    problem = path_problem(value.file_path)
    if problem:
        return result(False, problem)
    return result(True, "input is valid")


def verify_output(input_value, output_value, workspace: str) -> dict:
    expected = expected_count(Path(workspace), input_value.file_path, input_value.target)
    # file must exist before we can grade the count
    if expected is None:
        return result(False, "file not found in workspace")
    # count must be a plain int (bool is a subtype of int; reject it)
    if not isinstance(output_value.count, int) or isinstance(output_value.count, bool):
        return result(False, "count must be an integer", got=repr(output_value.count))
    # count must be non-negative (negative frequency is physically impossible)
    if output_value.count < 0:
        return result(False, "count must be non-negative", got=output_value.count)
    # count must exactly match the ground-truth substring tally
    if output_value.count != expected:
        return result(
            False,
            "count does not match expected",
            expected=expected,
            got=output_value.count,
        )
    return result(True, "count is correct", count=expected)


def verify_task(arguments, output, reference, workspace: str) -> dict:
    # task output shape is identical to tool output; reuse the same check
    return verify_output(arguments, output, workspace)
