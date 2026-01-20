from openai import OpenAI
from typing import List
from pydantic import BaseModel
import os

SYSTEM_PROMPT = """
You are a planning function.

Convert the given task into a sequence of atomic steps.

Rules:
- Output must match the schema exactly.
- Do not include explanations, reasoning, or extra text.
- The output will be consumed by another computer application, make it machine friendly
- Each step must be a single executable action.
- Steps must be ordered.
- Number of steps must be <= max_steps.
- Do not solve the task.
- Do not hallucinate
- Each step must depend only on the result of the immediately previous step.
- Do not reference results of earlier steps other than the most recent one.
- Do not create steps that require combining multiple prior results.

Additional Rule:
- The plan must form a single linear chain where each step takes exactly one input value (the current state) and produces exactly one output value.
- If the task cannot be executed in this form, produce a minimal best-effort linear plan without branching.


Schema:
{
  "steps": ["string"]
}
"""


class Plan(BaseModel):
    """
    Steps required to complete the task
    """

    steps: List[str]


class Planner:
    """
    Planner produces a structured plan for the given task. The plan is a sequence of steps that should be executed in order to arrive at the final result
    """

    def __init__(self, client: OpenAI, model: str = os.environ["MODEL"]) -> None:
        self.client = client
        self.model = model
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0

    def plan(
        self, task: str, max_steps=7, temperature=0.0, max_output_tokens=300
    ) -> Plan | None:
        """
        plan returns a list of actions that should be taken to complete the task

        :return: Plan object, that contains list of steps that should be executed by the model.
                 If the list is empty, it means that step generation failed
                 If the returned object is None, it means that the parsing failed
        :rtype: List[str]
        """
        # Call the api
        response = self.client.responses.parse(
            input=f"{SYSTEM_PROMPT}\n\nTask:\n{task}\n\nmax_steps:\n{max_steps}",
            model=self.model,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            store=False,
            text_format=Plan,
        )
        if response.usage:
            self.input_tokens += response.usage.input_tokens
            self.output_tokens += response.usage.output_tokens
            self.total_tokens += response.usage.total_tokens
        return response.output_parsed