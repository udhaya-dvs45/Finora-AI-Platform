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
extraction_agent.py
--------------------
ExtractionAgent for the Multi-Agent Financial Analysis System.

Responsibilities:
- Query ChromaDB for semantically relevant chunks per financial metric
- Parse numerical values from retrieved text using regex patterns
- Calculate derived financial ratios where source values are available
- Preserve full source provenance (document, page, company, year, source text)
- Save structured results to outputs/financial_metrics/<COMPANY>_<YEAR>_metrics.json

Extracted metrics:
    Revenue, Net Income, Operating Income, Gross Profit
    Total Assets, Total Liabilities, Shareholders Equity
    Operating Cash Flow, EPS
    Revenue Trends / Key Performance Numbers

Calculated ratios (only when both source values are present):
    Net Profit Margin, Gross Margin, Debt-to-Equity, ROA, Current Ratio
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from sentence_transformers import SentenceTransformer

import sys
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.chroma_manager import ChromaManager


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K_CHUNKS    = 15    # number of chunks to retrieve per metric query


# -----------------------------------------------------------------------------
# Metric query definitions
#   Each metric has one or more natural-language queries sent to ChromaDB
#   and a list of regex patterns used to extract the numerical value.
# -----------------------------------------------------------------------------

METRIC_QUERIES: Dict[str, List[str]] = {
    "revenue": [
        "total revenue net sales annual",
        "revenue for the year fiscal year revenue",
        "net revenue total net sales",
    ],
    "net_income": [
        "net income net earnings net profit",
        "net income attributable to common shareholders",
        "net loss net profit for the year",
    ],
    "operating_income": [
        "operating income income from operations",
        "operating profit loss from operations",
    ],
    "gross_profit": [
        "gross profit gross margin",
        "revenue cost of goods sold gross profit",
    ],
    "total_assets": [
        "total assets balance sheet assets",
        "total assets as of fiscal year end",
    ],
    "total_liabilities": [
        "total liabilities total debt obligations",
        "total liabilities shareholders equity balance sheet",
    ],
    "shareholders_equity": [
        "total shareholders equity stockholders equity",
        "equity attributable to common shareholders",
        "total equity book value",
    ],
    "operating_cash_flow": [
        "cash flow from operations operating activities",
        "net cash provided by operating activities",
        "operating cash flow free cash flow",
    ],
    "eps": [
        "earnings per share diluted EPS",
        "basic diluted earnings per share",
        "net income per share EPS",
    ],
    "revenue_trend": [
        "year over year revenue growth",
        "revenue increased decreased percent",
        "revenue growth rate annual comparison",
    ],
}


# -----------------------------------------------------------------------------
# Regex patterns for numeric extraction
# -----------------------------------------------------------------------------

