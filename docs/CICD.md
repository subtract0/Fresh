# CI/CD Documentation

Current workflows:
- .github/workflows/ci.yml — core CI (tests changed gate + pytest)
- .github/workflows/adr-check.yml — PRs must reference an ADR
- .github/workflows/docs-alignment.yml — documentation alignment checks (new)

Local equivalents:
- scripts/run-tests.sh — run test suite
- scripts/check-tests-changed.sh — ensure tests changed with code

Cross-references:
- Quality Gates: ./QUALITY_GATES.md
- Testing: ./TESTING.md
- ADR Index: ./ADR_INDEX.md

