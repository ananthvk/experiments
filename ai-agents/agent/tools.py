from openai.types.responses.tool_param import ParseableToolParam
from typing import Callable, Any, List

tools: List[ParseableToolParam] = [
    {
        "type": "function",
        "name": "calculate",
        "description": "Computes the result of a mathematical expression. The expression will be passed to python eval() function, so make sure that the expression is formatted using python syntax",
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
    }
]


def calculate(obj: dict[str, str]) -> str:
    if obj.get("expression") is None:
        return f"Error: key 'expression' not present in argument"
    # TODO: UNSAFE
    try:
        result = eval(obj["expression"])
        return str(result)
    except Exception as e:
        return f"Error: {e}"


functions_list: dict[str, Callable[..., Any]] = {"calculate": calculate}
