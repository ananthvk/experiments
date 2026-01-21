from openai import OpenAI
from typing import List
from pydantic import BaseModel
import os

SYSTEM_PROMPT = """
You are a planning agent.

Your task is to convert the given task into a **sequence of atomic steps** that can be executed one by one.

Rules:
1. **Do not solve** the task. Only plan the steps.
2. Output must **exactly** match the schema below. Do not include explanations, reasoning, or any extra text.
3. Each step must be **self-contained** and executable with all necessary information from the task.
4. Steps must be ordered logically for execution and may depend on structured memory (key/value pairs).
5. The number of steps must be **<= max_steps**.
6. If the task is a **mathematical expression with standard symbols** (e.g., +, -, *, /), output **only one step** containing the entire expression.
7. Do not make any assumptions about available tools or resources. The planner should only generate **steps** and not perform any tool-specific actions.
8. **Do not hallucinate** or invent extra steps. Only plan based on the task.
9. The output must be **machine-readable** and ready to be consumed by another LLM or agent.
10. You may reference **structured memory** (key-value pairs) available between steps.
11. **Do not reference the state of the task** (e.g., don’t refer to a specific result in an earlier step unless it’s part of the logical sequence).
12. If the task involves sequences or steps (e.g., "Add 5 to 10, then multiply by 3"), break it down correctly into individual steps.
13. Always ensure that each step is fully **executable**.

Schema:
{
  "steps": ["string"]
}

Example valid output:

{
  "steps": [
    "Evaluate the expression 2 * 3 + 5 / 4 * 2"
  ]
}

Always produce output in this **exact JSON format**, without markdown, quotes, or any extra text outside the JSON.
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
    