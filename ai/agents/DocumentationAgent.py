"""
DocumentationAgent

Specialized agent responsible for documentation management and alignment.
"""
from __future__ import annotations

try:
    from agency_swarm import Agent
except ImportError:
    class Agent:  # type: ignore
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

from ai.tools.docs_tools import DocsAlignmentCheck
from ai.tools.enhanced_memory_tools import SmartWriteMemory


class DocumentationAgent(Agent):
    """Agent focused on keeping documentation accurate and aligned with code."""
    def __init__(self):
        super().__init__(
            name="Documentation",
            description=(
                "Maintains documentation accuracy, runs alignment checks, and stores findings in memory."
            ),
            instructions=(
                "Run documentation alignment checks regularly. For any issues, store a concise report "
                "with SmartWriteMemory using tags: ['documentation','quality','issue'] and reference the files."
            ),
            tools=[
                DocsAlignmentCheck,
                SmartWriteMemory,
            ],
            temperature=0.1,
        )

