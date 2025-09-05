from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import os
import json
import uuid

router = APIRouter()


class AppGenesisAgentRequest(BaseModel):
    """Request model for AppGenesisAgent."""
    project_name: str
    description: Optional[str] = None
    author: Optional[str] = None
    initial_version: str = "0.1.0"
    repository_url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    @validator("project_name")
    def validate_project_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("project_name must be a non-empty string")
        if any(char in v for char in r"\/:*?\"<>|"):
            raise ValueError("project_name contains invalid characters")
        return v.strip()


class AppGenesisAgentResponse(BaseModel):
    """Response model for AppGenesisAgent."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


def _create_project_directory(base_dir: str, project_name: str) -> str:
    """
    Create a project directory under the specified base directory.

    Args:
        base_dir (str): Base directory where projects are stored.
        project_name (str): Name of the project directory to create.

    Returns:
        str: Absolute path to the created project directory.

    Raises:
        FileExistsError: If the directory already exists.
        OSError: If directory creation fails.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    dir_name = f"{project_name}_{timestamp}_{unique_id}"
    project_path = os.path.join(base_dir, dir_name)
    os.makedirs(project_path, exist_ok=False)
    return project_path


def _write_project_files(project_path: str, payload: Dict[str, Any]) -> None:
    """
    Write initial project files such as README.md and metadata.json.

    Args:
        project_path (str): Path to the project directory.
        payload (Dict[str, Any]): Payload data to be stored.

    Raises:
        OSError: If file writing fails.
    """
    readme_content = f"# {payload.get('project_name')}\n\n"
    if payload.get("description"):
        readme_content += f"{payload['description']}\n"
    readme_path = os.path.join(project_path, "README.md")
    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.write(readme_content)

    metadata_path = os.path.join(project_path, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as metadata_file:
        json.dump(payload, metadata_file, indent=4, default=str)


@router.post("/api/v1/AppGenesisAgent", response_model=AppGenesisAgentResponse)
async def appgenesisagent_endpoint(
    request: AppGenesisAgentRequest
) -> AppGenesisAgentResponse:
    """
    Initializes a new project by generating the necessary directory structure
    and metadata files. The project is created under the directory specified
    by the `APP_GENESIS_BASE_DIR` environment variable, or `/tmp/appgenesis`
    if the environment variable is not provided.

    Args:
        request (AppGenesisAgentRequest): Incoming request payload.

    Returns:
        AppGenesisAgentResponse: Standardized response containing result data.

    Raises:
        HTTPException: For validation errors, conflicts, or internal failures.
    """
    try:
        base_dir = os.getenv("APP_GENESIS_BASE_DIR", "/tmp/appgenesis")
        os.makedirs(base_dir, exist_ok=True)
    except OSError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to access or create base directory: {str(e)}",
        )

    try:
        project_path = _create_project_directory(base_dir, request.project_name)
        _write_project_files(project_path, request.dict())
    except FileExistsError:
        raise HTTPException(
            status_code=409,
            detail=f"Project directory already exists for '{request.project_name}'.",
        )
    except (OSError, ValueError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create project: {str(e)}",
        )
    except Exception as e:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during project initialization: {str(e)}",
        )

    result_data = {
        "feature": "AppGenesisAgent",
        "status": "initialized",
        "project_path": project_path,
    }

    return AppGenesisAgentResponse(
        success=True,
        message="Project initialized successfully.",
        data=result_data,
    )


__all__ = ["router", "AppGenesisAgentRequest", "AppGenesisAgentResponse"]