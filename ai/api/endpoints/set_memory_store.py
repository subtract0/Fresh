from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

router = APIRouter()

# In-memory storage for the memory store configuration.
# This would normally live in a persistence layer or shared cache.
_MEMORY_STORE_CONFIG: Dict[str, Any] = {}


class set_memory_storeRequest(BaseModel):
    """
    Request model for set_memory_store.
    Attributes
    ----------
    store_type : str
        The backend type to use for the memory store (e.g., 'redis', 'local', 'inmemory').
    config : Optional[Dict[str, Any]]
        Arbitrary key/value configuration for the backend.
    """

    store_type: str = Field(..., description="Backend type for the memory store.")
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Configuration dictionary for the backend."
    )

    @validator("store_type")
    def validate_store_type(cls, v: str) -> str:
        allowed = {"redis", "local", "inmemory"}
        if v.lower() not in allowed:
            raise ValueError(f"Unsupported store_type '{v}'. Allowed values: {', '.join(allowed)}")
        return v.lower()


class set_memory_storeResponse(BaseModel):
    """
    Response model for set_memory_store.
    """

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


def _apply_memory_store(store_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply the memory store configuration.
    In a real application this would initialise or update the actual backend service.

    Parameters
    ----------
    store_type : str
        The backend type ('redis', 'local', 'inmemory').
    config : Dict[str, Any]
        Configuration for the backend.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the applied configuration.
    """
    # Basic validation per backend, extend as needed.
    if store_type == "redis":
        required_keys = {"host", "port"}
        missing = required_keys - config.keys()
        if missing:
            raise ValueError(f"Missing Redis config keys: {', '.join(missing)}")
    elif store_type == "local":
        required_keys = {"path"}
        missing = required_keys - config.keys()
        if missing:
            raise ValueError(f"Missing Local config keys: {', '.join(missing)}")
    # 'inmemory' requires no additional config.

    # Store the configuration in the in-memory dict.
    _MEMORY_STORE_CONFIG.clear()
    _MEMORY_STORE_CONFIG.update({"store_type": store_type, "config": config, "updated_at": datetime.utcnow()})
    return _MEMORY_STORE_CONFIG.copy()


@router.post("/api/v1/set-memory-store", response_model=set_memory_storeResponse, tags=["Memory Store"])
async def set_memory_store_endpoint(request: set_memory_storeRequest) -> set_memory_storeResponse:
    """
    Configure the memory store backend for the Fresh AI Agent System.

    This endpoint validates the incoming request, applies the configuration,
    and returns a confirmation response.
    """
    try:
        applied_config = _apply_memory_store(request.store_type, request.config or {})

        return set_memory_storeResponse(
            success=True,
            message="Memory store configured successfully.",
            data=applied_config,
        )
    except ValueError as ve:
        # Validation failures raised deliberately inside _apply_memory_store
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as e:
        # Unexpected errors
        raise HTTPException(status_code=500, detail=f"set_memory_store execution failed: {str(e)}") from e


__all__ = ["router", "set_memory_storeRequest", "set_memory_storeResponse"]