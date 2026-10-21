import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
"""
chroma_manager.py
-----------------
ChromaDB abstraction layer for the Multi-Agent Financial Analysis System.

Responsibilities:
- Initialize a persistent ChromaDB client at chroma_db/
- Create / retrieve the 'financial_documents' collection
- Add document chunks with embeddings and metadata
- Query semantically for relevant chunks
- Provide collection statistics
"""

import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
COLLECTION_NAME = "financial_documents"


class ChromaManager:
    """
    Manages the persistent ChromaDB vector database for financial document chunks.

    The database is stored at <project_root>/chroma_db/ and survives between runs.
    """

    def __init__(self, db_path: str):
        """
        Parameters
        ----------
        db_path : str
            Absolute or relative path to the ChromaDB persistence directory.
        """
        os.makedirs(db_path, exist_ok=True)

        self.client = chromadb.PersistentClient(path=db_path)

        # Get or create the single collection for all financial document chunks
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},   # cosine similarity for sentence-transformers
        )

        print(f"[ChromaManager] Connected to ChromaDB at '{db_path}'")
        print(f"[ChromaManager] Collection '{COLLECTION_NAME}' has "
              f"{self.collection.count()} chunks loaded.")

    # -------------------------------------------------------------------------
    # Write operations
    # -------------------------------------------------------------------------

    def add_chunks(
        self,
        chunk_ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """
        Upsert a batch of chunks with their embeddings and metadata.

        Parameters
        ----------
        chunk_ids  : Unique string IDs for each chunk.
        embeddings : Corresponding embedding vectors (list of floats).
        documents  : Raw text content of each chunk.
        metadatas  : Metadata dicts -- must include company, year, doc_name,
                     page_number, chunk_index.
        """
        if not chunk_ids:
            return

        self.collection.upsert(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        print(f"[ChromaManager] Upserted {len(chunk_ids)} chunks into '{COLLECTION_NAME}'.")

    # -------------------------------------------------------------------------
    # Read / Query operations
    # -------------------------------------------------------------------------

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Semantic similarity search.

        Parameters
        ----------
        query_embeddings : One or more query embedding vectors.
        n_results        : Number of results to return per query.
        where            : Optional ChromaDB metadata filter dict.
                           E.g. {"company": "AMAZON", "year": "2023"}

        Returns
        -------
        Raw ChromaDB query result dict with keys: ids, documents, metadatas, distances.
        """
        kwargs: Dict[str, Any] = {
            "query_embeddings": query_embeddings,
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        return self.collection.query(**kwargs)

    def get_by_document(self, company: str, year: str) -> Dict[str, Any]:
        """
        Retrieve all chunks belonging to a specific company-year document.

        Parameters
        ----------
        company : Company name string (e.g. 'AMAZON').
        year    : Year string (e.g. '2023').

        Returns
        -------
        ChromaDB get() result dict.
        """
        return self.collection.get(
            where={"$and": [{"company": company}, {"year": year}]},
            include=["documents", "metadatas"],
        )

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Return a summary of what is stored in the collection.

        Returns
        -------
        Dict with total chunk count and a per-document breakdown.
        """
        total = self.collection.count()
        all_meta = self.collection.get(include=["metadatas"])["metadatas"]

        # Build document -> chunk count mapping
        doc_counts: Dict[str, int] = {}
        for meta in all_meta:
            key = f"{meta.get('company', '?')}_{meta.get('year', '?')}"
            doc_counts[key] = doc_counts.get(key, 0) + 1

        return {
            "total_chunks": total,
            "documents": doc_counts,
        }

    def delete_document(self, company: str, year: str) -> None:
        """
        Delete all chunks for a company-year document (useful for reprocessing).
        """
        result = self.collection.get(
            where={"$and": [{"company": company}, {"year": year}]},
        )
        ids_to_delete = result.get("ids", [])
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            print(f"[ChromaManager] Deleted {len(ids_to_delete)} chunks for "
                  f"{company} {year}.")
        else:
            print(f"[ChromaManager] No chunks found for {company} {year}.")
