from __future__ import annotations
from typing import List, Optional
import os

from ai.memory.store import MemoryStore, MemoryItem
from ai.monitor.firestore_tracker import wrap_firestore_client



class FirestoreMemoryStore(MemoryStore):
    """Firestore-backed memory store (staging-only as per ADR-002/003).

    Requires google-cloud-firestore and FIREBASE_* env vars. If prerequisites are
    not met, raises RuntimeError at init.
    """

    def __init__(self) -> None:
        try:
            from google.cloud import firestore  # type: ignore
        except Exception as e:  # pragma: no cover - only when package missing
            raise RuntimeError("google-cloud-firestore not installed") from e

        project_id = os.getenv("FIREBASE_PROJECT_ID")
        client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
        private_key = os.getenv("FIREBASE_PRIVATE_KEY")

        if not (project_id and client_email and private_key):
            raise RuntimeError("FIREBASE_* env vars are required for FirestoreMemoryStore")

        # Use ADC-compatible init via environment variables
        # Expect caller to export GOOGLE_APPLICATION_CREDENTIALS or set envs via workload identity
        raw_client = firestore.Client(project=project_id)  # type: ignore
        self._db = wrap_firestore_client(raw_client)  # Add cost tracking
        self._col = self._db.collection("agent_memory")  # type: ignore

    def write(self, *, content: str, tags: Optional[List[str]] = None) -> MemoryItem:
        from datetime import datetime, timezone
        doc = {
            "content": content,
            "tags": list(tags or []),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        ref = self._col.document()  # type: ignore
        ref.set(doc)  # type: ignore
        return MemoryItem(id=ref.id, content=content, tags=list(tags or []))

    def query(self, *, limit: int = 5, tags: Optional[List[str]] = None) -> List[MemoryItem]:
        q = self._col.order_by("created_at", direction="DESCENDING").limit(limit)  # type: ignore
        if tags:
            # Simple contains-any via array_contains on first tag; multi-tag OR can be expanded later
            q = q.where("tags", "array_contains", tags[0])  # type: ignore
        docs = list(q.stream())  # type: ignore
        items: List[MemoryItem] = []
        for d in docs:
            data = d.to_dict()
            items.append(MemoryItem(id=d.id, content=data.get("content", ""), tags=list(data.get("tags", []))))
        return items
