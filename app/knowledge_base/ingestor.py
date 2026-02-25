"""Knowledge base document ingestor.

Loads all Markdown files from the knowledge_base directory, splits them into
overlapping chunks, embeds them with OpenAI, and stores them in ChromaDB.
"""

import os
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma

from app.config import settings
from app.knowledge_base.embeddings import get_embeddings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_KB_DIR = Path(__file__).parent.parent.parent / "knowledge_base"


def ingest_knowledge_base(
    kb_dir: str | None = None,
    persist_dir: str | None = None,
) -> int:
    """Load, chunk, embed, and store all knowledge base documents.

    Args:
        kb_dir: Path to the knowledge_base directory.  Defaults to the
            repo-level ``knowledge_base/`` folder.
        persist_dir: ChromaDB persistence directory.  Defaults to
            ``settings.chroma_persist_dir``.

    Returns:
        int: Total number of chunks ingested.
    """
    kb_path = Path(kb_dir) if kb_dir else _DEFAULT_KB_DIR
    persist_path = persist_dir or settings.chroma_persist_dir

    logger.info("ingest_start", kb_dir=str(kb_path))

    loader = DirectoryLoader(
        str(kb_path),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        recursive=True,
    )
    documents = loader.load()
    logger.info("documents_loaded", count=len(documents))

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    logger.info("chunks_created", count=len(chunks))

    embeddings = get_embeddings()
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=settings.chroma_collection,
        persist_directory=persist_path,
    )

    logger.info("ingest_complete", chunks=len(chunks))
    return len(chunks)
