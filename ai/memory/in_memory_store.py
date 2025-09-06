from typing import Any, Dict, Optional

class InMemoryMemoryStore:
    """In-memory store for AI data."""

    def __init__(self):
        """Initialize an empty in-memory store."""
        self._store: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the store.

        Args:
            key: The key to get the value for.

        Returns:
            The value if it exists, None otherwise.
        """
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set a value in the store.

        Args:
            key: The key to set the value for.
            value: The value to set.
        """
        self._store[key] = value

    def delete(self, key: str) -> None:
        """Delete a value from the store.

        Args:
            key: The key to delete the value for.
        """
        if key in self._store:
            del self._store[key]