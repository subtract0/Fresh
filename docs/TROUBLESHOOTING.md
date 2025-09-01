# Troubleshooting

## Hangs & Timeouts (ADR-009)
If a command seems stuck or slow:

1) Identify if it’s a long-running mode
- These are intended to run until you stop them:
  - `fresh run --watch`
  - `fresh::monitor::live`
  - `fresh::monitor::web` (uvicorn)
- Exit with Ctrl-C.

2) Try Offline Mode (avoid network)
```bash
export FRESH_OFFLINE=1
# Example bounded run
poetry run python -m ai.cli.fresh run --once  # (future) add --offline too
```
- Network calls (OpenAI, GitHub, remote discovery) are skipped with a clear message.

3) Check connectivity/auth for networked commands
- GitHub PR flows can block on auth or network:
  - Pre-auth: `gh auth status`
  - Verify remote: `git remote -v`
- If still flaky, rerun with Offline Mode and retry later.

4) Timeouts
- External calls should use ~30s default timeouts (HTTP, OpenAI, git/gh subprocess, Firestore where applicable).
- On slow networks, retry rather than waiting indefinitely.

5) Firestore-specific
- If FIREBASE_* variables are set, Firestore backends may be used.
- For dev, prefer local intelligent memory (unset FIREBASE_*). If using Firestore, ensure credentials and connectivity.

6) Collect quick diagnostics
```bash
# Python deps available?
poetry run python -c "import openai,requests; print('ok')"
# gh auth?
gh auth status || true
# Git remotes?
git remote -v || true
```

---

## Common issues

- pytest not found:
  - Run via Poetry: `poetry run pytest -q`

- Firestore errors:
  - Ensure FIREBASE_* env vars are set
  - Verify google-cloud-firestore is installed (Poetry dependency)

- agency_swarm import errors:
  - Ensure Poetry install completed; if not available, tools and agents use graceful fallbacks

- Missing docs links:
  - Run: `python scripts/check_docs_alignment.py --strict`

