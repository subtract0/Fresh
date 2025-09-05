from typing import Any, Dict

class AgentConfig:
    """Class to handle configuration of AI agents."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize AgentConfig with a configuration.

        :param config: Configuration for the AI agent.
        """
        self.config = config

    def get_config(self, key: str) -> Any:
        """
        Get a value from the agent configuration.

        :param key: Key to get from the agent configuration.
        :return: Value associated with the key.
        :raises KeyError: If the key is not found in the agent configuration.
        """
        try:
            return self.config[key]
        except KeyError as e:
            raise KeyError(f"Key '{key}' not found in agent configuration.") from e

    def set_config(self, key: str, value: Any) -> None:
        """
        Set a value in the agent configuration.

        :param key: Key to set in the agent configuration.
        :param value: Value to set for the key.
        """
        self.config[key] = value