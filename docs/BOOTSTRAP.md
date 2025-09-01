# Bootstrap Guide

1) Install Poetry and Python 3.12
2) `poetry install --no-root`
3) `export PYTHONPATH=$(pwd)`
4) Run demos:
   - `poetry run python scripts/demo-persistent-memory.py`
   - `poetry run python scripts/demo-agent-activity.py`

Optional:
- Configure FIREBASE_* for persistent memory
- Set OPENAI_API_KEY for agency runtimes that require LLMs

