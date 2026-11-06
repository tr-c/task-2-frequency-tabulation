"""Typed inputs and outputs for every tool and task in this plugin."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    COUNT_OCCURRENCES = "count_occurrences"


class Task(Enum):
    FREQUENCY_TABULATION = "frequency-tabulation"


# input: a workspace-relative file path and the target substring to count
@dataclass
class CountInput(Output):
    file_path: Annotated[str, "Path to the text file to search, relative to the plugin workspace"]
    target: Annotated[str, "Exact substring to count across the entire file contents"]


# output: total number of times target appears as a substring in the file
@dataclass
class CountOutput(Output):
    count: Annotated[int, "Total occurrences of the target substring in the file"]


TOOLS = {Tool.COUNT_OCCURRENCES: (CountInput, CountOutput)}
TASKS = {Task.FREQUENCY_TABULATION: (CountInput, CountOutput)}
