from datetime import datetime
import os
from typing import Optional, Dict, Any, Tuple

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


def _get_system_memory_info() -> Tuple[int, int]:
    """
    Retrieve total and available system memory in bytes.

    Returns
    -------
    Tuple[int, int]
        A tuple in the form (total_bytes, available_bytes).

    Notes
    -----
    Attempts to use `psutil` if installed for accuracy. If not available,
    falls back to `os.sysconf` which may be less precise on some systems.
    """
    try:
        import psutil  # type: ignore
        mem = psutil.virtual_memory()
        return int(mem.total), int(mem.available)
    except Exception:  # pragma: no cover
        # Fallback using os.sysconf
        try:
            page_size = os.sysconf("SC_PAGE_SIZE")  # type: ignore
            phys_pages = os.sysconf("SC_PHYS_PAGES")  # type: ignore
            total = page_size * phys_pages
            # Available memory cannot be accurately determined without psutil,
            # so we approximate by treating 70% of total as "available".
            available = int(total * 0.7)
            return int(total), available
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Unable to determine system memory information"
            ) from exc


class ensure_memory_system_readyRequest(BaseModel):
    """
    Request model for ensuring memory system readiness.

    Attributes
    ----------
    required_memory_mb : Optional[int]
        Minimum amount of free memory (in megabytes) the system must have
        to be considered 'ready'. If omitted, only the `threshold_percent`
        will be evaluated.
    threshold_percent : float
        Maximum allowed percentage of used memory. The system is considered
        'ready' if the current memory utilisation is below this value.
    data : Optional[Dict[str, Any]]
        Arbitrary payload for extensibility.
    """
    required_memory_mb: Optional[int] = Field(
        default=None,
        ge=0,
        description="Required free memory in megabytes."
    )
    threshold_percent: float = Field(
        default=90.0,
        gt=0.0,
        lt=100.0,
        description="Maximum allowed memory utilisation percentage."
    )
    data: Optional[Dict[str, Any]] = None


class ensure_memory_system_readyResponse(BaseModel):
    """
    Response model for ensure_memory_system_ready.
    """
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


@router.post(
    "/api/v1/ensure-memory-system-ready",
    response_model=ensure_memory_system_readyResponse,
    tags=["System Health"],
    summary="Validate system memory readiness"
)
async def ensure_memory_system_ready_endpoint(
    request: ensure_memory_system_readyRequest,
) -> ensure_memory_system_readyResponse:
    """
    Validate that the host machine has sufficient memory available.

    The endpoint checks the current system memory utilisation and ensures it
    meets the criteria defined in the request. If the system fails to satisfy
    the requirements, a 503 Service Unavailable error is raised.

    Parameters
    ----------
    request : ensure_memory_system_readyRequest
        Memory readiness requirements.

    Returns
    -------
    ensure_memory_system_readyResponse
        Structured response indicating readiness status.

    Raises
    ------
    HTTPException
        503 if memory requirements are not met.
        500 for unexpected server errors.
    """
    try:
        total_bytes, available_bytes = _get_system_memory_info()
        total_mb = total_bytes / (1024 * 1024)
        available_mb = available_bytes / (1024 * 1024)
        used_percent = 100.0 - (available_mb / total_mb * 100.0)

        # Evaluate readiness conditions
        required_mb_condition = (
            request.required_memory_mb is None
            or available_mb >= request.required_memory_mb
        )
        threshold_condition = used_percent < request.threshold_percent
        is_ready = required_mb_condition and threshold_condition

        if not is_ready:
            failure_reasons = []
            if not required_mb_condition:
                failure_reasons.append(
                    f"Available memory {available_mb:.2f} MB is below required "
                    f"{request.required_memory_mb} MB."
                )
            if not threshold_condition:
                failure_reasons.append(
                    f"Memory utilisation {used_percent:.2f}% exceeds threshold "
                    f"{request.threshold_percent}%."
                )
            raise HTTPException(
                status_code=503,
                detail="; ".join(failure_reasons),
            )

        result_data = {
            "total_memory_mb": round(total_mb, 2),
            "available_memory_mb": round(available_mb, 2),
            "used_percent": round(used_percent, 2),
            "threshold_percent": request.threshold_percent,
            "required_memory_mb": request.required_memory_mb,
        }

        return ensure_memory_system_readyResponse(
            success=True,
            message="Memory system is ready.",
            data=result_data,
        )

    except HTTPException:
        # Re-raise FastAPI HTTPExceptions untouched
        raise
    except Exception as exc:
        # Log actual exception in real implementation
        raise HTTPException(
            status_code=500,
            detail=f"ensure_memory_system_ready execution failed: {str(exc)}",
        ) from exc


__all__ = [
    "router",
    "ensure_memory_system_readyRequest",
    "ensure_memory_system_readyResponse",
]