# Agency Manifesto

Mission
- To create a persistent-memory and learning mother-agent that spawns agents; she expects arguments: name, instructions, model, output_type.

Guiding Principles
- Outcomes over chatter: minimize back-and-forth; deliver working increments with tests.
- TDD + ADR discipline: start with failing tests; minimal code to green; link ADR-### for behavior/architecture changes.
- No Broken Windows: fix issues before adding features; keep code/tests/docs clean and simple.
- Staging-only data access (ADR-002): never connect to production in dev/test.

Operating Rules (Do/Don’t)
- Do:
  - Read recent memory context first (ReadMemoryContext); write key decisions/outcomes (WriteMemory).
  - Summarize → Plan → Clarify essentials only → Execute → Verify.
  - Keep diffs small and copy-pasteable in docs/PRs.
- Don’t:
  - Waste time exploring unrelated files; follow tests and ADRs.
  - Make irreversible changes without explicit approval.
  - Store secrets in code or logs.

Task Focus Heuristics
- If tests are red: stop feature work; fix tests.
- If source changed without tests: add/modify tests (scripts/check-tests-changed.sh).
- If unsure of intent: ask one crisp question; otherwise proceed with best practice defaults.

Memory Usage
- Always write a short memory after completing a meaningful step: what changed, why, and next step.
- Read top-k memory at the start of a task; prefer tag filters (e.g., feature, bug, adr).

Escalation
- Missing access, ambiguous requirements, or conflicting rules → ask one crisp question.
- External integrations or potentially destructive operations → pause for approval.

