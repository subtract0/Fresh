from __future__ import annotations
import os
import time
from pathlib import Path

from ai.monitor.event_bus import PersistentEventBus
from ai.monitor.activity import ActivityDetection, ActivityLevel


def test_bus_append_and_read(tmp_path: Path):
    bus_path = tmp_path / "events.jsonl"
    bus = PersistentEventBus(path=bus_path, max_lines=10)

    # Append a few events
    now = time.time()
    bus.append({"timestamp": now, "event_type": "memory_read", "agent_name": "Test", "details": None})
    bus.append({"timestamp": now + 0.1, "event_type": "memory_write", "agent_name": "Test", "details": None})

    rows = bus.read_recent(limit=5)
    assert len(rows) == 2
    assert rows[-1]["event_type"] == "memory_write"


def test_detector_reads_persisted_events(tmp_path: Path, monkeypatch):
    # Point bus to temp path and enable persisted reads
    bus_path = tmp_path / "events.jsonl"
    monkeypatch.setenv("MONITOR_EVENT_BUS_PATH", str(bus_path))
    monkeypatch.setenv("MONITOR_READ_PERSIST", "1")

    # Write persisted events directly via bus
    bus = PersistentEventBus(path=bus_path)
    now = time.time()
    for i in range(3):
        bus.append({"timestamp": now + i * 0.1, "event_type": "memory_read", "agent_name": "Tester"})

    detector = ActivityDetection(window_seconds=60)
    level = detector.compute_activity_level()

    # With persisted events in the last minute, level should not be IDLE
    assert level in (ActivityLevel.LOW, ActivityLevel.MEDIUM, ActivityLevel.HIGH)
