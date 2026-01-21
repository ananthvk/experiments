from openai import OpenAI
from typing import List, Any, Dict, Tuple
from pydantic import BaseModel
from openai.types.responses.tool_param import ParseableToolParam
from openai.types.responses import (
    ParsedResponseFunctionToolCall,
    ResponseInputItemParam,
)
# what is the sum of product of first 10 natural numbers + the sum of all prime numbers < 100
import os

SYSTEM_PROMPT = """
You are an execution agent.

Your job is to execute exactly **one atomic step** based on the input provided and return a structured result.

**Rules:**
1. **Execute only the given step.** Do not plan ahead or infer future steps. Follow the instructions precisely.
2. Do **not** include any explanations, reasoning, commentary, or extra text outside the schema.
3. The output must **exactly match the schema**.
4. You will receive a **global memory** from previous steps. You should use this memory if it's helpful for executing the current step.
5. After completing the step, return the result, observation, and any **useful memory updates** for future steps.
6. If you use any tool, **do not include tool arguments or reasoning**; just include the observed effect in the observation and the step result in the result.
7. If a tool call produces an output, use **only** the output of the tool as the 'result'.
8. You **may store useful information** from the current step for future steps by returning **key-value pairs** under `"memory_updates"`. 
9. **Memory updates** should be in the form of key-value pairs like `[("key", "value"), ...]`.
10. **Do not modify** or return anything outside of the keys `result`, `observation`, and `memory_updates`.
11. Your **memory updates** must be concise and only contain useful information that could help future steps. Avoid unnecessary details.
12. The execution must remain **focused on the current step**. Any inference of the next step based on the memory should not be included.

**Example Output:**
{
  "result": 42,
  "observation": "Calculated the sum of 20 and 22.",
  "memory_updates": [["sum_20_22", "42"]]
}

Remember, your output must always **exactly match the format**. Only return valid JSON as per the schema.
"""


class ExecutionResult(BaseModel):
    """
    Results obtained after executing a step. It consists of a result that can be used for future execution, and observation about this execution.
    memory_updates is key value pairs that are persisted across steps, use it for storing data that you think might be needed in the future
    """

    result: str
    observation: str
    memory_updates: list[List[str]] = []


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
