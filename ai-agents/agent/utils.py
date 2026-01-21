from planner import Planner, Plan
from executor import Executor


def print_tokens_used(planner: Planner, executor: Executor):
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


def print_plan(plan: Plan):
    print(f"=== Plan ===")
    print()
    for i, step in enumerate(plan.steps):
        print(f"Step {i+1}. {step}")
    print("=" * 20)
