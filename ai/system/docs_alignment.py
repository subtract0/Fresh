"""
Docs Alignment Service

Runs documentation alignment checks periodically in the background and stores
issues/recoveries into memory. Designed to be managed by the system coordinator.
"""
from __future__ import annotations
import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from ai.tools.docs_tools import DocsAlignmentCheck
    from ai.tools.enhanced_memory_tools import SmartWriteMemory
    _TOOLS_OK = True
except Exception as e:  # pragma: no cover - optional dependency context
    logger.warning(f"Docs alignment tools not available: {e}")
    _TOOLS_OK = False


@dataclass
class DocsAlignmentConfig:
    enabled: bool = True
    interval_sec: int = 600


class DocsAlignmentService:
    """Periodic documentation alignment runner."""
    def __init__(self, config: Optional[DocsAlignmentConfig] = None) -> None:
        self.config = config or DocsAlignmentConfig()
        self._task: Optional[asyncio.Task] = None
        self._stopping = False
        self._last_status: Optional[str] = None

    async def start(self) -> None:
        if not self.config.enabled:
            logger.info("DocsAlignmentService disabled by config")
            return
        if not _TOOLS_OK:
            logger.info("DocsAlignmentService cannot run (tools unavailable)")
            return
        if self._task and not self._task.done():
            return
        logger.info(
            f"Starting DocsAlignmentService (interval={self.config.interval_sec}s)"
        )
        self._stopping = False
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self._stopping = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            finally:
                self._task = None
        logger.info("DocsAlignmentService stopped")

    async def _run_loop(self) -> None:
        while not self._stopping:
            try:
                await self._run_once()
            except Exception as e:  # pragma: no cover - defensive
                logger.error(f"DocsAlignmentService iteration failed: {e}")
            await asyncio.sleep(max(1, int(self.config.interval_sec)))

    async def _run_once(self) -> None:
        # Run checker synchronously (tool is synchronous)
        if not _TOOLS_OK:
            return
        result = DocsAlignmentCheck(strict=False).run()
        status = "FAILED" if "FAILED" in result.upper() else "PASSED"
        if status == "FAILED":
            SmartWriteMemory(
                content=f"Docs Alignment: {status}. Summary: {result[:500]}",
                tags=["documentation", "alignment", "issue"],
            ).run()
        elif self._last_status == "FAILED":
            SmartWriteMemory(
                content="Docs Alignment: PASSED after previous failure.",
                tags=["documentation", "alignment", "recovered"],
            ).run()
        self._last_status = status


_service_singleton: Optional[DocsAlignmentService] = None


def get_docs_alignment_service(config: Optional[DocsAlignmentConfig] = None) -> DocsAlignmentService:
    global _service_singleton
    if _service_singleton is None:
        _service_singleton = DocsAlignmentService(config=config)
    else:
        if config is not None:
            _service_singleton.config = config
    return _service_singleton

