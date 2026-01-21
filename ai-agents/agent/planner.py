from openai import OpenAI
from typing import List
from pydantic import BaseModel
import os

SYSTEM_PROMPT = """
You are a planning function.

Your task is to convert the given task into a sequence of atomic steps.

- If the task is to solve a mathematical expression, ONLY OUTPUT ONE STEP CONTAINING THE WHOLE EXPRESSSION. DO NOT BREAK IT DOWN. AND ONE MORE STEP CALLED final_step with Print result
- Output must match the schema exactly.
- Do not include explanations, reasoning, or extra text.
- The output will be consumed by another LLM, make it machine friendly
- Each step must be a single executable action.
- Steps must be ordered.
- Number of steps must be <= max_steps.
- Do not solve the task.
- Do not hallucinate
- Steps must not depend on the existence of task to be evaluated, and they must include all information of the task
- Do not use any tools in this step

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
            input=[
                {
                    "role": "system",
                    "content": f"{SYSTEM_PROMPT}\n\nTask:\n{task}\n\nmax_steps:\n{max_steps}",
                }
            ],
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