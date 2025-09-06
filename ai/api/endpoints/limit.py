from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio

router = APIRouter()

# In-memory store for rate limits: {user_id: {"used": int, "quota": int, "reset_at": datetime}}
_LIMIT_STORE: Dict[str, Dict[str, Any]] = {}
_LIMIT_LOCK = asyncio.Lock()


class limitRequest(BaseModel):
    """Request model for limit management."""
    user_id: str
    consume: int = 1
    quota: Optional[int] = None  # Optional override of default quota
    interval_seconds: Optional[int] = None  # Optional override of default interval
    check_only: bool = False
    data: Optional[Dict[str, Any]] = None

    @validator("consume")
    def _validate_consume(cls, v: int) -> int:
        if v < 0:
            raise ValueError("consume value must be non-negative")
        return v

    @validator("interval_seconds")
    def _validate_interval(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("interval_seconds must be positive")
        return v


class limitResponse(BaseModel):
    """Response model for limit management."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


DEFAULT_QUOTA = 1000  # Default allowed requests per interval
DEFAULT_INTERVAL_SECONDS = 60 * 60 * 24  # 24 hours


async def _get_usage_record(
    user_id: str, quota: int, interval_seconds: int
) -> Dict[str, Any]:
    """Retrieve or create a usage record for a given user."""
    async with _LIMIT_LOCK:
        record = _LIMIT_STORE.get(user_id)
        now = datetime.utcnow()

        # Create new record or reset if interval has passed
        if record is None or now >= record["reset_at"]:
            record = {
                "used": 0,
                "quota": quota,
                "reset_at": now + timedelta(seconds=interval_seconds),
            }
            _LIMIT_STORE[user_id] = record
        else:
            # Update quota/interval overrides if provided
            if quota != record["quota"]:
                record["quota"] = quota
            if interval_seconds != int((record["reset_at"] - now).total_seconds()):
                record["reset_at"] = now + timedelta(seconds=interval_seconds)

    return record


@router.post("/api/v1/limit", response_model=limitResponse, status_code=200)
async def limit_endpoint(request: limitRequest) -> limitResponse:
    """
    Endpoint to check or consume quota for a user.

    Parameters
    ----------
    request : limitRequest
        The request payload containing user_id and desired operation.

    Returns
    -------
    limitResponse
        JSON response detailing remaining quota or error.
    """
    try:
        quota = request.quota or DEFAULT_QUOTA
        interval_seconds = request.interval_seconds or DEFAULT_INTERVAL_SECONDS

        # Obtain or initialize the user's usage record
        record = await _get_usage_record(request.user_id, quota, interval_seconds)

        async with _LIMIT_LOCK:
            # If only checking, do not mutate usage
            if not request.check_only:
                if record["used"] + request.consume > record["quota"]:
                    remaining = record["quota"] - record["used"]
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "Quota exceeded",
                            "allowed": record["quota"],
                            "used": record["used"],
                            "remaining": max(remaining, 0),
                            "reset_at": record["reset_at"].isoformat(),
                        },
                    )
                # Consume quota
                record["used"] += request.consume

            remaining_after = record["quota"] - record["used"]

        result_data = {
            "user_id": request.user_id,
            "allowed": record["quota"],
            "used": record["used"],
            "remaining": remaining_after,
            "reset_at": record["reset_at"].isoformat(),
            "check_only": request.check_only,
        }

        return limitResponse(
            success=True,
            message="Quota check successful" if request.check_only else "Quota consumed successfully",
            data=result_data,
        )

    except HTTPException as http_exc:
        # Propagate HTTPExceptions as is
        raise http_exc
    except Exception as exc:
        # Generic unhandled errors
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(exc)}") from exc


__all__ = ["router", "limitRequest", "limitResponse"]