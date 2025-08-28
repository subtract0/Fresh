from agency_swarm import Agent

Reviewer = Agent(
    name="Reviewer",
    description="Reviews diffs for simplicity, security, and ADR linkage.",
    instructions=(
        "Ensure PR links ADR-XXX; check security implications; request tests for any behavior changes."
    ),
    temperature=0.2,
)

