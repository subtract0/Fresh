# Agency Manifesto

Mission
- To create a persistent-memory and learning mother-agent that spawns agents; she expects arguments: name, instructions, model, output_type.

Principles
- TDD-first and ADR discipline; every behavior/architecture change references an ADR (ADR-###)
- No Broken Windows: fix issues before adding features; keep code/tests/docs clean and simple
- Staging-only data access (ADR-002); never connect to production in dev/test

Shared Guidance for Agents
- Communicate directionally as wired in the Agency; escalate uncertainties early
- Prefer smallest change to green tests; then refactor for clarity and safety
- Reference ADRs in all significant PRs and design changes

