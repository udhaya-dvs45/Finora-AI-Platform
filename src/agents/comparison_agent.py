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
comparison_agent.py
-------------------
Comparison Agent for the Multi-Agent Financial Analysis System (Milestone 3).

Responsibilities:
1. Cross-reference financial metrics across multiple companies or multiple years.
2. Side-by-side financial benchmarking:
   - Revenue, Operating Income, Net Income, Margins
   - Balance Sheet Strength (Assets, Equity, Debt-to-Equity)
   - Risk Profiles & Red Flag counts
3. Outperformance & Variance Analysis:
   - Comparative growth & profitability ranking
   - Clear Markdown comparison table
   - Provenance tracking back to source files
4. Saves benchmark reports to outputs/comparisons/
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from agents.extraction_agent import ExtractionAgent
from agents.red_flag_agent import RedFlagAgent


class ComparisonAgent:
    """
    Comparison Agent for multi-company / multi-year financial benchmarking.
    """

    def __init__(self, root_dir: str = ROOT_DIR):
        self.root_dir = os.path.abspath(root_dir)
        self.metrics_dir = os.path.join(self.root_dir, "outputs", "financial_metrics")
        self.red_flags_dir = os.path.join(self.root_dir, "outputs", "red_flags")
        self.output_dir = os.path.join(self.root_dir, "outputs", "comparisons")
        os.makedirs(self.output_dir, exist_ok=True)

        self.extraction_agent = ExtractionAgent(self.root_dir)
        self.red_flag_agent = RedFlagAgent(self.root_dir)

    def _get_entity_data(self, company: str, year: str) -> Dict[str, Any]:
        """Load or extract metrics and red flags for a single company/year."""
        comp = company.upper().strip()
        yr = str(year).strip()
        doc_id = f"{comp}_{yr}"

        # 1. Load metrics
        metrics_file = os.path.join(self.metrics_dir, f"{doc_id}_metrics.json")
        metrics_data = None
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, "r", encoding="utf-8") as f:
                    metrics_data = json.load(f)
            except Exception:
                pass

        if not metrics_data:
            print(f"[ComparisonAgent] Extracting metrics on-the-fly for {doc_id}...")
            metrics_data = self.extraction_agent.extract(comp, yr)

        # 2. Load red flags
        rf_file = os.path.join(self.red_flags_dir, f"{doc_id}_red_flags.json")
        rf_data = None
        if os.path.exists(rf_file):
            try:
                with open(rf_file, "r", encoding="utf-8") as f:
                    rf_data = json.load(f)
            except Exception:
                pass

        if not rf_data:
            print(f"[ComparisonAgent] Scanning red flags on-the-fly for {doc_id}...")
            rf_data = self.red_flag_agent.scan(comp, yr)

        return {
            "doc_id": doc_id,
            "company": comp,
            "year": yr,
            "metrics": metrics_data.get("metrics", {}),
            "calculated_ratios": metrics_data.get("ratios", metrics_data.get("calculated_ratios", {})),
            "red_flags_summary": rf_data.get("summary", {}),
        }

    def compare(self, targets: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Compare financial performance across a list of (company, year) tuples.

        Parameters
        ----------
        targets : List of (company, year) tuples, e.g. [("AMAZON", "2023"), ("TESLA", "2023")]

        Returns
        -------
        Dict containing structured comparison table, metrics summary, and benchmarking insights.
        """
        if len(targets) < 2:
            raise ValueError("At least 2 targets required for comparison.")

        print(f"\n[ComparisonAgent] Comparing {len(targets)} entities: {targets}")

        entities = []
        for comp, yr in targets:
            data = self._get_entity_data(comp, yr)
            entities.append(data)

        # Helper to extract numeric value
        def extract_num(ent: Dict[str, Any], key: str) -> Optional[float]:
            val = ent["metrics"].get(key, {}).get("value")
            if isinstance(val, (int, float)):
                return float(val)
            return None

        # Build comparison rows
        metric_keys = [
            ("Revenue / Net Sales", "revenue", True),
            ("Operating Income", "operating_income", True),
            ("Net Income", "net_income", True),
            ("Operating Cash Flow", "operating_cash_flow", True),
            ("Total Assets", "total_assets", True),
            ("Shareholders' Equity", "shareholders_equity", True),
        ]

        table_rows = []
        for label, m_key, is_currency in metric_keys:
            row_data = {"metric": label}
            for ent in entities:
                val = extract_num(ent, m_key)
                if val is not None:
                    row_data[ent["doc_id"]] = f"{val:,.1f}" if is_currency else f"{val:.2f}"
                else:
                    raw = ent["metrics"].get(m_key, {}).get("raw_text")
                    row_data[ent["doc_id"]] = raw if raw else "N/A"
            table_rows.append(row_data)

        # Helper to extract ratio value
        def extract_ratio(ent: Dict[str, Any], key: str) -> Optional[float]:
            ratios_dict = ent.get("calculated_ratios") or {}
            entry = ratios_dict.get(key)
            if isinstance(entry, dict):
                v = entry.get("value")
                return float(v) if isinstance(v, (int, float)) else None
            elif isinstance(entry, (int, float)):
                return float(entry)
            return None

        # Add calculated ratios
        ratio_keys = [
            ("Operating Margin (%)", "operating_margin"),
            ("Net Profit Margin (%)", "net_profit_margin"),
            ("Debt-to-Equity Ratio", "debt_to_equity"),
            ("Return on Assets (%)", "return_on_assets"),
        ]
        for label, r_key in ratio_keys:
            row_data = {"metric": label}
            for ent in entities:
                val = extract_ratio(ent, r_key)
                if val is not None:
                    row_data[ent["doc_id"]] = f"{val * 100:.2f}%" if "Margin" in label or "Return" in label else f"{val:.2f}"
                else:
                    row_data[ent["doc_id"]] = "N/A"
            table_rows.append(row_data)

        # Add Red Flag Summary
        rf_row = {"metric": "Overall Risk Profile"}
        for ent in entities:
            risk = ent["red_flags_summary"].get("overall_risk_level", "UNKNOWN")
            cnt = ent["red_flags_summary"].get("total_flags", 0)
            rf_row[ent["doc_id"]] = f"{risk} ({cnt} flags)"
        table_rows.append(rf_row)

        # Generate Markdown Table
        header = ["Metric"] + [e["doc_id"] for e in entities]
        md_lines = []
        md_lines.append("| " + " | ".join(header) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        for row in table_rows:
            line_vals = [row["metric"]] + [str(row.get(e["doc_id"], "N/A")) for e in entities]
            md_lines.append("| " + " | ".join(line_vals) + " |")

        markdown_table = "\n".join(md_lines)

        # Generate Benchmarking Insights
        insights = []
        # Compare Revenues if available
        rev_list = [(e["doc_id"], extract_num(e, "revenue")) for e in entities if extract_num(e, "revenue") is not None]
        if len(rev_list) >= 2:
            rev_list.sort(key=lambda x: x[1], reverse=True)
            leader, runner_up = rev_list[0], rev_list[1]
            diff_pct = ((leader[1] - runner_up[1]) / runner_up[1]) * 100 if runner_up[1] > 0 else 0
            insights.append(f"**Scale Leadership**: {leader[0]} leads in total revenue at {leader[1]:,.1f}, which is {diff_pct:.1f}% higher than {runner_up[0]} ({runner_up[1]:,.1f}).")

        # Compare Margins if available
        margin_list = [(e["doc_id"], e["calculated_ratios"].get("operating_margin")) for e in entities if isinstance(e["calculated_ratios"].get("operating_margin"), (int, float))]
        if len(margin_list) >= 2:
            margin_list.sort(key=lambda x: x[1], reverse=True)
            insights.append(f"**Operating Efficiency**: {margin_list[0][0]} demonstrates the highest operating margin at {margin_list[0][1]:.2f}%, compared to {margin_list[-1][0]} at {margin_list[-1][1]:.2f}%.")

        # Risk comparison
        insights.append(
            "**Risk Benchmarking**: " + "; ".join(
                f"{e['doc_id']} is rated {e['red_flags_summary'].get('overall_risk_level', 'UNKNOWN')} risk ({e['red_flags_summary'].get('total_flags', 0)} flags)"
                for e in entities
            ) + "."
        )

        comparison_id = "_vs_".join([e["doc_id"] for e in entities])
        result = {
            "comparison_id": comparison_id,
            "compared_at": datetime.now().isoformat(),
            "entities": [e["doc_id"] for e in entities],
            "markdown_table": markdown_table,
            "table_data": table_rows,
            "insights": insights,
        }

        # Save comparison report
        out_file = os.path.join(self.output_dir, f"compare_{comparison_id}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"[ComparisonAgent] Comparison complete for {comparison_id}. Saved to {out_file}")
        return result


if __name__ == "__main__":
    agent = ComparisonAgent(ROOT_DIR)
    res = agent.compare([("AMAZON", "2023"), ("TESLA", "2023")])
    print("\n" + res["markdown_table"])
    print("\nInsights:")
    for ins in res["insights"]:
        print(f"- {ins}")
