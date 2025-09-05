from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter()


class show_integration_examplesRequest(BaseModel):
    """
    Request model for show_integration_examples.

    Attributes
    ----------
    language: Optional[str]
        Specific language example to retrieve. Supported values are
        ``python``, ``curl``, and ``javascript``. If omitted, examples for
        all supported languages are returned.
    """
    language: Optional[str] = None

    # Allowed languages
    _supported_languages = {"python", "curl", "javascript"}

    @validator("language")
    def validate_language(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value.lower() not in cls._supported_languages:
            raise ValueError(
                f"Unsupported language '{value}'. "
                f"Supported languages: {', '.join(sorted(cls._supported_languages))}"
            )
        return value.lower() if value is not None else value


class show_integration_examplesResponse(BaseModel):
    """
    Response model for show_integration_examples.

    Attributes
    ----------
    success: bool
        Indicates whether the request was successfully processed.
    message: str
        Human-readable message describing the result.
    data: Optional[Dict[str, Any]]
        Payload containing integration examples keyed by language.
    timestamp: datetime
        Timestamp at which the response was generated.
    """
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()


def _get_all_examples() -> Dict[str, str]:
    """
    Retrieve integration examples for all supported languages.

    Returns
    -------
    Dict[str, str]
        Mapping of language identifiers to code snippets.
    """
    return {
        "python": (
            "import requests\n\n"
            "url = 'https://api.your-domain.com/api/v1/your-endpoint'\n"
            "payload = {'key': 'value'}\n"
            "headers = {'Authorization': 'Bearer YOUR_API_KEY'}\n"
            "response = requests.post(url, json=payload, headers=headers)\n"
            "print(response.json())"
        ),
        "curl": (
            "curl -X POST \\\n"
            "  https://api.your-domain.com/api/v1/your-endpoint \\\n"
            "  -H 'Authorization: Bearer YOUR_API_KEY' \\\n"
            "  -H 'Content-Type: application/json' \\\n"
            "  -d '{\"key\":\"value\"}'"
        ),
        "javascript": (
            "fetch('https://api.your-domain.com/api/v1/your-endpoint', {\n"
            "  method: 'POST',\n"
            "  headers: {\n"
            "    'Content-Type': 'application/json',\n"
            "    'Authorization': 'Bearer YOUR_API_KEY'\n"
            "  },\n"
            "  body: JSON.stringify({ key: 'value' })\n"
            "})\n"
            "  .then(response => response.json())\n"
            "  .then(data => console.log(data));"
        ),
    }


@router.post("/api/v1/show-integration-examples", response_model=show_integration_examplesResponse)
async def show_integration_examples_endpoint(
    request: show_integration_examplesRequest,
) -> show_integration_examplesResponse:
    """
    Return example code snippets demonstrating how to integrate with the API.

    Parameters
    ----------
    request: show_integration_examplesRequest
        Request payload specifying the language for which to retrieve examples.

    Returns
    -------
    show_integration_examplesResponse
        Response containing the requested integration examples.
    """
    try:
        all_examples = _get_all_examples()

        if request.language:
            # Specific language requested
            language = request.language.lower()
            example = all_examples.get(language)
            if not example:
                # Should never happen due to validation, but safe-guard
                raise HTTPException(
                    status_code=404,
                    detail=f"No integration example found for language '{language}'.",
                )
            data = {language: example}
            message = f"Integration example for '{language}' returned successfully."
        else:
            # Return all examples
            data = all_examples
            message = "Integration examples returned successfully."

        return show_integration_examplesResponse(
            success=True,
            message=message,
            data=data,
            timestamp=datetime.utcnow(),
        )

    except HTTPException:
        # Re-raise HTTPExceptions unmodified so FastAPI can handle status codes
        raise
    except Exception as exc:
        # Catch-all error handling to avoid leaking internal errors
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve integration examples: {str(exc)}",
        ) from exc


__all__ = [
    "router",
    "show_integration_examplesRequest",
    "show_integration_examplesResponse",
]