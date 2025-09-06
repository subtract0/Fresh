from typing import Any, Dict

class WriteMemory:
    """Class to handle writing data to memory."""

    def __init__(self):
        """Initialize WriteMemory class."""
        self.memory = {}

    def write(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Write a key-value pair to memory.

        Args:
            key (str): The key to write to memory.
            value (Any): The value to write to memory.

        Returns:
            Dict[str, Any]: A dictionary containing the key-value pair that was written to memory.
        """
        try:
            self.memory[key] = value
            return {key: value}
        except Exception as e:
            raise ValueError(f"Failed to write to memory: {e}")

    def read(self, key: str) -> Any:
        """
        Read a value from memory.

        Args:
            key (str): The key to read from memory.

        Returns:
            Any: The value associated with the given key.
        """
        try:
            return self.memory[key]
        except KeyError:
            raise KeyError(f"No value found in memory for key: {key}")