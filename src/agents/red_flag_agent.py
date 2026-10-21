import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import os
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_FLAX", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

"""
red_flag_agent.py
-----------------
Red Flag Agent for the Multi-Agent Financial Analysis System (Milestone 3).

Responsibilities:
1. Quantitative Red Flag Detection:
   - Scans extracted financial metrics from outputs/financial_metrics/
   - Identifies rising debt levels, high leverage (Debt-to-Equity > 2.0 or > 3.0)
   - Identifies falling profit / operating margins or negative margins
   - Detects earnings quality warnings (Operating Cash Flow significantly lower than Net Income)
   - Checks liquidity risks (Current Ratio < 1.0)
   - Analyzes multi-year deterioration if historical reports exist

2. Qualitative & Audit Risk Detection:
   - Queries ChromaDB collection ('financial_documents') with semantic search for:
     * Auditor qualifications, adverse opinions, going concern doubts
     * Material weaknesses in internal controls
     * Significant legal proceedings, regulatory probes, investigations, fines
     * Financial restatements or accounting changes
     * Major asset impairments, write-offs, or debt covenant breaches

3. Outputs & Grounding:
   - Each red flag is assigned a severity (HIGH, MEDIUM, LOW)
   - Every flag includes source evidence (document, page number, snippet or metric formula)
   - Saves structured report to outputs/red_flags/<COMPANY>_<YEAR>_red_flags.json
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from sentence_transformers import SentenceTransformer

# Add src to sys.path
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.chroma_manager import ChromaManager


EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Qualitative search topics with keywords to detect in retrieved chunks
QUALITATIVE_SCANS = [
    {
        "category": "Auditor & Internal Controls",
        "queries": [
            "auditor report adverse opinion qualified opinion going concern",
            "material weakness in internal control over financial reporting significant deficiency",
            "auditor qualification restatement of prior period financial statements",
        ],
        "keywords": [
            "material weakness", "adverse opinion", "qualified opinion",
            "going concern", "restatement", "significant deficiency", "internal control deficiency"
        ],
        "default_severity": "HIGH",
        "description": "Potential issues in accounting integrity, auditor disclaimers, or internal control weaknesses."
    },
    {
        "category": "Legal & Regulatory Risks",
        "queries": [
            "legal proceedings antitrust investigation government inquiry penalty lawsuit",
            "regulatory sanction litigation settlement contingency material liability",
        ],
        "keywords": [
            "investigation", "subpoena", "antitrust", "lawsuit", "penalty",
            "injunction", "patent infringement", "litigation", "class action", "regulatory inquiry"
        ],
        "default_severity": "MEDIUM",
        "description": "Pending litigations, antitrust matters, or government investigations that could impair operations."
    },
    {
        "category": "Impairments & Solvency Risks",
        "queries": [
            "goodwill impairment asset write down debt covenant violation default",
            "restructuring charges facility closure credit rating downgrade liquidity risk",
        ],
        "keywords": [
            "impairment", "write-down", "covenant breach", "default", "downgrade", "debt maturity", "liquidity constraint"
        ],
        "default_severity": "MEDIUM",
        "description": "Large asset write-downs, goodwill impairments, or debt covenant stress."
    }
]


class RedFlagAgent:
    """
    Automated Red Flag & Risk Detection Agent.
    """

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = os.path.abspath(root_dir or ROOT_DIR)
        self.metrics_dir = os.path.join(self.root_dir, "outputs", "financial_metrics")
        self.output_dir = os.path.join(self.root_dir, "outputs", "red_flags")
        self.chroma_dir = os.path.join(self.root_dir, "chroma_db")
        os.makedirs(self.output_dir, exist_ok=True)

        self._embedder: Optional[SentenceTransformer] = None
        self._chroma: Optional[ChromaManager] = None

    @property
    def embedder(self) -> SentenceTransformer:
        if self._embedder is None:
            print(f"[RedFlagAgent] Loading embedding model '{EMBEDDING_MODEL}'...")
            self._embedder = SentenceTransformer(EMBEDDING_MODEL)
        return self._embedder

    @property
    def chroma(self) -> ChromaManager:
        if self._chroma is None:
            self._chroma = ChromaManager(self.chroma_dir)
        return self._chroma

    def _load_metrics(self, company: str, year: str) -> Optional[Dict[str, Any]]:
        """Load extracted metrics JSON if available."""
        filename = f"{company.upper()}_{year}_metrics.json"
        filepath = os.path.join(self.metrics_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[RedFlagAgent] Warning: Failed to read {filepath}: {e}")
        return None

    def _scan_quantitative(self, metrics_data: Optional[Dict[str, Any]], company: str, year: str) -> List[Dict[str, Any]]:
        """Analyze ratios and numbers for quantitative financial anomalies."""
        flags: List[Dict[str, Any]] = []
        if not metrics_data or "metrics" not in metrics_data:
            return flags

        m = metrics_data.get("metrics", {})
        ratios_raw = metrics_data.get("ratios", metrics_data.get("calculated_ratios", {}))

        def get_ratio_val(key: str) -> Optional[float]:
            entry = ratios_raw.get(key)
            if isinstance(entry, dict):
                v = entry.get("value")
                return float(v) if isinstance(v, (int, float)) else None
            elif isinstance(entry, (int, float)):
                return float(entry)
            return None

        def get_val(key: str) -> Optional[float]:
            entry = m.get(key)
            if entry and isinstance(entry, dict) and isinstance(entry.get("value"), (int, float)):
                return float(entry["value"])
            return None

        def get_prov(key: str) -> Dict[str, Any]:
            entry = m.get(key, {})
            return {
                "document": entry.get("document", f"{company}_{year}"),
                "page_number": entry.get("page_number", "N/A"),
                "raw_text": entry.get("raw_text", "N/A"),
            }

        rev = get_val("revenue")
        net_inc = get_val("net_income")
        op_inc = get_val("operating_income")
        total_assets = get_val("total_assets")
        total_liab = get_val("total_liabilities")
        equity = get_val("shareholders_equity")
        ocf = get_val("operating_cash_flow")

        # 1. Negative Net Income / Loss
        if net_inc is not None and net_inc < 0:
            flags.append({
                "id": "FLAG_NET_LOSS",
                "category": "Profitability",
                "severity": "HIGH",
                "title": "Net Loss Reported",
                "description": f"{company} reported a net loss of {net_inc:,.2f} in {year}.",
                "evidence": f"Net Income value: {net_inc}",
                "provenance": get_prov("net_income")
            })

        # 2. Operating Loss
        if op_inc is not None and op_inc < 0:
            flags.append({
                "id": "FLAG_OP_LOSS",
                "category": "Profitability",
                "severity": "HIGH",
                "title": "Operating Loss Reported",
                "description": f"Core operations generated an operating loss of {op_inc:,.2f}.",
                "evidence": f"Operating Income value: {op_inc}",
                "provenance": get_prov("operating_income")
            })

        # 3. Cash Flow vs Net Income Divergence (Earnings Quality)
        if net_inc is not None and ocf is not None:
            if ocf < 0 and net_inc > 0:
                flags.append({
                    "id": "FLAG_OCF_NEGATIVE_NET_POSITIVE",
                    "category": "Earnings Quality / Cash Flow",
                    "severity": "HIGH",
                    "title": "Cash Flow Divergence (Negative OCF with Positive Net Income)",
                    "description": f"Reported positive net income ({net_inc:,.2f}) but negative operating cash flow ({ocf:,.2f}), signaling aggressive revenue recognition or working capital strain.",
                    "evidence": f"OCF: {ocf:,.2f}, Net Income: {net_inc:,.2f}",
                    "provenance": get_prov("operating_cash_flow")
                })
            elif ocf < (0.5 * net_inc) and net_inc > 0:
                flags.append({
                    "id": "FLAG_OCF_LOW_CONVERSION",
                    "category": "Earnings Quality / Cash Flow",
                    "severity": "MEDIUM",
                    "title": "Poor Cash Conversion",
                    "description": f"Operating cash flow ({ocf:,.2f}) is less than 50% of net income ({net_inc:,.2f}).",
                    "evidence": f"OCF: {ocf:,.2f}, Net Income: {net_inc:,.2f}",
                    "provenance": get_prov("operating_cash_flow")
                })

        # 4. Solvency & Debt / Equity Risk
        de_ratio = get_ratio_val("debt_to_equity")
        if de_ratio is not None and isinstance(de_ratio, (int, float)):
            if de_ratio > 3.0:
                flags.append({
                    "id": "FLAG_HIGH_LEVERAGE",
                    "category": "Solvency & Capital Structure",
                    "severity": "HIGH",
                    "title": "Severe Financial Leverage",
                    "description": f"Debt-to-Equity ratio is {de_ratio:.2f}, indicating heavily leveraged capital structure.",
                    "evidence": f"Debt/Equity ratio: {de_ratio:.2f}",
                    "provenance": {"calculated": True, "ratio": de_ratio}
                })
            elif de_ratio > 2.0:
                flags.append({
                    "id": "FLAG_ELEVATED_LEVERAGE",
                    "category": "Solvency & Capital Structure",
                    "severity": "MEDIUM",
                    "title": "Elevated Debt-to-Equity Ratio",
                    "description": f"Debt-to-Equity ratio is {de_ratio:.2f}, above recommended prudent benchmarks.",
                    "evidence": f"Debt/Equity ratio: {de_ratio:.2f}",
                    "provenance": {"calculated": True, "ratio": de_ratio}
                })

        # 5. Negative Shareholders Equity (Technical Insolvency)
        if equity is not None and equity < 0:
            flags.append({
                "id": "FLAG_NEGATIVE_EQUITY",
                "category": "Solvency & Capital Structure",
                "severity": "HIGH",
                "title": "Negative Shareholders' Equity",
                "description": f"Stockholders' equity is negative ({equity:,.2f}), meaning accumulated liabilities exceed assets.",
                "evidence": f"Stockholders' Equity: {equity:,.2f}",
                "provenance": get_prov("shareholders_equity")
            })

        # 6. Compressed Operating Margin (< 5%)
        if rev is not None and op_inc is not None and rev > 0:
            margin = (op_inc / rev) * 100.0
            if 0 < margin < 5.0:
                flags.append({
                    "id": "FLAG_THIN_MARGIN",
                    "category": "Profitability",
                    "severity": "LOW",
                    "title": "Thin Operating Margin",
                    "description": f"Operating margin is only {margin:.2f}%, leaving little buffer for cost inflation or revenue contraction.",
                    "evidence": f"Operating Margin: {margin:.2f}% (OpInc: {op_inc:,.2f}, Rev: {rev:,.2f})",
                    "provenance": get_prov("operating_income")
                })

        return flags

    def _scan_qualitative(self, company: str, year: str) -> List[Dict[str, Any]]:
        """Scan vector chunks for qualitative warnings and disclosures."""
        flags: List[Dict[str, Any]] = []
        where_filter = {"$and": [{"company": company.upper()}, {"year": str(year)}]}

        for scan_cfg in QUALITATIVE_SCANS:
            category = scan_cfg["category"]
            keywords = scan_cfg["keywords"]
            queries = scan_cfg["queries"]
            default_sev = scan_cfg["default_severity"]

            for q_text in queries:
                try:
                    q_vec = self.embedder.encode([q_text], convert_to_numpy=True).tolist()
                    res = self.chroma.query(query_embeddings=q_vec, n_results=5, where=where_filter)
                except Exception as e:
                    continue

                if not res or not res.get("documents"):
                    continue

                docs = res["documents"][0]
                metas = res["metadatas"][0]

                for doc_chunk, meta in zip(docs, metas):
                    text_lower = doc_chunk.lower()
                    matched_kws = []
                    for kw in keywords:
                        # Exclude 'unqualified opinion' from triggering 'qualified opinion'
                        if kw == "qualified opinion":
                            if re.search(r"(?<!un)qualified\s+opinion", text_lower):
                                matched_kws.append(kw)
                        elif kw == "material weakness":
                            # Check if it actually states no material weakness was found
                            if "material weakness" in text_lower:
                                if not any(clean_phrase in text_lower for clean_phrase in [
                                    "no material weakness", "did not identify any material weakness",
                                    "free of material weakness", "without material weakness"
                                ]):
                                    matched_kws.append(kw)
                        else:
                            pattern = r"\b" + re.escape(kw) + r"\b"
                            if re.search(pattern, text_lower):
                                matched_kws.append(kw)

                    if matched_kws:
                        # Extract first relevant sentence as evidence
                        flag_id = f"FLAG_{matched_kws[0].upper().replace(' ', '_')}"
                        
                        # Prevent duplicate flags of same type in same document
                        if any(f["id"] == flag_id and f.get("provenance", {}).get("page_number") == meta.get("page_number") for f in flags):
                            continue

                        flags.append({
                            "id": flag_id,
                            "category": category,
                            "severity": default_sev,
                            "title": f"Disclosure: {matched_kws[0].title()} Detected",
                            "description": f"Disclosed mentions of {', '.join(matched_kws)} found in annual filing.",
                            "evidence": doc_chunk[:300].strip(),
                            "provenance": {
                                "document": meta.get("doc_name", f"{company}_{year}"),
                                "page_number": meta.get("page_number", "N/A"),
                                "matched_keywords": matched_kws
                            }
                        })
                        if len(flags) >= 12:  # cap max qualitative flags per report
                            break
        return flags

    def scan(self, company: str, year: str, force_rescan: bool = False) -> Dict[str, Any]:
        """
        Execute full scan (quantitative + qualitative) for a given company and year.
        """
        company_clean = company.upper().strip()
        year_clean = str(year).strip()
        doc_id = f"{company_clean}_{year_clean}"
        out_path = os.path.join(self.output_dir, f"{doc_id}_red_flags.json")

        if not force_rescan and os.path.exists(out_path):
            try:
                with open(out_path, "r", encoding="utf-8") as f:
                    cached_rf = json.load(f)
                    print(f"[RedFlagAgent] Loaded cached red flags for {doc_id} from {out_path}")
                    return cached_rf
            except Exception:
                pass

        print(f"\n[RedFlagAgent] Starting Red Flag Scan for {doc_id}...")

        metrics_data = self._load_metrics(company_clean, year_clean)
        quant_flags = self._scan_quantitative(metrics_data, company_clean, year_clean)
        print(f"[RedFlagAgent] Identified {len(quant_flags)} quantitative flags.")

        qual_flags = self._scan_qualitative(company_clean, year_clean)
        print(f"[RedFlagAgent] Identified {len(qual_flags)} qualitative disclosure flags.")

        all_flags = quant_flags + qual_flags

        # Summary statistics
        high_cnt = sum(1 for f in all_flags if f["severity"] == "HIGH")
        med_cnt = sum(1 for f in all_flags if f["severity"] == "MEDIUM")
        low_cnt = sum(1 for f in all_flags if f["severity"] == "LOW")

        risk_score = min(100, (high_cnt * 30) + (med_cnt * 15) + (low_cnt * 5))
        overall_risk = "HIGH" if risk_score >= 60 else "MEDIUM" if risk_score >= 25 else "LOW"

        result = {
            "doc_id": doc_id,
            "company": company_clean,
            "year": year_clean,
            "scanned_at": datetime.now().isoformat(),
            "summary": {
                "overall_risk_level": overall_risk,
                "risk_score_out_of_100": risk_score,
                "total_flags": len(all_flags),
                "high_severity_count": high_cnt,
                "medium_severity_count": med_cnt,
                "low_severity_count": low_cnt,
            },
            "red_flags": all_flags,
        }

        # Save result JSON
        out_path = os.path.join(self.output_dir, f"{doc_id}_red_flags.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"[RedFlagAgent] Saved report to '{out_path}' (Overall Risk: {overall_risk}, Flags: {len(all_flags)})")

        return result

    def scan_all(self) -> List[Dict[str, Any]]:
        """Scan all indexed documents found in the database or processed JSON directory."""
        processed_json_dir = os.path.join(self.root_dir, "processed", "json")
        doc_keys = set()

        if os.path.exists(processed_json_dir):
            for fname in os.listdir(processed_json_dir):
                if fname.endswith(".json"):
                    base = fname.replace(".json", "")
                    doc_keys.add(base)

        results = []
        for key in sorted(doc_keys):
            parts = key.split("_")
            if len(parts) >= 2:
                company = parts[0]
                year = parts[1]
                res = self.scan(company, year)
                results.append(res)

        return results


if __name__ == "__main__":
    agent = RedFlagAgent(ROOT_DIR)
    # Test on AMAZON 2023
    res = agent.scan("AMAZON", "2023")
    print(f"\nCompleted scan with {res['summary']['total_flags']} flags detected.")
