from openai.types.responses.tool_param import ParseableToolParam
import decimal
import requests
from typing import Callable, Any, List
import math
import numpy as np
import os
import sys
import io

tools: List[ParseableToolParam] = [
    {
        "type": "function",
        "name": "calculate",
        "description": (
            "Computes the result of a mathematical expression. "
            "The expression will be passed to python eval(). "
            "IMPORTANT: The model must return the argument as valid JSON. "
            "Escape quotes and special characters. Do not return raw Python objects."
            "Available modules - math, numpy as np"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "the expression to be evaluated in python syntax",
                }
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "execute_python_script",
        "description": (
            "Executes a complete Python script provided in the 'script' argument. "
            "The 'script' must be a valid Python script in string format. "
            "The generate code must ensure that *print* statements are used. The script output will be fed back into the model"
            "IMPORTANT: The model must return the argument as valid JSON. "
            "Code, state, and variables from one run will not persist to the next one"
            "Escape quotes and special characters. Do not return raw Python objects."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "The full Python script to execute.",
                }
            },
            "required": ["script"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "execute_shell_script",
        "description": (
            "Executes a shell script provided in the 'script' key. "
            "The script will be executed in the shell using subprocess.run(). "
            "The model should return the captured output of the script execution."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "The shell script to be executed",
                }
            },
            "required": ["script"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def calculate(obj: dict[str, str]) -> str:
    if obj.get("expression") is None:
        return f"Error: key 'expression' not present in argument"
    # TODO: UNSAFE
    try:
        result = str(eval(obj["expression"]))
        return result
    except Exception as e:
        return f"Error while invoking tool"


# TODO: NOT SAFE since it allows untrusted execution, run the code on a container / VM
import sys
import io


def execute_python_script(obj: dict[str, str]) -> str:
    """
    Executes a complete Python script provided in the 'script' key of the input dictionary.
    The 'script' should be a valid Python script in string format.
    """

    if "script" not in obj:
        return "Error: script key is missing in input."

    # Capture the original stdout and stderr to avoid printing directly to the console
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Redirect stdout and stderr to capture output and errors
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    try:
        # Execute the full Python script
        exec(obj["script"])

        # Get the captured output and errors
        output = sys.stdout.getvalue()
        error = sys.stderr.getvalue()

        # If there were errors, return them alongside the regular output
        if error:
            return f"Output: {output}\nErrors: {error}"
        return output
    except Exception as e:
        # In case of an error during execution, capture the exception message
        return f"Error: {e}"
    finally:
        # Restore the original stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr


import subprocess
import sys
import io


def execute_shell_script(obj: dict[str, str]) -> str:
    """
    Executes a shell script provided in the 'script' key of the input dictionary.
    The 'script' should be a valid shell script in string format.
    """

    if "script" not in obj:
        return "Error: script key is missing in input."

    # Capture the original stdout and stderr to avoid printing directly to the console
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Redirect stdout and stderr to capture output and errors
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    try:
        # Execute the shell script
        result = subprocess.run(
            obj["script"], shell=True, check=True, text=True, capture_output=True
        )

        # Get the captured output and error
        output = result.stdout
        error = result.stderr

        # If there's an error, return the stderr
        if error:
            output += "\nError: " + error

    except subprocess.CalledProcessError as e:
        # If the shell command fails, capture the error message
        output = f"Error: {e.stderr}"

    finally:
        # Restore the original stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    return output


functions_list: dict[str, Callable[..., Any]] = {
    "calculate": calculate,
    "execute_python_script": execute_python_script,
    "execute_shell_script": execute_shell_script,
}
