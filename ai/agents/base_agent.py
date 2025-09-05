from typing import Any, Dict

class Agent:
    """Agent class for the Fresh AI system."""

    def __init__(self, name: str, attributes: Dict[str, Any] = None):
        """
        Initialize an agent with a name and optional attributes.

        :param name: Name of the agent.
        :param attributes: Optional dictionary of attributes.
        """
        self.name = name
        self.attributes = attributes if attributes else {}

    def get_attribute(self, attribute: str) -> Any:
        """
        Get an attribute of the agent.

        :param attribute: Name of the attribute.
        :return: Value of the attribute.
        :raises KeyError: If the attribute does not exist.
        """
        try:
            return self.attributes[attribute]
        except KeyError:
            raise KeyError(f"Attribute '{attribute}' not found in agent '{self.name}'")

    def set_attribute(self, attribute: str, value: Any) -> None:
        """
        Set an attribute of the agent.

        :param attribute: Name of the attribute.
        :param value: Value to set the attribute to.
        """
        self.attributes[attribute] = value