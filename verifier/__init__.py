"""The deterministic verifier: routes verify_* calls to the correct module by enum key."""

from contract import Task, Tool

from . import counter as _counter

# map each tool to its verifier module
TOOLS = {Tool.COUNT_OCCURRENCES: _counter}
# map each task to its verify_task function
TASKS = {Task.FREQUENCY_TABULATION: _counter.verify_task}


def verify_input(tool: str, value) -> dict:
    return TOOLS[Tool(tool)].verify_input(value)


def verify_output(tool: str, input_value, output_value, workspace: str) -> dict:
    return TOOLS[Tool(tool)].verify_output(input_value, output_value, workspace)


def verify_task(task: str, arguments, output, reference, workspace: str) -> dict:
    return TASKS[Task(task)](arguments, output, reference, workspace)
