from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, root_validator, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

router = APIRouter()


class SyncOperation(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    UPSERT = "upsert"
    DELETE = "delete"
    GET = "get"


class sync_with_firestoreRequest(BaseModel):
    """Request model for Firestore synchronization."""
    collection: str = Field(..., description="Name of the Firestore collection")
    operation: SyncOperation = Field(..., description="Type of operation to perform")
    data: Optional[Dict[str, Any]] = Field(
        None, description="Document data for create/update/upsert operations"
    )
    doc_id: Optional[str] = Field(
        None,
        description="Document ID for operations that target a specific document",
    )

    @root_validator
    def validate_fields(cls, values):  # noqa: N805
        operation = values.get("operation")
        data = values.get("data")
        doc_id = values.get("doc_id")

        if operation in {SyncOperation.CREATE, SyncOperation.UPDATE, SyncOperation.UPSERT} and data is None:
            raise ValueError(f"Data must be provided for '{operation}' operation.")

        if operation in {SyncOperation.UPDATE, SyncOperation.DELETE, SyncOperation.GET, SyncOperation.UPSERT} and not doc_id:
            raise ValueError(f"doc_id must be provided for '{operation}' operation.")

        return values


class sync_with_firestoreResponse(BaseModel):
    """Response model for Firestore synchronization."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


def _get_firestore_client():
    """
    Lazily import and return a Firestore client.

    Raises:
        HTTPException: If the Firestore client cannot be initialized.
    """
    try:
        from google.cloud import firestore  # pylint: disable=import-error
        return firestore.Client()
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize Firestore client: {exc}",
        ) from exc


def _perform_firestore_operation(
    client, payload: sync_with_firestoreRequest
) -> Dict[str, Any]:
    """
    Execute the requested Firestore operation.

    Args:
        client: Firestore client instance.
        payload: Validated request payload.

    Returns:
        dict: Details about the performed operation.

    Raises:
        HTTPException: For operational errors.
    """
    collection_ref = client.collection(payload.collection)
    operation = payload.operation
    result: Dict[str, Any] = {"operation": operation, "collection": payload.collection}

    try:
        if operation == SyncOperation.CREATE:
            if payload.doc_id:
                doc_ref = collection_ref.document(payload.doc_id)
                doc_ref.create(payload.data)
                result.update({"doc_id": payload.doc_id})
            else:
                doc_ref = collection_ref.document()
                doc_ref.set(payload.data)
                result.update({"doc_id": doc_ref.id})
            result["status"] = "created"

        elif operation == SyncOperation.UPDATE:
            doc_ref = collection_ref.document(payload.doc_id)
            doc_ref.update(payload.data)
            result.update({"doc_id": payload.doc_id, "status": "updated"})

        elif operation == SyncOperation.UPSERT:
            doc_ref = collection_ref.document(payload.doc_id)
            doc_ref.set(payload.data, merge=True)
            result.update({"doc_id": payload.doc_id, "status": "upserted"})

        elif operation == SyncOperation.DELETE:
            doc_ref = collection_ref.document(payload.doc_id)
            doc_ref.delete()
            result.update({"doc_id": payload.doc_id, "status": "deleted"})

        elif operation == SyncOperation.GET:
            doc_ref = collection_ref.document(payload.doc_id)
            snapshot = doc_ref.get()
            if not snapshot.exists:
                raise HTTPException(
                    status_code=404,
                    detail=f"Document {payload.doc_id} not found in {payload.collection}",
                )
            result.update({"doc_id": payload.doc_id, "data": snapshot.to_dict(), "status": "retrieved"})

        else:
            raise HTTPException(status_code=400, detail="Unsupported operation")

    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=500,
            detail=f"Firestore operation failed: {exc}",
        ) from exc

    return result


@router.post(
    "/api/v1/sync-with-firestore",
    response_model=sync_with_firestoreResponse,
    summary="Synchronize data with Firestore",
)
async def sync_with_firestore_endpoint(
    request: sync_with_firestoreRequest,
) -> sync_with_firestoreResponse:
    """
    Endpoint to synchronize data with Google Firestore.

    Workflow:
    1. Validate incoming request.
    2. Initialize Firestore client.
    3. Perform requested operation.
    4. Return a structured response with operation metadata.
    """
    try:
        client = _get_firestore_client()
        result_data = _perform_firestore_operation(client, request)

        return sync_with_firestoreResponse(
            success=True,
            message="Operation completed successfully",
            data=result_data,
        )

    except HTTPException:
        raise  # Re-raise FastAPI HTTPException to preserve status code and message
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {exc}",
        ) from exc


__all__ = ["router", "sync_with_firestoreRequest", "sync_with_firestoreResponse"]