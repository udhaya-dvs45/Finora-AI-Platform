import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import os
os.environ.setdefault("USE_TF", "0")          # prevent transformers from loading TensorFlow
os.environ.setdefault("USE_FLAX", "0")        # prevent transformers from loading Flax
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

"""
document_agent.py
-----------------
DocumentAgent for the Multi-Agent Financial Analysis System.

Pipeline:
    PDF
     |  PyMuPDF  -- page-by-page text extraction
     |  JSON     -- structured document saved to processed/json/
     |  Chunking -- fixed-size with overlap, saved to processed/chunks/
     |  Embeddings -- sentence-transformers all-MiniLM-L6-v2
     |  ChromaDB -- persistent vector storage with full metadata

Metadata stored per chunk:
    company, year, doc_name, page_number, chunk_index, chunk_id, total_chunks
"""

import os
import re
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer

# Project-level imports -- resolved relative to the project root added to sys.path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.chroma_manager import ChromaManager
from workspace.session_manager import SessionManager


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # local model, ~80 MB download on first run
CHUNK_SIZE      = 800                   # characters per chunk
CHUNK_OVERLAP   = 150                   # overlap between consecutive chunks
BATCH_SIZE      = 64                    # embedding batch size


# -----------------------------------------------------------------------------
# Filename -> (company, year) parser
# -----------------------------------------------------------------------------

# Standard filename pattern: COMPANY_ANNUAL_YEAR.pdf (case-insensitive)
_FILENAME_RE = re.compile(
    r"^(?P<company>[A-Za-z0-9]+)_ANNUAL_(?P<year>\d{2,4})(?:_.*)?\.pdf$",
    re.IGNORECASE,
)

COMMON_COMPANIES = [
    "AMAZON", "APPLE", "INFOSYS", "MICROSOFT", "REALIANCE", "RELIANCE",
    "TESLA", "META", "ALPHABET", "GOOGLE", "NVIDIA", "NETFLIX", "ADOBE", "INTEL"
]


def _parse_filename(pdf_path: str) -> Tuple[str, str]:
    """
    Extract (company, year) from an annual-report filename or PDF content.

    Supports:
    - COMPANY_ANNUAL_YEAR.pdf  -> ('AMAZON', '2023')
    - COMPANY_YEAR.pdf         -> ('META', '2024')
    - COMPANY-YEAR.pdf         -> ('TESLA', '2023')
    - YEAR_COMPANY.pdf         -> ('INFOSYS', '2023')
    - Free-form with year / company search + first-page text inspection fallback.
    """
    basename = os.path.basename(pdf_path)
    stem = os.path.splitext(basename)[0]

    # Pattern 1: Standard COMPANY_ANNUAL_YEAR.pdf
    m = _FILENAME_RE.match(basename)
    if m:
        comp = m.group("company").upper()
        yr = m.group("year")
        yr = yr if len(yr) == 4 else f"20{yr}"
        return ("REALIANCE" if comp == "RELIANCE" else comp), yr

    # Pattern 2: COMPANY_YEAR or COMPANY-YEAR or COMPANY_ANNUAL_REPORT_YEAR
    m2 = re.match(r"^(?P<company>[A-Za-z0-9]+)[_\-\s]+(?:ANNUAL|REPORT|10K|10-K|FILING|ANNUAL_REPORT)?[_\-\s]*(?P<year>\d{2,4})$", stem, re.IGNORECASE)
    if m2:
        comp = m2.group("company").upper()
        yr = m2.group("year")
        yr = yr if len(yr) == 4 else f"20{yr}"
        return ("REALIANCE" if comp == "RELIANCE" else comp), yr

    # Pattern 3: YEAR_COMPANY
    m3 = re.match(r"^(?P<year>\d{4})[_\-\s]+(?P<company>[A-Za-z0-9]+)$", stem, re.IGNORECASE)
    if m3:
        comp = m3.group("company").upper()
        return ("REALIANCE" if comp == "RELIANCE" else comp), m3.group("year")

    # Pattern 4: Search for year in stem
    y_m = re.search(r"\b(20\d{2}|19\d{2})\b", stem)
    found_year = y_m.group(1) if y_m else None

    # Search for known company in stem
    found_comp = None
    stem_upper = stem.upper()
    for comp in COMMON_COMPANIES:
        if comp in stem_upper:
            found_comp = "REALIANCE" if comp == "RELIANCE" else comp
            break

    # Pattern 5: Inspect first page of PDF if available
    if (not found_comp or not found_year) and os.path.exists(pdf_path):
        try:
            doc = fitz.open(pdf_path)
            if len(doc) > 0:
                first_page = doc[0].get_text("text").upper()
                if not found_comp:
                    for comp in COMMON_COMPANIES:
                        if comp in first_page:
                            found_comp = "REALIANCE" if comp == "RELIANCE" else comp
                            break
                if not found_year:
                    doc_y_m = re.search(r"\b(20\d{2})\b", first_page)
                    if doc_y_m:
                        found_year = doc_y_m.group(1)
            doc.close()
        except Exception:
            pass

    # Fallbacks
    if not found_comp:
        cleaned = re.sub(r"\b(ANNUAL|REPORT|10K|10-K|FILING|FORM|\d{2,4})\b", "", stem, flags=re.IGNORECASE)
        cleaned = re.sub(r"[_\-\s]+", " ", cleaned).strip()
        found_comp = cleaned.split()[0].upper() if cleaned else stem.upper()

    if not found_year:
        found_year = "2024"

    return found_comp, found_year


