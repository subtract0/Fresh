# Troubleshooting

Common issues:

- pytest not found:
  - Run via Poetry: `poetry run pytest -q`

- Firestore errors:
  - Ensure FIREBASE_* env vars are set
  - Verify google-cloud-firestore is installed (Poetry dependency)

- agency_swarm import errors:
  - Ensure Poetry install completed; if not available, tools and agents use graceful fallbacks

- Missing docs links:
  - Run: `python scripts/check_docs_alignment.py --strict`

