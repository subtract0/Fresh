# Testing Guide

- Runner: pytest (configured in pyproject.toml)
- Quick checks:
  - `poetry run pytest -q tests/test_intelligent_memory.py`
  - `poetry run pytest -q tests/test_firestore_memory.py` (requires Firestore env)
- Full suite: `poetry run pytest -q`
- Timeouts: configured via pytest-timeout

Notes:
- Some integration tests are skipped without external credentials
- Use `-k` to filter tests and `-vv` for verbose output

