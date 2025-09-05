from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio

"""
API endpoint for InMemoryMemoryStore
Production-ready implementation
"""

router = APIRouter()

# Global in-memory store and lock for thread safety
_MEMORY_STORE: Dict[str, Any] = {}
_MEMORY_LOCK = asyncio.Lock()


class InMemoryMemoryStoreRequest(BaseModel):
    """
    Request model for InMemoryMemoryStore.

    action:
        set     -> Store a key/value pair  (requires key, value)
        get     -> Retrieve value by key    (requires key)
        delete  -> Remove key/value pair    (requires key)
        clear   -> Clear entire store       (no key/value needed)
    """
    action: str
    key: Optional[str] = None
    value: Optional[Any] = None

    @validator("action")
    def validate_action(cls, v: str) -> str:
        allowed = {"set", "get", "delete", "clear"}
        if v not in allowed:
            raise ValueError(f"action must be one of {allowed}")
        return v

    @validator("key", always=True)
    def validate_key(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        action = values.get("action")
        if action in {"set", "get", "delete"} and not v:
            raise ValueError("key is required for action 'set', 'get', or 'delete'")
        return v

    @validator("value", always=True)
    def validate_value(cls, v: Optional[Any], values: Dict[str, Any]) -> Optional[Any]:
        if values.get("action") == "set" and v is None:
            raise ValueError("value is required for action 'set'")
        return v


class InMemoryMemoryStoreResponse(BaseModel):
    """Response model for InMemoryMemoryStore."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()


@router.post("/api/v1/InMemoryMemoryStore", response_model=InMemoryMemoryStoreResponse)
async def inmemorymemorystore_endpoint(
    request: InMemoryMemoryStoreRequest
) -> InMemoryMemoryStoreResponse:
    """
    Handle in-memory key/value storage operations.

    Supported actions:
    - set:     Store a key/value pair
    - get:     Retrieve a value by key
    - delete:  Delete a key/value pair
    - clear:   Remove all stored data
    """
    try:
        async with _MEMORY_LOCK:
            if request.action == "set":
                _MEMORY_STORE[request.key] = request.value
                result_data = {"key": request.key, "value": request.value}

            elif request.action == "get":
                if request.key not in _MEMORY_STORE:
                    raise HTTPException(status_code=404, detail="Key not found")
                result_data = {"key": request.key, "value": _MEMORY_STORE[request.key]}

            elif request.action == "delete":
                if request.key not in _MEMORY_STORE:
                    raise HTTPException(status_code=404, detail="Key not found")
                deleted_value = _MEMORY_STORE.pop(request.key)
                result_data = {"key": request.key, "deleted_value": deleted_value}

            elif request.action == "clear":
                _MEMORY_STORE.clear()
                result_data = {"cleared": True}

            else:  # This should never occur due to validation
                raise HTTPException(status_code=400, detail="Invalid action")

        return InMemoryMemoryStoreResponse(
            success=True,
            message=f"Action '{request.action}' completed successfully",
            data=result_data,
            timestamp=datetime.now(),
        )

    except HTTPException:
        # Re-raise FastAPI HTTPExceptions without modification
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"InMemoryMemoryStore execution failed: {str(e)}",
        )


__all__ = ["router", "InMemoryMemoryStoreRequest", "InMemoryMemoryStoreResponse"]