# Public alias
parse_document_metadata = _parse_filename


# -----------------------------------------------------------------------------
# Text chunking
# -----------------------------------------------------------------------------

def _chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Split `text` into overlapping fixed-size character chunks.

    Parameters
    ----------
    text       : Input string to chunk.
    chunk_size : Maximum characters per chunk.
    overlap    : Characters of overlap between consecutive chunks.

    Returns
    -------
    List of text chunks (non-empty strings only).
    """
    if not text.strip():
        return []

    chunks: List[str] = []
    step = chunk_size - overlap
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start += step

    return chunks


# -----------------------------------------------------------------------------
# DocumentAgent
# -----------------------------------------------------------------------------

class DocumentAgent:
    """
    Responsible for converting annual-report PDFs into searchable ChromaDB entries.

    Usage
    -----
    agent = DocumentAgent(project_root="/path/to/INFOSYS_INTERN")
    agent.process_document("DATA/AMAZON_ANNUAL_2023.pdf", session_id="<uuid>")
    agent.process_all(session_id="<uuid>")
    """

    def __init__(
        self,
        project_root: str,
        session_manager: Optional[SessionManager] = None,
    ):
        """
        Parameters
        ----------
        project_root    : Root directory of the project (contains DATA/, src/, ...).
        session_manager : Optional SessionManager instance for linking documents
                          to research sessions.
        """
        self.project_root    = os.path.abspath(project_root)
        self.data_dir        = os.path.join(self.project_root, "DATA")
        self.json_dir        = os.path.join(self.project_root, "processed", "json")
        self.chunks_dir      = os.path.join(self.project_root, "processed", "chunks")
        self.chroma_db_path  = os.path.join(self.project_root, "chroma_db")
        self.session_manager = session_manager

        # Create output directories
        os.makedirs(self.json_dir,   exist_ok=True)
        os.makedirs(self.chunks_dir, exist_ok=True)

        # Initialise embedding model (downloaded once to ~/.cache/huggingface)
        print(f"[DocumentAgent] Loading embedding model '{EMBEDDING_MODEL}' ...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        print(f"[DocumentAgent] Embedding model ready.")

        # Initialise ChromaDB
        self.chroma = ChromaManager(self.chroma_db_path)

    # -------------------------------------------------------------------------
    # Core pipeline
    # -------------------------------------------------------------------------

    def process_document(
        self,
        pdf_path: str,
        session_id: Optional[str] = None,
        force_reprocess: bool = False,
    ) -> Dict[str, Any]:
        """
        Full pipeline: PDF -> JSON -> Chunks -> Embeddings -> ChromaDB.

        Parameters
        ----------
        pdf_path        : Absolute or project-relative path to the PDF.
        session_id      : If provided, the document is linked to this session.
        force_reprocess : If True, delete existing ChromaDB chunks and reprocess.

        Returns
        -------
        A summary dict with keys: company, year, doc_name, total_pages,
        total_chunks, json_path, chunks_path, status.
        """
        # -- Resolve path ----------------------------------------------------
        if not os.path.isabs(pdf_path):
            pdf_path = os.path.join(self.project_root, pdf_path)

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        filename          = os.path.basename(pdf_path)
        company, year     = _parse_filename(pdf_path)
        doc_id            = f"{company}_{year}"

        print(f"\n[DocumentAgent] -- Processing: {filename} ------------------")
        print(f"[DocumentAgent]   Company: {company}  |  Year: {year}")

        # -- Skip if already processed (unless forced) ------------------------
        json_path   = os.path.join(self.json_dir,   f"{doc_id}.json")
        chunks_path = os.path.join(self.chunks_dir, f"{doc_id}_chunks.json")

        if not force_reprocess:
            existing_stats = self.chroma.get_collection_stats()
            if doc_id in existing_stats["documents"]:
                print(f"[DocumentAgent] '{doc_id}' already in ChromaDB "
                      f"({existing_stats['documents'][doc_id]} chunks). "
                      "Use force_reprocess=True to redo.")
                # Still link to session if requested
                if session_id and self.session_manager:
                    self.session_manager.add_document_to_session(
                        session_id, company, year, filename
                    )
                return {
                    "company": company, "year": year, "doc_name": filename,
                    "status": "already_processed",
                    "total_chunks": existing_stats["documents"][doc_id],
                }

        if force_reprocess:
            self.chroma.delete_document(company, year)

        # -- Step 1: Extract text page by page (PyMuPDF) ---------------------
        print(f"[DocumentAgent] Step 1: Extracting text with PyMuPDF ...")
        pages_data = self._extract_pages(pdf_path, company, year, filename)
        total_pages = len(pages_data)
        print(f"[DocumentAgent]   Extracted {total_pages} pages.")

        # -- Step 2: Save structured JSON ------------------------------------
        print(f"[DocumentAgent] Step 2: Saving structured JSON ...")
        doc_json = {
            "doc_id":       doc_id,
            "company":      company,
            "year":         year,
            "doc_name":     filename,
            "pdf_path":     pdf_path,
            "total_pages":  total_pages,
            "processed_at": datetime.now().isoformat(),
            "pages":        pages_data,
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(doc_json, f, indent=2, ensure_ascii=False)
        print(f"[DocumentAgent]   JSON saved -> {json_path}")

        # -- Step 3: Chunk text -----------------------------------------------
        print(f"[DocumentAgent] Step 3: Chunking text ...")
        all_chunks = self._create_chunks(pages_data, company, year, filename, doc_id)
        total_chunks = len(all_chunks)
        print(f"[DocumentAgent]   Created {total_chunks} chunks.")

        # Save chunks JSON
        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        print(f"[DocumentAgent]   Chunks saved -> {chunks_path}")

        # -- Step 4: Generate embeddings --------------------------------------
        print(f"[DocumentAgent] Step 4: Generating embeddings ...")
        texts = [c["text"] for c in all_chunks]
        embeddings = self._embed_texts(texts)
        print(f"[DocumentAgent]   Embeddings generated for {len(embeddings)} chunks.")

        # -- Step 5: Store in ChromaDB ----------------------------------------
        print(f"[DocumentAgent] Step 5: Storing in ChromaDB ...")
        chunk_ids  = [c["chunk_id"] for c in all_chunks]
        metadatas  = [
            {
                "company":     c["company"],
                "year":        c["year"],
                "doc_name":    c["doc_name"],
                "page_number": c["page_number"],
                "chunk_index": c["chunk_index"],
                "chunk_id":    c["chunk_id"],
                "total_chunks": c["total_chunks"],
            }
            for c in all_chunks
        ]
        self.chroma.add_chunks(chunk_ids, embeddings, texts, metadatas)
        print(f"[DocumentAgent] [OK] Done! Stored {total_chunks} chunks for {doc_id}.")

        # -- Step 6: Link to session ------------------------------------------
        if session_id and self.session_manager:
            self.session_manager.add_document_to_session(
                session_id, company, year, filename
            )

        return {
            "company":      company,
            "year":         year,
            "doc_name":     filename,
            "total_pages":  total_pages,
            "total_chunks": total_chunks,
            "json_path":    json_path,
            "chunks_path":  chunks_path,
            "status":       "processed",
        }

    def process_all(
        self,
        session_id: Optional[str] = None,
        force_reprocess: bool = False,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process every PDF found in the DATA/ directory.

        Parameters
        ----------
        session_id      : Optional session to link all documents to.
        force_reprocess : Reprocess even if already in ChromaDB.
        limit           : Process only the first N documents (useful for testing).

        Returns
        -------
        List of result dicts from process_document().
        """
        pdfs = sorted([
            f for f in os.listdir(self.data_dir)
            if f.lower().endswith(".pdf")
        ])

        if not pdfs:
            print(f"[DocumentAgent] No PDFs found in '{self.data_dir}'.")
            return []

        if limit:
            pdfs = pdfs[:limit]

        print(f"\n[DocumentAgent] Found {len(pdfs)} PDF(s) to process.")
        results = []
        for pdf_name in pdfs:
            pdf_path = os.path.join(self.data_dir, pdf_name)
            try:
                result = self.process_document(
                    pdf_path,
                    session_id=session_id,
                    force_reprocess=force_reprocess,
                )
                results.append(result)
            except Exception as e:
                print(f"[DocumentAgent] ERROR processing '{pdf_name}': {e}")
                results.append({"doc_name": pdf_name, "status": "error", "error": str(e)})

        # Print summary table
        print("\n[DocumentAgent] -- Batch Summary ----------------------------")
        for r in results:
            status = r.get("status", "unknown")
            chunks = r.get("total_chunks", "-")
            name   = r.get("doc_name", r.get("doc_id", "?"))
            print(f"  {name:<35} status={status:<20} chunks={chunks}")
        print("[DocumentAgent] ---------------------------------------------\n")

        return results

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _extract_pages(
        self,
        pdf_path: str,
        company: str,
        year: str,
        filename: str,
    ) -> List[Dict[str, Any]]:
        """
        Open the PDF and extract text page-by-page using PyMuPDF.

        Returns a list of dicts, one per page:
            page_number (1-indexed), text, char_count, company, year, doc_name
        """
        pages_data: List[Dict[str, Any]] = []
        doc = fitz.open(pdf_path)

        try:
            for page_idx in range(len(doc)):
                page   = doc[page_idx]
                text   = page.get_text("text")           # plain text
                text   = text.strip()

                pages_data.append({
                    "page_number": page_idx + 1,           # 1-indexed
                    "text":        text,
                    "char_count":  len(text),
                    "company":     company,
                    "year":        year,
                    "doc_name":    filename,
                })
        finally:
            doc.close()

        return pages_data

    def _create_chunks(
        self,
        pages_data: List[Dict[str, Any]],
        company: str,
        year: str,
        filename: str,
        doc_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Chunk each page's text and return a flat list of chunk records.

        Each chunk record:
            chunk_id, chunk_index, page_number, text, company, year, doc_name,
            doc_id, total_chunks (filled in after all chunks are collected)
        """
        raw_chunks: List[Dict[str, Any]] = []
        chunk_index = 0

        for page in pages_data:
            page_text = page["text"]
            if not page_text.strip():
                continue

            page_chunks = _chunk_text(page_text)

            for chunk_text in page_chunks:
                chunk_id = f"{doc_id}_chunk_{chunk_index:05d}"
                raw_chunks.append({
                    "chunk_id":    chunk_id,
                    "chunk_index": chunk_index,
                    "page_number": page["page_number"],
                    "text":        chunk_text,
                    "company":     company,
                    "year":        year,
                    "doc_name":    filename,
                    "doc_id":      doc_id,
                    "total_chunks": 0,   # placeholder -- filled below
                })
                chunk_index += 1

        # Fill in total_chunks now that we know the total
        total = len(raw_chunks)
        for chunk in raw_chunks:
            chunk["total_chunks"] = total

        return raw_chunks

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using SentenceTransformers.

        Processing is done in batches to keep memory usage reasonable.
        Returns a list of float lists (one per input text).
        """
        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i : i + BATCH_SIZE]
            vecs  = self.embedder.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            all_embeddings.extend(vecs.tolist())
        return all_embeddings

    def list_available_pdfs(self) -> List[str]:
        """Return a sorted list of PDF filenames found in DATA/."""
        return sorted([
            f for f in os.listdir(self.data_dir)
            if f.lower().endswith(".pdf")
        ])
