from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4
import threading
import logging

router = APIRouter()

# Initialize module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Thread-safe in-memory store for tracked query snapshots
_snapshots_lock = threading.Lock()
_snapshots: List[Dict[str, Any]] = []


class TrackedQuerySnapshotRequest(BaseModel):
    """
    Request model for TrackedQuerySnapshot.
    Represents a single query snapshot submitted by a client.
    """
    query: str = Field(..., description="The raw query string to be tracked")
    user_id: Optional[str] = Field(
        None, description="Optional identifier of the user that issued the query"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata accompanying the query"
    )

    @validator("query")
    def query_must_not_be_empty(cls, v: str) -> str:  # noqa: N805
        """Ensure the query string is not empty."""
        if not v.strip():
            raise ValueError("Query string must not be empty.")
        return v


class TrackedQuerySnapshotResponse(BaseModel):
    """
    Response model for TrackedQuerySnapshot.
    Returned to the caller after a snapshot has been processed.
    """
    success: bool = Field(..., description="Indicates whether the operation succeeded")
    message: str = Field(..., description="Human-readable status message")
    data: Optional[Dict[str, Any]] = Field(
        None, description="Payload containing snapshot details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Server-side timestamp when the response was generated",
    )


def _store_snapshot(snapshot: Dict[str, Any]) -> None:
    """
    Thread-safe helper that stores a snapshot in the in-memory list.

    Args:
        snapshot: Dictionary containing snapshot data.

    Raises:
        ValueError: If snapshot is malformed.
    """
    if not isinstance(snapshot, dict):
        raise ValueError("Snapshot must be a dictionary.")

    with _snapshots_lock:
        _snapshots.append(snapshot)
        logger.debug("Snapshot stored. Current count: %d", len(_snapshots))


@router.post(
    "/api/v1/TrackedQuerySnapshot",
    response_model=TrackedQuerySnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
async def trackedquerysnapshot_endpoint(  # noqa: N802
    request: TrackedQuerySnapshotRequest,
) -> TrackedQuerySnapshotResponse:
    """
    Persist a TrackedQuerySnapshot received from a client.

    The endpoint records the snapshot in an in-memory data store which can later
    be queried by analytics components. Every snapshot is assigned a unique
    identifier and stored together with its creation timestamp.

    Args:
        request: `TrackedQuerySnapshotRequest` containing the snapshot data.

    Returns:
        TrackedQuerySnapshotResponse: Confirmation that the snapshot was stored.
    """
    try:
        snapshot_id = str(uuid4())
        created_at = datetime.utcnow()

        snapshot_record = {
            "id": snapshot_id,
            "query": request.query,
            "user_id": request.user_id,
            "metadata": request.metadata or {},
            "created_at": created_at.isoformat(),
        }

        _store_snapshot(snapshot_record)
        logger.info(
            "Stored TrackedQuerySnapshot %s for user %s",
            snapshot_id,
            request.user_id or "anonymous",
        )

        return TrackedQuerySnapshotResponse(
            success=True,
            message="TrackedQuerySnapshot stored successfully.",
            data=snapshot_record,
        )

    except ValueError as ve:
        logger.error("Validation error: %s", ve)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve),
        ) from ve
    except Exception as exc:
        logger.exception("Unhandled error while storing snapshot.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TrackedQuerySnapshot execution failed: {str(exc)}",
        ) from exc


# Export router for main application
__all__ = [
    "router",
    "TrackedQuerySnapshotRequest",
    "TrackedQuerySnapshotResponse",
]