import sys
from pathlib import Path

# Ensure project root is importable during tests
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

