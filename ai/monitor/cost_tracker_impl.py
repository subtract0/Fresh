# ai/monitor/cost_tracker.py

from typing import Any, Dict

class CostTracker:
    """CostTracker class to track the cost of AI operations."""

    def __init__(self):
        """Initialize the CostTracker."""
        self.total_cost = 0.0

    def add_cost(self, cost: float) -> None:
        """
        Add a cost to the total.

        :param cost: The cost to add.
        """
        if not isinstance(cost, float):
            raise ValueError("Cost must be a float.")
        if cost < 0:
            raise ValueError("Cost cannot be negative.")
        self.total_cost += cost

    def get_total_cost(self) -> float:
        """
        Get the total cost tracked so far.

        :return: The total cost.
        """
        return self.total_cost

    def reset(self) -> None:
        """Reset the total cost to zero."""
        self.total_cost = 0.0