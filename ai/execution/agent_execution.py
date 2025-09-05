from typing import Any

class AgentExecution:
    """AgentExecution class for executing AI tasks."""

    def __init__(self, agent: Any):
        """
        Initialize AgentExecution with an agent.

        :param agent: An instance of an AI agent.
        """
        self.agent = agent

    def execute(self, task: Any) -> Any:
        """
        Execute a task using the agent.

        :param task: The task to be executed.
        :return: The result of the task execution.
        """
        try:
            result = self.agent.perform_task(task)
        except Exception as e:
            # Handle error and return appropriate response
            return {"error": str(e)}
        return result