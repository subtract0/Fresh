from typing import Any, Dict

class ReadMemoryContext:
    """Class to handle reading from memory context."""

    def __init__(self, memory: Dict[str, Any]):
        """
        Initialize ReadMemoryContext with a memory context.

        :param memory: Memory context to read from.
        """
        self.memory = memory

    def read(self, key: str) -> Any:
        """
        Read a value from the memory context.

        :param key: Key to read from the memory context.
        :return: Value associated with the key.
        :raises KeyError: If the key is not found in the memory context.
        """
        try:
            return self.memory[key]
        except KeyError as e:
            raise KeyError(f"Key '{key}' not found in memory context.") from e