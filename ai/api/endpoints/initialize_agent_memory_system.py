from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter()

# In-memory registry to track agent memory initialization status.
# In a real production environment this would be a persistent store (DB / KV / etc.).
_memory_registry: Dict[str, Dict[str, Any]] = {}


class initialize_agent_memory_systemRequest(BaseModel):
    """
    Request model for initialize_agent_memory_system.

    Attributes
    ----------
    agent_id: str
        Unique identifier of the agent whose memory system is being initialized.
    memory_strategy: Optional[str]
        Optional name of the memory strategy/driver to use (e.g., 'redis', 'local', 'vector').
        Defaults to 'default'.
    configuration: Optional[Dict[str, Any]]
        Arbitrary configuration parameters needed by the chosen strategy.
    reset: bool
        When true, any existing memory for the given agent_id will be overwritten.
    """
    agent_id: str
    memory_strategy: Optional[str] = "default"
    configuration: Optional[Dict[str, Any]] = None
    reset: bool = False

    @validator("agent_id")
    def validate_agent_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("agent_id must be a non-empty string")
        return v.strip()


class initialize_agent_memory_systemResponse(BaseModel):
    """
    Response model for initialize_agent_memory_system.

    Attributes
    ----------
    success: bool
        Indicates whether the memory system was successfully initialized.
    message: str
        Human-readable status message.
    data: Optional[Dict[str, Any]]
        Additional data related to the initialization.
    timestamp: datetime
        Server timestamp when the response was generated.
    """
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


def _initialize_memory_for_agent(
    agent_id: str,
    memory_strategy: str,
    configuration: Optional[Dict[str, Any]],
    reset: bool,
) -> Dict[str, Any]:
    """
    Initializes (or resets) the memory system entry for a given agent.

    Parameters
    ----------
    agent_id: str
        Unique identifier for the agent.
    memory_strategy: str
        Selected memory strategy.
    configuration: Optional[Dict[str, Any]]
        Additional configuration data.
    reset: bool
        Whether to overwrite existing memory entry.

    Returns
    -------
    Dict[str, Any]
        Dictionary summarizing the operation performed.
    """
    global _memory_registry

    existing_entry = _memory_registry.get(agent_id)
    if existing_entry and not reset:
        raise HTTPException(
            status_code=409,
            detail=f"Memory system for agent_id '{agent_id}' already exists. "
                   f"Use 'reset=true' to overwrite."
        )

    _memory_registry[agent_id] = {
        "memory_strategy": memory_strategy,
        "configuration": configuration or {},
        "initialized_at": datetime.utcnow().isoformat(),
    }

    return {
        "agent_id": agent_id,
        "memory_strategy": memory_strategy,
        "configuration": configuration or {},
        "status": "initialized" if not existing_entry or reset else "updated",
    }


@router.post(
    "/api/v1/initialize-agent-memory-system",
    response_model=initialize_agent_memory_systemResponse,
    summary="Initialize or reset the memory system for a given agent",
)
async def initialize_agent_memory_system_endpoint(
    request: initialize_agent_memory_systemRequest,
) -> initialize_agent_memory_systemResponse:
    """
    Endpoint to initialize or reset an agent's memory system.

    Raises
    ------
    HTTPException
        409 if the memory system already exists and reset is False.
        500 for any unhandled server error.
    """
    try:
        result_data = _initialize_memory_for_agent(
            agent_id=request.agent_id,
            memory_strategy=request.memory_strategy,
            configuration=request.configuration,
            reset=request.reset,
        )

        return initialize_agent_memory_systemResponse(
            success=True,
            message="Memory system initialized successfully",
            data=result_data,
        )

    except HTTPException:
        # Re-raise FastAPI HTTPException to preserve status codes.
        raise
    except Exception as e:
        # Catch-all for unexpected errors.
        raise HTTPException(
            status_code=500,
            detail=f"initialize_agent_memory_system execution failed: {str(e)}",
        ) from e


__all__ = [
    "router",
    "initialize_agent_memory_systemRequest",
    "initialize_agent_memory_systemResponse",
]