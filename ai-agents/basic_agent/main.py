from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
import os
from planner import Planner
from executor import Executor

if os.environ.get("API_BASE") is None:
    raise ValueError("x API_BASE environment variable not set")
if os.environ.get("API_KEY") is None:
    raise ValueError("x API_BASE environment variable not set")
if os.environ.get("MODEL") is None:
    raise ValueError("x MODEL environment variable not set")

api_base = os.environ["API_BASE"]
api_key = os.environ["API_KEY"]
model_name = os.environ["MODEL"]

client = OpenAI(
    base_url=api_base,
    api_key=api_key,
)

planner = Planner(client=client)
executor = Executor(client=client)
current_state = None

print(f"=== Using model {model_name} from {api_base} ===")


task = input("Task > ")
plan = planner.plan(task)

print(f"=== Planning ===")
print()
if plan is None:
    print("Could not generate plan")
    exit(1)
print("steps:")
for i, step in enumerate(plan.steps):
    print(f"{i+1}. {step}")

print(f"=== Executing ===")
for i, step in enumerate(plan.steps):
    result = executor.execute(current_state, step)
    if result is None:
        print("Could not execute step")
        exit(1)
    print(f"=== Step {i + 1} ===")
    print(f"Task: {step} current_state: {current_state}")
    print(f"Result: {result.result}")
    print(f"Observation: {result.observation} current_state: {result.result}")
    print()
    current_state = result.result

print("=== Token usage ===")
print(
    f"planner tokens used: input {planner.input_tokens}, output {planner.output_tokens}, total {planner.total_tokens}"
)
print(
    f"executor tokens used: input {executor.input_tokens}, output {executor.output_tokens}, total {executor.total_tokens}"
)
print(
    f"combined tokens used: input {planner.input_tokens + executor.input_tokens}, output {planner.output_tokens + executor.output_tokens}, total {planner.total_tokens + executor.total_tokens}"
)