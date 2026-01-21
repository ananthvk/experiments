from openai import OpenAI
from typing import List, Any, Dict, Tuple
from pydantic import BaseModel
from openai.types.responses.tool_param import ParseableToolParam
from openai.types.responses import (
    ParsedResponseFunctionToolCall,
    ResponseInputItemParam,
)
import os

SYSTEM_PROMPT = """
You are an execution function.

Execute exactly one atomic step

Rules:
- Output must match the schema exactly.
- Do not include explanations or reasoning.
- Execute only the given step.
- Do not plan ahead or infer future steps.
- observation must be a short factual description of what was done.
- ExecutionResult contains the final result after a step is executed
"""


class ExecutionResult(BaseModel):
    """
    Results obtained after executing a step. It consists of a result that can be used for future execution, and observation about this execution
    """

    result: str
    observation: str


class ToolCallsRequest(BaseModel):
    """
    Object of this type is returned from execute if the step requires execution of one or more tool calls.
    Once all tool calls are executed, they must be passed back along with the step so that the model can produce
    the final result
    """

    tool_calls: List[ParsedResponseFunctionToolCall]


class Executor:
    """
    Executor executes a step one by one
    """

    def __init__(self, client: OpenAI, model: str = os.environ["MODEL"]) -> None:
        self.client = client
        self.model = model
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0

    def execute(
        self,
        step_context: List[ResponseInputItemParam],
        step: str,
        temperature=0.0,
        max_output_tokens=150,
        tools: list[ParseableToolParam] | None = None,
    ) -> Tuple[ExecutionResult | ToolCallsRequest | None, Any]:
        # Call the api
        if tools is None:
            tools = []
        context: List[ResponseInputItemParam] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Step: {step}"},
        ]
        context += step_context
        response = self.client.responses.parse(
            input=context,
            model=self.model,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            store=False,
            text_format=ExecutionResult,
            tools=tools,
        )
        tool_calls: List[ParsedResponseFunctionToolCall] = []
        for item in response.output:
            if item.type == "function_call":
                tool_calls += [item]
        if response.usage:
            self.input_tokens += response.usage.input_tokens
            self.output_tokens += response.usage.output_tokens
            self.total_tokens += response.usage.total_tokens
        if tool_calls and response.output_parsed is not None:
            raise RuntimeError("Model returned both tool calls and parsed output")
        if tool_calls:
            return (ToolCallsRequest(tool_calls=tool_calls), response.output)
        return (response.output_parsed, response.output)
