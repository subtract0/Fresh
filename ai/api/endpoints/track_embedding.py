from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from collections import defaultdict
import asyncio

router = APIRouter()

# --------------------------------------------------------------------------- #
# In-memory statistics storage (thread/async safe)                            #
# --------------------------------------------------------------------------- #
_usage_stats: Dict[str, Any] = {
    "total_requests": 0,
    "per_model": defaultdict(int),
    "per_user": defaultdict(int),
}
_stats_lock = asyncio.Lock()


class track_embeddingRequest(BaseModel):
    """Request model for track_embedding.

    Attributes
    ----------
    user_id: Optional identifier of the user generating the embedding.
    model: Name or identifier of the embedding model used.
    tokens: Number of tokens processed for the embedding.
    latency_ms: Time taken to compute embedding in milliseconds.
    metadata: Optional arbitrary metadata sent by the caller.
    """
    user_id: Optional[str] = None
    model: str
    tokens: int = Field(..., gt=0, description="Number of tokens must be > 0.")
    latency_ms: Optional[float] = Field(
        None, gt=0, description="Request latency in milliseconds."
    )
    metadata: Optional[Dict[str, Any]] = None

    @validator("model")
    def model_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("model must not be empty.")
        return v


class track_embeddingResponse(BaseModel):
    """Response model for track_embedding."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


async def _update_statistics(req: track_embeddingRequest) -> Dict[str, Any]:
    """
    Update the in-memory statistics safely.

    Parameters
    ----------
    req: track_embeddingRequest
        Incoming validated request data.

    Returns
    -------
    Dict[str, Any]
        Snapshot of updated statistics.
    """
    async with _stats_lock:
        _usage_stats["total_requests"] += 1
        _usage_stats["per_model"][req.model] += 1
        if req.user_id:
            _usage_stats["per_user"][req.user_id] += 1
        # We return a shallow copy to avoid external mutation.
        return {
            "total_requests": _usage_stats["total_requests"],
            "per_model": dict(_usage_stats["per_model"]),
            "per_user": dict(_usage_stats["per_user"]),
        }


@router.post("/api/v1/track-embedding", response_model=track_embeddingResponse)
async def track_embedding_endpoint(
    request: track_embeddingRequest
) -> track_embeddingResponse:
    """
    Track embedding usage and return aggregated statistics.

    The endpoint collects usage information for embeddings and
    maintains aggregated in-memory statistics that can be used
    for monitoring and analytics dashboards.
    """
    try:
        updated_stats = await _update_statistics(request)

        result_data = {
            "feature": "track_embedding",
            "received": request.dict(),
            "stats": updated_stats,
        }

        return track_embeddingResponse(
            success=True,
            message="Embedding usage tracked successfully.",
            data=result_data,
        )

    except HTTPException:
        # Re-raise HTTPExceptions untouched.
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"track_embedding execution failed: {str(e)}",
        ) from e


# Export router for main application
__all__ = ["router", "track_embeddingRequest", "track_embeddingResponse"]