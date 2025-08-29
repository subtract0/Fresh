# Architecture Decision Records (ADR)

**Purpose**: Documents architectural decisions and defines how the agent manages memory, context, and persistent information across sessions.

## Memory & Context Management

1. **Persist stable preferences**: Poetry usage; summarize‑plan‑clarify‑confirm workflow; search‑first behavior.

2. **Do not store secrets** (keys, tokens) in memory.

3. Always include local **rules/docs** in your context when available (e.g., `.windsurf/*`, `.cursorRules`, `rules/*.md`, `docs/specs.md`, `README.md`). Cite filenames/sections when you rely on them.

## Guardrails

- Never make irreversible changes without explicit approval.
- If you're unsure or missing access, stop and ask for exactly what you need.
- When rate limits or external API errors occur, propose a local mock/test plan.
- Never connect agents to production databases. During development and testing, always use a staging database; any production data access requires explicit approval and should be executed through controlled, auditable workflows (prefer read‑only and anonymized data).
- "No Broken Windows" discipline: fix issues immediately before building new features; never ship unfinished code; keep code/tests/docs clean, simple, tidy, and persistently documented for fast onboarding.

## Decision Record Template

When making architectural decisions, document them using this format:

```markdown
# ADR-XXX: [Decision Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[What forces are at play? What constraints exist?]

## Decision
[What is the change that we're making?]

## Consequences
[What becomes easier or more difficult to do because of this change?]
```
