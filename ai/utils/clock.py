"""
Injectable clock system for deterministic time handling in tests.
Enables fast-forward testing without real time delays.
"""
from __future__ import annotations
import time
from typing import Protocol, Optional


class Clock(Protocol):
    """Clock interface for time operations."""
    
    def now(self) -> float:
        """Get current timestamp."""
        ...
        
    def sleep(self, seconds: float) -> None:
        """Sleep for given seconds."""
        ...


class SystemClock:
    """Production clock using system time."""
    
    def now(self) -> float:
        return time.time()
        
    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


class MockClock:
    """Test clock with controllable time."""
    
    def __init__(self, start_time: float = 0.0):
        self._current_time = start_time
        
    def now(self) -> float:
        return self._current_time
        
    def sleep(self, seconds: float) -> None:
        # In mock mode, sleep just advances the clock
        self._current_time += seconds
        
    def advance(self, seconds: float) -> None:
        """Manually advance clock by seconds."""
        self._current_time += seconds


# Global clock instance - can be swapped in tests
_clock: Clock = SystemClock()


def now() -> float:
    """Get current time from active clock."""
    return _clock.now()


def sleep(seconds: float) -> None:
    """Sleep using active clock."""
    return _clock.sleep(seconds)


def set_clock(clock: Clock) -> None:
    """Set the global clock instance (for tests)."""
    global _clock
    _clock = clock


def get_clock() -> Clock:
    """Get the current clock instance."""
    return _clock


def reset_to_system_clock() -> None:
    """Reset to system clock (cleanup after tests)."""
    global _clock
    _clock = SystemClock()
