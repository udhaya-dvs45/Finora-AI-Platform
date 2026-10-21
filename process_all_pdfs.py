"""
process_all_pdfs.py
-------------------
Batch-process ALL 17 PDFs → ChromaDB → Extract financial metrics.
Skips documents already indexed.

Run from the project root:
    python process_all_pdfs.py
"""

import sys
import os
import re

# Fix encoding for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_FLAX", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR  = os.path.join(ROOT_DIR, "src")
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from agents.document_agent   import DocumentAgent
from agents.extraction_agent import ExtractionAgent

# ─────────────────────────────────────────────
DATA_DIR      = os.path.join(ROOT_DIR, "DATA")
PROCESSED_DIR = os.path.join(ROOT_DIR, "processed", "json")

def separator(char="─", width=60):
    print(char * width)

def print_header(text):
    separator("═")
    print(f"  {text}")
    separator("═")

def main():
    print_header("Multi-Agent Financial System -- Batch Processor")

    # List all PDFs
    pdf_files = sorted([f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")])
    print(f"\n  Found {len(pdf_files)} PDFs in DATA/:\n")
    for i, f in enumerate(pdf_files, 1):
        size_mb = os.path.getsize(os.path.join(DATA_DIR, f)) / (1024 * 1024)
        print(f"  {i:2}. {f:<45}  {size_mb:5.1f} MB")

    # Load Document Agent
    print(f"\n  Loading Document Agent (embedding model ~30s on first run)...")
    doc_agent = DocumentAgent(ROOT_DIR)
    print(f"  Document Agent ready.\n")

    # STEP 1: Process all PDFs
    separator()
    print(f"  STEP 1/2 -- Document Agent: PDF -> Chunks -> ChromaDB")
    separator()

    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(DATA_DIR, pdf_file)
        print(f"\n  [{i:2}/{len(pdf_files)}] Processing: {pdf_file}")
        try:
            result = doc_agent.process_document(pdf_path, force_reprocess=False)
            status = result.get("status", "unknown")
            if status == "already_indexed":
                print(f"        [SKIP] Already indexed")
            elif status in ("success", "ok"):
                chunks = result.get("chunks_added", result.get("total_chunks", "?"))
                print(f"        [OK]   {chunks} chunks added to ChromaDB")
            else:
                print(f"        [OK]   Status: {status}")
        except Exception as e:
            print(f"        [ERROR] {e}")

    # STEP 2: Extract financial metrics
    separator()
    print(f"\n  STEP 2/2 -- Extraction Agent: ChromaDB -> Financial JSON")
    separator()

    print(f"\n  Loading Extraction Agent...")
    ext_agent = ExtractionAgent(ROOT_DIR)
    print(f"  Extraction Agent ready.\n")

    extract_targets = []
    for pdf_file in pdf_files:
        m = re.match(
            r"^([A-Za-z0-9]+)_ANNUAL_(\d{2,4})(?:_.*)?\.pdf$",
            pdf_file,
            re.IGNORECASE,
        )
        if m:
            company = m.group(1).upper()
            year_raw = m.group(2)
            year = ("20" + year_raw) if len(year_raw) == 2 else year_raw
            extract_targets.append((company, year))

    for i, (company, year) in enumerate(extract_targets, 1):
        out_json = os.path.join(PROCESSED_DIR, f"{company}_{year}.json")
        print(f"\n  [{i:2}/{len(extract_targets)}] Extracting: {company} {year}")

        if os.path.exists(out_json):
            size_kb = os.path.getsize(out_json) // 1024
            print(f"        [SKIP] JSON already exists ({size_kb} KB)")
            continue

        try:
            ext_agent.extract(company, year)
            if os.path.exists(out_json):
                size_kb = os.path.getsize(out_json) // 1024
                print(f"        [OK]   Saved {company}_{year}.json ({size_kb} KB)")
            else:
                print(f"        [WARN] Completed but JSON not found")
        except Exception as e:
            print(f"        [ERROR] {e}")

    # Final Summary
    separator("=")
    print(f"\n  FINAL SUMMARY")
    separator()

    try:
        from database.chroma_manager import ChromaManager
        chroma = ChromaManager(os.path.join(ROOT_DIR, "chroma_db"))
        stats  = chroma.get_collection_stats()
        print(f"\n  ChromaDB:")
        print(f"    Total chunks : {stats['total_chunks']}")
        print(f"    Documents    : {len(stats['documents'])}")
        for doc_key, count in sorted(stats["documents"].items()):
            print(f"      {doc_key:<30}  {count:>6} chunks")
    except Exception as e:
        print(f"  ChromaDB stats unavailable: {e}")

    json_files = sorted([f for f in os.listdir(PROCESSED_DIR) if f.endswith(".json")])
    print(f"\n  Extracted JSONs ({len(json_files)} files):")
    for jf in json_files:
        size_kb = os.path.getsize(os.path.join(PROCESSED_DIR, jf)) // 1024
        print(f"      {jf:<35}  {size_kb:>6} KB")

    separator("=")
    print(f"\n  All done! Knowledge base ready for Milestone 3.\n")


if __name__ == "__main__":
    main()
