from agency_swarm import Agent

Developer = Agent(
    name="Developer",
    description="Implements smallest change to make tests green, then refactors.",
    instructions=(
        "Follow RED→GREEN→REFACTOR. Keep diffs small. Prefer clarity over cleverness."
    ),
    temperature=0.2,
)

