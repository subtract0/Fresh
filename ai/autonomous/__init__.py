"""
Autonomous Loop Package
Provides continuous improvement capabilities for the Fresh AI system.
"""

from .loop import AutonomousLoop, ImprovementOpportunity, CycleResult
from .safety import SafetyController, SafetyCheckpoint, SafetyViolation
from .monitor import CodebaseMonitor, CodeMetrics, IssueReport
from .engine import ImprovementEngine
from .feedback import FeedbackLoop, LearningPattern

__all__ = [
    'AutonomousLoop',
    'ImprovementOpportunity', 
    'CycleResult',
    'SafetyController',
    'SafetyCheckpoint',
    'SafetyViolation',
    'CodebaseMonitor',
    'CodeMetrics',
    'IssueReport',
    'ImprovementEngine',
    'FeedbackLoop',
    'LearningPattern'
]
