from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, root_validator, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import threading

router = APIRouter()


class AnalyticsAction(str, Enum):
    record = "record"
    query = "query"


class CrossSessionAnalyticsRequest(BaseModel):
    """
    Request model for CrossSessionAnalytics.
    Depending on `action`, different fields are required.
    """
    action: AnalyticsAction = Field(
        ...,
        description="Action to perform: `record` to store a new event, `query` to retrieve analytics.",
    )
    user_id: Optional[str] = Field(
        None, description="Unique identifier of the user."
    )
    session_id: Optional[str] = Field(
        None, description="Unique identifier of the session (required for record)."
    )
    event_name: Optional[str] = Field(
        None, description="Name of the event to record."
    )
    event_properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata for the event."
    )
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Event timestamp. Defaults to now."
    )
    start_time: Optional[datetime] = Field(
        None,
        description="Start of time range for query. If omitted, queries from earliest event.",
    )
    end_time: Optional[datetime] = Field(
        None,
        description="End of time range for query. If omitted, queries up to latest event.",
    )

    @root_validator
    def validate_fields(cls, values):
        action = values.get("action")
        user_id = values.get("user_id")
        if action == AnalyticsAction.record:
            missing = []
            if user_id is None:
                missing.append("user_id")
            if values.get("session_id") is None:
                missing.append("session_id")
            if values.get("event_name") is None:
                missing.append("event_name")
            if missing:
                raise ValueError(f"Missing required fields for record: {', '.join(missing)}")
        elif action == AnalyticsAction.query and user_id is None:
            raise ValueError("`user_id` is required for query action")
        return values


class CrossSessionAnalyticsResponse(BaseModel):
    """Response model for CrossSessionAnalytics."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class _InMemoryAnalyticsStore:
    """
    Thread-safe in-memory analytics store.
    This is a basic implementation for demonstration purposes and
    should be replaced with persistent storage in production.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: Dict[str, List[Dict[str, Any]]] = {}

    def record_event(
        self,
        user_id: str,
        session_id: str,
        event_name: str,
        event_properties: Dict[str, Any],
        timestamp: datetime,
    ) -> None:
        with self._lock:
            self._events.setdefault(user_id, []).append(
                {
                    "session_id": session_id,
                    "event_name": event_name,
                    "event_properties": event_properties,
                    "timestamp": timestamp,
                }
            )

    def query_user_events(
        self,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        with self._lock:
            events = list(self._events.get(user_id, []))  # copy to avoid race conditions

        if start_time or end_time:
            filtered: List[Dict[str, Any]] = []
            for evt in events:
                ts: datetime = evt["timestamp"]
                if start_time and ts < start_time:
                    continue
                if end_time and ts > end_time:
                    continue
                filtered.append(evt)
            return filtered
        return events


# Instantiate a single store for the application lifetime.
_ANLYTICS_STORE = _InMemoryAnalyticsStore()


def get_analytics_store() -> _InMemoryAnalyticsStore:
    """
    Dependency that returns the analytics store instance.
    Replaces with persistent storage implementation when needed.
    """
    return _ANLYTICS_STORE


@router.post("/api/v1/CrossSessionAnalytics", response_model=CrossSessionAnalyticsResponse)
async def crosssessionanalytics_endpoint(
    request: CrossSessionAnalyticsRequest,
    store: _InMemoryAnalyticsStore = Depends(get_analytics_store),
) -> CrossSessionAnalyticsResponse:
    """
    Endpoint to record events across sessions or query analytics results.

    Actions:
    - record: Store a new event for a user/session.
    - query: Retrieve aggregated analytics for a user within an optional time range.
    """
    try:
        if request.action == AnalyticsAction.record:
            store.record_event(
                user_id=request.user_id,
                session_id=request.session_id,
                event_name=request.event_name,
                event_properties=request.event_properties or {},
                timestamp=request.timestamp,
            )
            return CrossSessionAnalyticsResponse(
                success=True,
                message="Event recorded successfully",
                data={
                    "user_id": request.user_id,
                    "session_id": request.session_id,
                    "event_name": request.event_name,
                    "timestamp": request.timestamp,
                },
            )

        # Action == query
        events = store.query_user_events(
            user_id=request.user_id,
            start_time=request.start_time,
            end_time=request.end_time,
        )
        if not events:
            return CrossSessionAnalyticsResponse(
                success=True,
                message="No events found for the specified criteria.",
                data={"events": []},
            )

        # Simple aggregation: count by event_name
        counts: Dict[str, int] = {}
        for evt in events:
            counts[evt["event_name"]] = counts.get(evt["event_name"], 0) + 1

        return CrossSessionAnalyticsResponse(
            success=True,
            message="Analytics query executed successfully",
            data={
                "total_events": len(events),
                "event_counts": counts,
                "events": events,
            },
        )

    except ValueError as ve:
        # Validation errors from our own logic
        raise HTTPException(status_code=422, detail=str(ve)) from ve
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"CrossSessionAnalytics execution failed: {str(e)}",
        ) from e


__all__ = [
    "router",
    "CrossSessionAnalyticsRequest",
    "CrossSessionAnalyticsResponse",
]