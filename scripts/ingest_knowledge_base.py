#!/usr/bin/env python3
"""CLI script to ingest knowledge base documents into ChromaDB.

Usage:
    python scripts/ingest_knowledge_base.py
    python scripts/ingest_knowledge_base.py --rebuild
"""

import argparse
import os
import sys

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.knowledge_base.ingestor import ingest_knowledge_base


def main() -> None:
    """Main entry point for the KB ingest script."""
    parser = argparse.ArgumentParser(description="Ingest knowledge base into ChromaDB")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Clear existing ChromaDB collection before ingesting",
    )
    args = parser.parse_args()

    if args.rebuild:
        print("Rebuilding ChromaDB collection...")
        from app.config import settings
        import shutil

        chroma_dir = settings.chroma_persist_dir
        if os.path.exists(chroma_dir):
            shutil.rmtree(chroma_dir)
            print(f"Cleared: {chroma_dir}")

    print("Ingesting knowledge base...")
    chunks = ingest_knowledge_base()
    print(f"Done. Ingested {chunks} chunks into ChromaDB.")


if __name__ == "__main__":
    main()
