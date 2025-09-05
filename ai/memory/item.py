# ai/memory/store.py

from typing import Any


class MemoryItem:
    """MemoryItem class for storing data in memory."""

    def __init__(self, key: str, value: Any):
        """
        Initialize a MemoryItem instance.

        :param key: The key for the memory item.
        :param value: The value for the memory item.
        """
        self.key = key
        self.value = value

    def get_key(self) -> str:
        """
        Get the key of the memory item.

        :return: The key of the memory item.
        """
        return self.key

    def get_value(self) -> Any:
        """
        Get the value of the memory item.

        :return: The value of the memory item.
        """
        return self.value

    def set_value(self, value: Any) -> None:
        """
        Set the value of the memory item.

        :param value: The new value for the memory item.
        """
        self.value = value