# Matches values like: $12.5 billion, $1,234 million, 99.5%, (1,234), 12.50
_CURRENCY_PATTERN = re.compile(
    r"""
    (?:
        (?:\$|₹|€|£|¥|INR\s?|USD\s?)?      # optional currency symbol/code
        [-−]?                                # optional minus sign
        \(?\s*                               # optional opening paren (negative)
        (?:\d{1,3}(?:,\d{3})*|\d+)         # integer with optional thousands comma
        (?:\.\d+)?                           # optional decimal part
        \s*\)?                               # optional closing paren
        (?:\s*(?:billion|million|trillion|   # optional scale word
               crore|lakh|lakhs|
               bn|mn|tr|B|M|T))?
        |
        [-−]?\d+\.\d+                        # plain decimal
    )
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Context patterns for specific metrics -- captures the value after the label
_METRIC_PATTERNS: Dict[str, List[re.Pattern]] = {
    "revenue": [
        re.compile(r"(?:net\s+)?(?:total\s+)?(?:revenue|net\s+sales|revenues)\s*[:\-]?\s*([\$₹€£]?\s*[\d,\.]+\s*(?:billion|million|trillion|crore|lakh|bn|mn|B|M|T)?)", re.IGNORECASE),
    ],
    "net_income": [
        re.compile(r"net\s+(?:income|earnings|profit|loss)\s*(?:attributable[^:]*?)?\s*[:\-]?\s*([\$₹€£\(]?\s*[\d,\.]+\s*(?:billion|million|trillion|crore|lakh|bn|mn|B|M|T)?\s*\)?)", re.IGNORECASE),
    ],
    "operating_income": [
        re.compile(r"(?:operating\s+income|income\s+from\s+operations|operating\s+profit)\s*[:\-]?\s*([\$₹€£\(]?\s*[\d,\.]+\s*(?:billion|million|trillion|crore|lakh|bn|mn|B|M|T)?\s*\)?)", re.IGNORECASE),
    ],
    "gross_profit": [
        re.compile(r"gross\s+profit\s*[:\-]?\s*([\$₹€£\(]?\s*[\d,\.]+\s*(?:billion|million|trillion|crore|lakh|bn|mn|B|M|T)?\s*\)?)", re.IGNORECASE),
    ],
    "total_assets": [
        re.compile(r"total\s+assets\s*[:\-]?\s*([\$₹€£]?\s*[\d,\.]+\s*(?:billion|million|trillion|crore|lakh|bn|mn|B|M|T)?)", re.IGNORECASE),
    ],
    "total_liabilities": [
        re.compile(r"total\s+liabilities\s*[:\-]?\s*([\$₹€£]?\s*[\d,\.]+\s*(?:billion|million|trillion|crore|lakh|bn|mn|B|M|T)?)", re.IGNORECASE),
    ],
    "shareholders_equity": [
        re.compile(r"(?:total\s+)?(?:stockholders|shareholders)\s*['\u2019]?\s*equity\s*[:\-]?\s*([\$₹€£\(]?\s*[\d,\.]+\s*(?:billion|million|trillion|crore|lakh|bn|mn|B|M|T)?\s*\)?)", re.IGNORECASE),
        re.compile(r"total\s+equity\s*[:\-]?\s*([\$₹€£\(]?\s*[\d,\.]+\s*(?:billion|million|trillion|crore|lakh|bn|mn|B|M|T)?\s*\)?)", re.IGNORECASE),
    ],
    "operating_cash_flow": [
        re.compile(r"(?:net\s+cash\s+(?:provided\s+by|from)\s+operating\s+activities|operating\s+cash\s+flow)\s*[:\-]?\s*([\$₹€£\(]?\s*[\d,\.]+\s*(?:billion|million|trillion|crore|lakh|bn|mn|B|M|T)?\s*\)?)", re.IGNORECASE),
    ],
    "eps": [
        re.compile(r"(?:diluted|basic)\s+(?:net\s+)?(?:earnings|income|loss)\s+per\s+share\s*[:\-]?\s*([\$₹€£\(]?\s*[\d,\.]+\s*\)?)", re.IGNORECASE),
        re.compile(r"(?:earnings|loss)\s+per\s+(?:diluted|basic)?\s*share\s*[:\-]?\s*([\$₹€£\(]?\s*[\d,\.]+\s*\)?)", re.IGNORECASE),
        re.compile(r"EPS\s*[:\-]?\s*([\$₹€£\(]?\s*[\d,\.]+\s*\)?)", re.IGNORECASE),
    ],
    "revenue_trend": [
        re.compile(r"(?:revenue|sales)\s+(?:increased|decreased|grew|declined|rose|fell|was)\s+(?:by\s+)?([^\.\n]{0,80})", re.IGNORECASE),
        re.compile(r"(\d+(?:\.\d+)?%?\s+(?:increase|decrease|growth|decline)\s+in\s+(?:revenue|net\s+sales))", re.IGNORECASE),
    ],
}


# -----------------------------------------------------------------------------
# Utility -- clean and normalise extracted numeric strings
# -----------------------------------------------------------------------------

def _clean_value(raw: str) -> str:
    """Strip extra whitespace and normalise minus / parenthesis notation."""
    v = raw.strip()
    # Replace en-dash minus
    v = v.replace("\u2212", "-").replace("\u2013", "-")
    # (1,234) -> -1,234
    if v.startswith("(") and v.endswith(")"):
        v = "-" + v[1:-1].strip()
    return v.strip()


def _try_parse_float(value_str: str) -> Optional[float]:
    """
    Attempt to convert a cleaned value string to a float.

    Handles: commas, currency symbols, scale words (billion/million/etc.).
    Returns None on failure.
    """
    s = value_str.strip()
    # Remove currency symbols
    s = re.sub(r"[₹$€£¥]", "", s)
    s = s.strip()

    # Detect and remove scale multiplier
    multiplier = 1.0
    scale_match = re.search(
        r"\b(billion|trillion|million|crore|lakh|lakhs|bn|mn|tr|B|M|T)\b",
        s,
        re.IGNORECASE,
    )
    if scale_match:
        scale_word = scale_match.group(1).lower()
        scale_map = {
            "trillion": 1e12, "tr": 1e12,
            "billion": 1e9,   "bn": 1e9,  "b": 1e9,
            "million": 1e6,   "mn": 1e6,  "m": 1e6,
            "crore": 1e7,
            "lakh": 1e5,      "lakhs": 1e5,
        }
        multiplier = scale_map.get(scale_word, 1.0)
        s = s[:scale_match.start()].strip()

    # Remove commas (thousands separator)
    s = s.replace(",", "")

    try:
        return float(s) * multiplier
    except ValueError:
        return None


# -----------------------------------------------------------------------------
# ExtractionAgent
# -----------------------------------------------------------------------------

class ExtractionAgent:
    """
    Extracts key financial metrics from ChromaDB-indexed document chunks.

    Usage
    -----
    agent = ExtractionAgent(project_root="/path/to/INFOSYS_INTERN")
    result = agent.extract(company="AMAZON", year="2023")
    agent.extract_all()
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Parameters
        ----------
        project_root : Root directory of the project.
        """
        self.project_root   = os.path.abspath(project_root or ROOT_DIR)
        self.output_dir     = os.path.join(self.project_root, "outputs", "financial_metrics")
        self.chroma_db_path = os.path.join(self.project_root, "chroma_db")

        os.makedirs(self.output_dir, exist_ok=True)

        print(f"[ExtractionAgent] Loading embedding model '{EMBEDDING_MODEL}' ...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        print(f"[ExtractionAgent] Embedding model ready.")

        self.chroma = ChromaManager(self.chroma_db_path)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def extract(self, company: str, year: str, force_reextract: bool = False) -> Dict[str, Any]:
        """
        Extract all financial metrics for a specific company-year document.

        Parameters
        ----------
        company : Company name (e.g. 'AMAZON') -- case-insensitive.
        year    : Year string (e.g. '2023').
        force_reextract : If True, recalculate and re-query ChromaDB even if already saved.

        Returns
        -------
        Full metrics dict saved to outputs/financial_metrics/<COMPANY>_<YEAR>_metrics.json
        """
        company = company.upper().strip()
        year = str(year).strip()
        doc_key = f"{company}_{year}"
        out_path = os.path.join(self.output_dir, f"{doc_key}_metrics.json")

        if not force_reextract and os.path.exists(out_path):
            try:
                with open(out_path, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                    print(f"[ExtractionAgent] Loaded cached metrics for {doc_key} from {out_path}")
                    return cached_data
            except Exception as e:
                print(f"[ExtractionAgent] Notice: Failed reading cache ({e}), re-extracting...")

        print(f"\n[ExtractionAgent] -- Extracting: {company} {year} -------------")

        # Verify document exists in ChromaDB
        stats = self.chroma.get_collection_stats()
        doc_key = f"{company}_{year}"
        if doc_key not in stats["documents"]:
            available = list(stats["documents"].keys())
            raise ValueError(
                f"[ExtractionAgent] '{doc_key}' not found in ChromaDB.\n"
                f"Available documents: {available}\n"
                "Run DocumentAgent first to process and index this PDF."
            )

        print(f"[ExtractionAgent]   Found {stats['documents'][doc_key]} chunks in ChromaDB.")

        # Extract each metric
        metrics: Dict[str, Any] = {}
        for metric_name, queries in METRIC_QUERIES.items():
            print(f"[ExtractionAgent]   Extracting: {metric_name} ...", end=" ")
            result = self._extract_metric(metric_name, queries, company, year)
            metrics[metric_name] = result
            found = "[OK]" if result.get("value") is not None else "-"
            print(found)

        # Calculate derived ratios
        ratios = self._calculate_ratios(metrics)

        # Assemble output document
        output = {
            "doc_id":       doc_key,
            "company":      company,
            "year":         year,
            "extracted_at": datetime.now().isoformat(),
            "metrics":      metrics,
            "ratios":       ratios,
        }

        # Save to disk
        out_path = os.path.join(self.output_dir, f"{doc_key}_metrics.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"[ExtractionAgent] [OK] Saved -> {out_path}")

        # Print human-readable summary
        self._print_summary(output)

        return output

    def extract_all(self) -> List[Dict[str, Any]]:
        """
        Extract financial metrics for every document currently indexed in ChromaDB.

        Returns
        -------
        List of result dicts.
        """
        stats = self.chroma.get_collection_stats()
        doc_keys = list(stats["documents"].keys())

        if not doc_keys:
            print("[ExtractionAgent] No documents found in ChromaDB. "
                  "Run DocumentAgent first.")
            return []

        print(f"\n[ExtractionAgent] Extracting metrics for {len(doc_keys)} document(s).")
        results = []
        for doc_key in sorted(doc_keys):
            parts = doc_key.split("_", 1)
            company = parts[0]
            year    = parts[1] if len(parts) > 1 else "unknown"
            try:
                result = self.extract(company, year)
                results.append(result)
            except Exception as e:
                print(f"[ExtractionAgent] ERROR for '{doc_key}': {e}")
                results.append({"doc_id": doc_key, "status": "error", "error": str(e)})

        return results

    # -------------------------------------------------------------------------
    # Core extraction logic
    # -------------------------------------------------------------------------

    def _extract_metric(
        self,
        metric_name: str,
        queries: List[str],
        company: str,
        year: str,
    ) -> Dict[str, Any]:
        """
        Query ChromaDB for relevant chunks and parse the metric value.

        Returns
        -------
        Dict with: value (float or str or None), raw_text, source_text,
                   document, page_number, company, year, confidence.
        """
        best_result: Dict[str, Any] = {
            "value":       None,
            "raw_text":    None,
            "source_text": None,
            "document":    None,
            "page_number": None,
            "company":     company,
            "year":        year,
            "confidence":  "not_found",
            "all_candidates": [],
        }

        where_filter = {"$and": [{"company": company}, {"year": year}]}
        patterns = _METRIC_PATTERNS.get(metric_name, [])

        for query_text in queries:
            query_embedding = self.embedder.encode(
                [query_text], convert_to_numpy=True
            ).tolist()

            try:
                results = self.chroma.query(
                    query_embeddings=query_embedding,
                    n_results=TOP_K_CHUNKS,
                    where=where_filter,
                )
            except Exception:
                continue

            if not results or not results.get("documents"):
                continue

            chunks    = results["documents"][0]
            metas     = results["metadatas"][0]
            distances = results["distances"][0]

            for chunk_text, meta, dist in zip(chunks, metas, distances):
                for pattern in patterns:
                    for m in pattern.finditer(chunk_text):
                        raw = m.group(1) if m.lastindex else m.group(0)
                        cleaned = _clean_value(raw)
                        numeric = _try_parse_float(cleaned)

                        candidate = {
                            "value":       numeric if numeric is not None else cleaned,
                            "raw_text":    cleaned,
                            "source_text": chunk_text[:400],   # truncate for storage
                            "document":    meta.get("doc_name", ""),
                            "page_number": meta.get("page_number", None),
                            "company":     meta.get("company", company),
                            "year":        meta.get("year", year),
                            "distance":    dist,
                        }
                        best_result["all_candidates"].append(candidate)

        # Pick best candidate: prefer numeric values, then closest distance
        candidates = best_result["all_candidates"]
        if candidates:
            # Prefer candidates with a numeric value
            numeric_cands = [c for c in candidates if isinstance(c["value"], float)]
            pool = numeric_cands if numeric_cands else candidates

            # Sort by distance (lower = more similar)
            pool.sort(key=lambda c: c.get("distance", 1.0))
            best = pool[0]

            best_result["value"]       = best["value"]
            best_result["raw_text"]    = best["raw_text"]
            best_result["source_text"] = best["source_text"]
            best_result["document"]    = best["document"]
            best_result["page_number"] = best["page_number"]
            best_result["confidence"]  = "high" if isinstance(best["value"], float) else "low"

        # Remove the verbose all_candidates list from final storage (keep only best)
        best_result.pop("all_candidates", None)

        return best_result

    # -------------------------------------------------------------------------
    # Ratio calculations
    # -------------------------------------------------------------------------

    def _calculate_ratios(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate derived financial ratios from the extracted base metrics.

        Only calculated when both required source values are available as floats.
        Returns a dict of ratio_name -> {value, formula, inputs_used}.
        """
        def _get_float(key: str) -> Optional[float]:
            v = metrics.get(key, {}).get("value")
            return v if isinstance(v, float) else None

        revenue            = _get_float("revenue")
        net_income         = _get_float("net_income")
        gross_profit       = _get_float("gross_profit")
        total_assets       = _get_float("total_assets")
        total_liabilities  = _get_float("total_liabilities")
        equity             = _get_float("shareholders_equity")

        ratios: Dict[str, Any] = {}

        # Net Profit Margin = Net Income / Revenue
        if net_income is not None and revenue and revenue != 0:
            ratios["net_profit_margin"] = {
                "value":       round(net_income / revenue, 4),
                "percentage":  f"{round(net_income / revenue * 100, 2)}%",
                "formula":     "Net Income / Revenue",
                "inputs_used": {"net_income": net_income, "revenue": revenue},
            }

        # Gross Margin = Gross Profit / Revenue
        if gross_profit is not None and revenue and revenue != 0:
            ratios["gross_margin"] = {
                "value":       round(gross_profit / revenue, 4),
                "percentage":  f"{round(gross_profit / revenue * 100, 2)}%",
                "formula":     "Gross Profit / Revenue",
                "inputs_used": {"gross_profit": gross_profit, "revenue": revenue},
            }

        # Debt-to-Equity = Total Liabilities / Shareholders Equity
        if total_liabilities is not None and equity is not None and equity != 0:
            ratios["debt_to_equity"] = {
                "value":       round(total_liabilities / equity, 4),
                "formula":     "Total Liabilities / Shareholders Equity",
                "inputs_used": {"total_liabilities": total_liabilities, "equity": equity},
            }

        # Return on Assets = Net Income / Total Assets
        if net_income is not None and total_assets is not None and total_assets != 0:
            ratios["return_on_assets"] = {
                "value":       round(net_income / total_assets, 4),
                "percentage":  f"{round(net_income / total_assets * 100, 2)}%",
                "formula":     "Net Income / Total Assets",
                "inputs_used": {"net_income": net_income, "total_assets": total_assets},
            }

        # Equity Ratio = Shareholders Equity / Total Assets
        if equity is not None and total_assets is not None and total_assets != 0:
            ratios["equity_ratio"] = {
                "value":       round(equity / total_assets, 4),
                "percentage":  f"{round(equity / total_assets * 100, 2)}%",
                "formula":     "Shareholders Equity / Total Assets",
                "inputs_used": {"equity": equity, "total_assets": total_assets},
            }

        return ratios

    # -------------------------------------------------------------------------
    # Display helpers
    # -------------------------------------------------------------------------

    def _print_summary(self, output: Dict[str, Any]) -> None:
        """Print a human-readable summary of extracted metrics to stdout."""
        print(f"\n{'='*65}")
        print(f"  Financial Metrics  --  {output['company']}  {output['year']}")
        print(f"{'='*65}")

        metrics = output.get("metrics", {})
        for key, data in metrics.items():
            val  = data.get("value")
            page = data.get("page_number", "?")
            conf = data.get("confidence", "?")

            if val is None:
                display = "NOT FOUND"
            elif isinstance(val, float):
                display = f"{val:,.2f}"
            else:
                display = str(val)[:60]

            print(f"  {key:<25} {display:<30} (page {page}, conf={conf})")

        ratios = output.get("ratios", {})
        if ratios:
            print(f"\n  --- Calculated Ratios ---")
            for ratio_name, ratio_data in ratios.items():
                pct = ratio_data.get("percentage", "")
                print(f"  {ratio_name:<25} {ratio_data['value']:<15} {pct}")

        print(f"{'='*65}\n")
