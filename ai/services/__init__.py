"""
AI Services Package

Provides autonomous services that run continuously to maintain code quality
and implement the self-documenting loop.
"""

from .self_documenting_loop import SelfDocumentingLoopService, get_self_documenting_service

__all__ = [
    'SelfDocumentingLoopService',
    'get_self_documenting_service'
]
