"""Knowledge base API routes — POST /kb/ingest, GET /kb/status."""

from fastapi import APIRouter, HTTPException

from app.api.schemas import KBIngestResponse
from app.knowledge_base.ingestor import ingest_knowledge_base
from app.knowledge_base.vector_store import get_vector_store
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/ingest", response_model=KBIngestResponse)
async def ingest_kb() -> KBIngestResponse:
    """Ingest all knowledge base Markdown files into ChromaDB.

    Returns:
        KBIngestResponse: Number of chunks ingested and status string.

    Raises:
        HTTPException: 500 on ingest error.
    """
    try:
        chunks = ingest_knowledge_base()
        logger.info("kb_ingest_complete", chunks=chunks)
        return KBIngestResponse(chunks_ingested=chunks, status="ok")
    except Exception as exc:
        logger.error("kb_ingest_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/status")
async def kb_status() -> dict:
    """Return the current status of the ChromaDB knowledge base.

    Returns:
        dict: ``{"status": "ok", "chunks": N}`` or an error status.
    """
    try:
        store = get_vector_store()
        count = store._collection.count()
        return {"status": "ok", "chunks": count}
    except Exception as exc:
        logger.warning("kb_status_error", error=str(exc))
        return {"status": "error", "error": str(exc)}
