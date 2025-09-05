from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

router = APIRouter()

# Internal in-memory fallback registry for active agents. The structure is:
# {
#     "agent_id": {
#         "id": str,
#         "name": str,
#         "status": str,
#         "last_heartbeat": datetime,
#         "metadata": dict
#     },
#     ...
# }
_active_agents_registry: Dict[str, Dict[str, Any]] = {}


class get_active_agentsRequest(BaseModel):
    """Request model for get_active_agents."""
    agent_id: Optional[str] = Field(
        default=None,
        description="Filter by a specific agent ID and return only that agent if present.",
    )
    include_metadata: bool = Field(
        default=False,
        description="Whether to include additional metadata for each agent.",
    )

    @validator("agent_id")
    def _strip_agent_id(cls, v):  # pragma: no cover
        return v.strip() if v else v


class get_active_agentsResponse(BaseModel):
    """Response model for get_active_agents."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


def _load_active_agents() -> List[Dict[str, Any]]:
    """
    Attempt to retrieve the list of active agents from a shared agent manager.
    Falls back to the local in-memory registry if the manager is unavailable.

    Returns
    -------
    List[Dict[str, Any]]
        A list of active agents represented as dictionaries.
    """
    # Attempt to integrate with a central AgentManager if available
    try:
        from ai.core.agent_manager import AgentManager  # type: ignore
        manager = AgentManager.get_instance()
        agents = manager.list_active_agents()  # Expected to return list[dict]
        return agents if isinstance(agents, list) else []
    except ModuleNotFoundError:
        # Fallback to local registry
        return list(_active_agents_registry.values())
    except Exception:
        # Any unexpected error falls back to local registry as a safe guard
        return list(_active_agents_registry.values())


def _filter_agents(
    agents: List[Dict[str, Any]], agent_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter the list of agents by agent_id if provided.

    Parameters
    ----------
    agents : List[Dict[str, Any]]
        The list of agents to filter.
    agent_id : Optional[str], optional
        The agent ID to filter by, by default None.

    Returns
    -------
    List[Dict[str, Any]]
        Filtered list of agents.
    """
    if agent_id is None:
        return agents
    return [agent for agent in agents if agent.get("id") == agent_id]


def _sanitize_agents(
    agents: List[Dict[str, Any]], include_metadata: bool = False
) -> List[Dict[str, Any]]:
    """
    Remove or include metadata based on the `include_metadata` flag.

    Parameters
    ----------
    agents : List[Dict[str, Any]]
        List of agent dictionaries.
    include_metadata : bool, optional
        Whether to include `metadata` field in each agent dict, by default False.

    Returns
    -------
    List[Dict[str, Any]]
        Sanitized list of agents ready for JSON response.
    """
    sanitized: List[Dict[str, Any]] = []
    for agent in agents:
        copy_agent = {
            "id": agent.get("id"),
            "name": agent.get("name"),
            "status": agent.get("status", "unknown"),
            "last_heartbeat": agent.get("last_heartbeat"),
        }
        if include_metadata:
            copy_agent["metadata"] = agent.get("metadata", {})
        sanitized.append(copy_agent)
    return sanitized


@router.get("/api/v1/active-agents", response_model=get_active_agentsResponse)
async def get_active_agents_endpoint(
    request: get_active_agentsRequest,
) -> get_active_agentsResponse:
    """
    Retrieve a list of currently active agents.

    The endpoint optionally filters by `agent_id` and can include extra metadata
    when `include_metadata` is set to True.

    Parameters
    ----------
    request : get_active_agentsRequest
        The incoming request payload containing optional filters.

    Returns
    -------
    get_active_agentsResponse
        Response object containing agent data or error details.
    """
    try:
        # Step 1. Load agents from source
        agents_raw = _load_active_agents()

        # Step 2. Filter by agent_id if provided
        agents_filtered = _filter_agents(agents_raw, request.agent_id)

        # Step 3. Sanitize output
        agents_response = _sanitize_agents(agents_filtered, request.include_metadata)

        if request.agent_id and not agents_response:
            raise HTTPException(
                status_code=404,
                detail=f"No active agent found with id '{request.agent_id}'",
            )

        # Step 4. Construct successful response
        result_data = {
            "count": len(agents_response),
            "agents": agents_response,
        }

        return get_active_agentsResponse(
            success=True,
            message="Active agents retrieved successfully.",
            data=result_data,
        )

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions untouched
        raise http_exc
    except Exception as exc:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve active agents: {str(exc)}",
        ) from exc


# Export router for main application
__all__ = ["router", "get_active_agentsRequest", "get_active_agentsResponse"]