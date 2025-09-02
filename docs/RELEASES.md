# Releases

## v0.1.0

Date: 2025-09-02

Highlights:
- Assist planning workflow: tests for plan-pr, docs-only enforcement, CLI helpers exported
- Scaffold command: directory placeholder rendering and tests
- Integration readiness: basic MCP defaults, Telegram dev dependency, .env loaded for tests
- CI: default unit suite remains clean; manual integration workflow added
- Docs: ASSIST.md, SCAFFOLD.md, README CLI quickstart

# Releases

## v0 (baseline)
- Tag: v0
- Commit: 638624ab541d
- Date: 2025-09-02
- Purpose: Establish a clean, stable baseline for three supported modes of operation:
  - Build on itself (extend Fresh incrementally)
  - Scaffold new applications (outside this repo)
  - Assist other repositories (operate as an agent tool against a target repo)
- Notes:
  - Keep changes small, shippable, and verifiable (v0.1, v0.2, …)
  - Avoid broad, multi-feature edits; prefer focused MVPs with tests and docs

