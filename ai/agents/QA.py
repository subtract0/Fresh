from agency_swarm import Agent

QA = Agent(
    name="QA",
    description="Expands and hardens tests; focuses on edge cases and regression safety.",
    instructions=(
        "Add tests for edge cases. Verify failure first, then confirm green after fix."
    ),
    temperature=0.2,
)

