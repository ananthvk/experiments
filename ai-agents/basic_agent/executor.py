from openai import OpenAI
from typing import List, Any
from pydantic import BaseModel
import os

SYSTEM_PROMPT = """
You are an execution function.

Execute exactly one atomic step using the provided current_state.

Rules:
- Output must match the schema exactly.
- Do not include explanations or reasoning.
- Execute only the given step.
- Do not plan ahead or infer future steps.
- Use current_state as the input state.
- observation must be a short factual description of what was done.

Schema:
{
  "result": number | string,
  "observation": "string"
}

"""


class ExecutionResult(BaseModel):
    """
    Results obtained after executing a step. It consists of a result that can be used for future execution, and observation about this execution
    """

    result: int | float | str
    observation: str


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
        self, current_state: Any, step: str, temperature=0.0, max_output_tokens=150
    ) -> ExecutionResult | None:
        # Call the api
        response = self.client.responses.parse(
            input=f"{SYSTEM_PROMPT}\n\ncurrent_state:\n{current_state}\n\nstep:\n{step}",
            model=self.model,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            store=False,
            text_format=ExecutionResult,
        )
        if response.usage:
            self.input_tokens += response.usage.input_tokens
            self.output_tokens += response.usage.output_tokens
            self.total_tokens += response.usage.total_tokens
        return response.output_parsed
