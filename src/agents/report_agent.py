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
report_agent.py
---------------
Complete Report Agent for the Financial Multi-Agent System (Milestone 4).

Compiles outputs from ALL agents into a structured PDF report covering:
  1. Executive Summary
  2. Key Financial Highlights & Ratio Analysis
  3. Red Flag & Audit Risk Assessment
  4. Company Comparison / Benchmarking
  5. Strategic Outlook & Recommendation

PDF generation uses only the Python stdlib + a lightweight HTML-to-PDF
approach via PyMuPDF (fitz), which is already a project dependency.

Output formats:
  - JSON  (outputs/reports/<DOC_ID>_report.json)
  - MD    (outputs/reports/<DOC_ID>_report.md)
  - PDF   (outputs/reports/<DOC_ID>_report.pdf)
"""

import json
import time
import fitz  # PyMuPDF — already in requirements.txt
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# ---------------------------------------------------------------------------
# PDF Theme Constants
# ---------------------------------------------------------------------------
COLORS = {
    "navy":       (15, 23, 42),
    "slate700":   (51, 65, 85),
    "slate500":   (100, 116, 139),
    "slate300":   (203, 213, 225),
    "white":      (255, 255, 255),
    "gold":       (217, 119, 6),
    "emerald":    (16, 185, 129),
    "rose":       (244, 63, 94),
    "blue":       (37, 99, 235),
    "indigo":     (99, 102, 241),
    "amber_bg":   (255, 251, 235),
    "emerald_bg": (236, 253, 245),
    "rose_bg":    (255, 241, 242),
    "blue_bg":    (239, 246, 255),
}

PAGE_W = 595.28  # A4 width  in points
PAGE_H = 841.89  # A4 height in points
MARGIN = 50
CONTENT_W = PAGE_W - 2 * MARGIN


class ReportAgent:
    """
    Synthesizes extracted metrics, red flag findings, comparison data,
    and research insights into a comprehensive executive PDF report.
    """

    def __init__(self, root_dir: str = ROOT_DIR):
        self.root_dir = os.path.abspath(root_dir)
        self.output_dir = os.path.join(self.root_dir, "outputs", "reports")
        os.makedirs(self.output_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # PUBLIC: generate()
    # ------------------------------------------------------------------
    def generate(
        self,
        company: str,
        year: str,
        extracted_metrics: Dict[str, Any],
        red_flag_result: Dict[str, Any],
        comparison: Optional[Dict[str, Any]] = None,
        research_insights: Optional[List[str]] = None,
        force_regenerate: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate complete structured report in JSON, Markdown, and PDF.
        """
        start_time = time.time()
        company_clean = company.upper().strip()
        year_clean = str(year).strip()
        doc_id = f"{company_clean}_{year_clean}"
        out_json = os.path.join(self.output_dir, f"{doc_id}_report.json")

        # -- Cache check
        if not force_regenerate and os.path.exists(out_json):
            try:
                with open(out_json, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                    print(f"[ReportAgent] Loaded cached report for {doc_id}")
                    return cached
            except Exception:
                pass

        print(f"[ReportAgent] Generating comprehensive report for {doc_id}...")

        # -- Extract raw data
        m = extracted_metrics.get("metrics", {})
        ratios = extracted_metrics.get("ratios", extracted_metrics.get("calculated_ratios", {}))
        rf_summary = red_flag_result.get("summary", {})
        flags = red_flag_result.get("red_flags", [])

        # Metric helpers
        def get_val(k: str) -> str:
            v = m.get(k, {}).get("value") if isinstance(m.get(k), dict) else m.get(k)
            if isinstance(v, (int, float)):
                return f"{v:,.2f}"
            return str(v) if v else "N/A"

        def get_r(k: str, is_pct: bool = False) -> str:
            entry = ratios.get(k)
            v = entry.get("value") if isinstance(entry, dict) else entry
            if isinstance(v, (int, float)):
                return f"{v * 100:.2f}%" if is_pct else f"{v:.2f}"
            return "N/A"

        rev = get_val("revenue")
        net_inc = get_val("net_income")
        op_inc = get_val("operating_income")
        assets = get_val("total_assets")
        equity = get_val("shareholders_equity")
        total_debt = get_val("total_debt")
        cash = get_val("cash_and_equivalents")
        ebitda = get_val("ebitda")
        fcf = get_val("free_cash_flow")
        cogs = get_val("cost_of_goods_sold")
        gross_profit = get_val("gross_profit")

        net_margin = get_r("net_profit_margin", is_pct=True)
        op_margin = get_r("operating_margin", is_pct=True)
        gross_margin = get_r("gross_margin", is_pct=True)
        debt_to_equity = get_r("debt_to_equity", is_pct=False)
        roa = get_r("return_on_assets", is_pct=True)
        roe = get_r("return_on_equity", is_pct=True)
        current_ratio = get_r("current_ratio", is_pct=False)
        eps = get_val("diluted_eps")

        overall_risk = rf_summary.get("overall_risk_level", "LOW")
        total_flags = rf_summary.get("total_flags", 0)
        high_flags = rf_summary.get("high_severity_count", 0)
        med_flags = rf_summary.get("medium_severity_count", 0)
        low_flags = rf_summary.get("low_severity_count", 0)
        risk_score = rf_summary.get("risk_score_out_of_100", 0)

        # -- Build Markdown Report
        md_lines = self._build_markdown(
            company_clean, year_clean, rev, net_inc, op_inc, assets, equity,
            total_debt, cash, ebitda, fcf, gross_profit, cogs, eps,
            net_margin, op_margin, gross_margin, debt_to_equity, roa, roe,
            current_ratio, overall_risk, total_flags, high_flags, med_flags,
            low_flags, risk_score, flags, comparison, research_insights,
        )
        report_md = "\n".join(md_lines)

        # -- Build structured data
        report_data = {
            "doc_id": doc_id,
            "company": company_clean,
            "year": year_clean,
            "generated_at": datetime.now().isoformat(),
            "generation_time_seconds": 0,
            "executive_summary": {
                "revenue": rev,
                "net_income": net_inc,
                "operating_income": op_inc,
                "total_assets": assets,
                "shareholders_equity": equity,
                "overall_risk": overall_risk,
                "total_flags": total_flags,
                "risk_score": risk_score,
            },
            "key_financials": {
                "net_margin": net_margin,
                "op_margin": op_margin,
                "gross_margin": gross_margin,
                "debt_to_equity": debt_to_equity,
                "roa": roa,
                "roe": roe,
                "current_ratio": current_ratio,
                "eps": eps,
                "ebitda": ebitda,
                "fcf": fcf,
            },
            "red_flags": {
                "overall_risk_level": overall_risk,
                "risk_score_out_of_100": risk_score,
                "total_flags": total_flags,
                "high": high_flags,
                "medium": med_flags,
                "low": low_flags,
                "top_flags": [
                    {
                        "title": f["title"],
                        "severity": f["severity"],
                        "category": f["category"],
                        "description": f["description"],
                        "citation": {
                            "document": f.get("provenance", {}).get("document", "N/A"),
                            "page": f.get("provenance", {}).get("page_number", "N/A"),
                        },
                    }
                    for f in flags[:10]
                ],
            },
            "comparison": comparison or {},
            "markdown_report": report_md,
        }

        md_file = os.path.join(self.output_dir, f"{doc_id}_report.md")
        pdf_path = os.path.join(self.output_dir, f"{doc_id}_report.pdf")

        if overall_risk == "HIGH":
            rec_level = "CAUTION / MONITOR"
        elif overall_risk == "MEDIUM":
            rec_level = "NEUTRAL / HOLD"
        else:
            rec_level = "BUY / ACCUMULATE"

        report_data["recommendation"] = rec_level
        report_data["overall_risk_level"] = overall_risk
        report_data["json_path"] = out_json
        report_data["markdown_path"] = md_file
        report_data["pdf_path"] = pdf_path

        # -- Save JSON
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        # -- Save Markdown
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(report_md)

        # -- Generate PDF
        self._generate_pdf(
            pdf_path, company_clean, year_clean,
            rev, net_inc, op_inc, assets, equity, total_debt, cash,
            ebitda, fcf, gross_profit, cogs, eps,
            net_margin, op_margin, gross_margin, debt_to_equity,
            roa, roe, current_ratio,
            overall_risk, total_flags, high_flags, med_flags, low_flags,
            risk_score, flags, comparison, research_insights,
        )
        report_data["pdf_path"] = pdf_path
        report_data["generation_time_seconds"] = round(time.time() - start_time, 2)

        print(f"[ReportAgent] Report generated in {report_data['generation_time_seconds']}s")
        print(f"  -> JSON: {out_json}")
        print(f"  -> MD:   {md_file}")
        print(f"  -> PDF:  {pdf_path}")

        return report_data

    # ------------------------------------------------------------------
    # Markdown builder
    # ------------------------------------------------------------------
    def _build_markdown(
        self, company, year, rev, net_inc, op_inc, assets, equity,
        total_debt, cash, ebitda, fcf, gross_profit, cogs, eps,
        net_margin, op_margin, gross_margin, debt_to_equity, roa, roe,
        current_ratio, overall_risk, total_flags, high_flags, med_flags,
        low_flags, risk_score, flags, comparison, research_insights,
    ) -> List[str]:
        md = [
            f"# 📑 Financial Analysis Report: {company} ({year})",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  **Overall Risk Level:** `{overall_risk}` ({risk_score}/100)\n",
            "---\n",

            "## 1. Executive Summary",
            f"{company} reported total revenue/sales of **{rev}** for fiscal year {year}.",
            f"Operating income reached **{op_inc}**, reflecting an operating margin of **{op_margin}**.",
            f"The company closed the year with a net income of **{net_inc}** (net profit margin: **{net_margin}**).",
            f"Total assets stood at **{assets}** and shareholders' equity at **{equity}**.",
            f"The automated risk scanner assigned an overall risk level of **{overall_risk}** based on {total_flags} detected flag(s).\n",

            "## 2. Key Financial Highlights & Ratios",
            "| Metric | Reported Value | Assessment |",
            "| --- | --- | --- |",
            f"| Total Revenue | {rev} | Core top-line performance |",
            f"| Gross Profit | {gross_profit} | Revenue minus COGS |",
            f"| Operating Income (EBIT) | {op_inc} | Primary operating profitability |",
            f"| Net Income | {net_inc} | Bottom-line earnings |",
            f"| EBITDA | {ebitda} | Earnings before interest, taxes, depreciation |",
            f"| Free Cash Flow | {fcf} | Operating cash flow minus CapEx |",
            f"| Total Assets | {assets} | Total balance sheet scale |",
            f"| Shareholders' Equity | {equity} | Net asset backing |",
            f"| Total Debt | {total_debt} | Outstanding debt obligations |",
            f"| Cash & Equivalents | {cash} | Liquid reserves |",
            f"| Diluted EPS | {eps} | Earnings per share |\n",
            "### Ratio Analysis",
            "| Ratio | Value | Benchmark |",
            "| --- | --- | --- |",
            f"| Gross Margin | {gross_margin} | Pricing power & cost efficiency |",
            f"| Operating Margin | {op_margin} | Operational leverage |",
            f"| Net Profit Margin | {net_margin} | Profitability conversion |",
            f"| Debt-to-Equity | {debt_to_equity} | Capital structure leverage |",
            f"| Return on Assets (ROA) | {roa} | Asset utilization efficiency |",
            f"| Return on Equity (ROE) | {roe} | Shareholder value creation |",
            f"| Current Ratio | {current_ratio} | Short-term liquidity |\n",

            "## 3. Red Flag & Audit Risk Assessment",
            f"The automated audit scanner detected **{total_flags} flag(s)** — "
            f"HIGH: {high_flags}, MEDIUM: {med_flags}, LOW: {low_flags}.",
            f"Overall Risk Score: **{risk_score}/100** (Level: **{overall_risk}**).\n",
        ]

        if flags:
            md.append("### Key Detected Disclosures & Anomalies:")
            for i, f in enumerate(flags[:8], 1):
                prov = f.get("provenance", {})
                pg = prov.get("page_number", "N/A")
                doc = prov.get("document", "N/A")
                md.append(f"{i}. **[{f['severity'].upper()}] {f['title']}** ({f['category']})")
                md.append(f"   - *Finding:* {f['description']}")
                md.append(f"   - *Evidence:* \"{f.get('evidence', 'N/A')[:200]}\"")
                md.append(f"   - *Citation:* `{doc}`, Page {pg}\n")
        else:
            md.append("No critical red flags or auditor exceptions detected.\n")

        # Comparison section
        md.append("## 4. Company Comparison & Benchmarking")
        if comparison and comparison.get("markdown_table"):
            md.append(comparison["markdown_table"])
            if comparison.get("insights"):
                md.append("\n### Benchmarking Insights:")
                for ins in comparison["insights"]:
                    md.append(f"- {ins}")
            md.append("")
        else:
            md.append("_No comparison data available for this report. Use the Compare command to add peer benchmarks._\n")

        # Outlook & Recommendation
        md.append("## 5. Strategic Outlook & Recommendation")
        if overall_risk == "HIGH":
            md.append(f"⚠️ **Caution Advised:** {company} displays multiple high-severity risk signals or regulatory disclosures requiring thorough review before credit or capital allocation.")
            md.append("Elevated risk factors suggest a defensive positioning strategy with active monitoring of material developments.")
        elif overall_risk == "MEDIUM":
            md.append(f"⚖️ **Neutral / Selective:** Moderate risk factors identified for {company}.")
            md.append("Capital structure leverage and ongoing litigations should be monitored closely. Selective exposure recommended.")
        else:
            md.append(f"✅ **Favorable Profile:** Financial metrics indicate healthy operational margins and absence of severe audit qualifications for {company}.")
            md.append("The company demonstrates solid fundamentals suitable for constructive investment positioning.")

        if research_insights:
            md.append("\n### Research Agent Insights:")
            for insight in research_insights:
                md.append(f"- {insight}")

        md.append(f"\n---\n*Report compiled by Finora AI Multi-Agent System — {datetime.now().strftime('%B %d, %Y')}*")

        return md

    # ------------------------------------------------------------------
    # PDF Generation using PyMuPDF (fitz)
    # ------------------------------------------------------------------
    def _generate_pdf(
        self, pdf_path, company, year,
        rev, net_inc, op_inc, assets, equity, total_debt, cash,
        ebitda, fcf, gross_profit, cogs, eps,
        net_margin, op_margin, gross_margin, debt_to_equity,
        roa, roe, current_ratio,
        overall_risk, total_flags, high_flags, med_flags, low_flags,
        risk_score, flags, comparison, research_insights,
    ):
        """Build a professional PDF report using PyMuPDF drawing primitives."""
        doc = fitz.open()
        y = 0  # current y position on page

        def new_page():
            nonlocal y
            page = doc.new_page(width=PAGE_W, height=PAGE_H)
            y = MARGIN
            return page

        def check_space(page, needed):
            nonlocal y
            if y + needed > PAGE_H - MARGIN:
                page = new_page()
            return page

        def rgb(color_tuple):
            return tuple(c / 255 for c in color_tuple)

        def draw_rect(page, x, yp, w, h, color, fill=True):
            r = fitz.Rect(x, yp, x + w, yp + h)
            shape = page.new_shape()
            shape.draw_rect(r)
            if fill:
                shape.finish(color=rgb(color), fill=rgb(color))
            else:
                shape.finish(color=rgb(color), width=0.5)
            shape.commit()

        def write_text(page, x, yp, text, fontsize=10, color=COLORS["navy"], fontname="helv", max_width=None):
            nonlocal y
            if max_width and len(text) * fontsize * 0.5 > max_width:
                # Truncate
                max_chars = int(max_width / (fontsize * 0.45))
                text = text[:max_chars] + "..."
            tp = fitz.Point(x, yp)
            page.insert_text(tp, text, fontsize=fontsize, color=rgb(color), fontname=fontname)
            return yp + fontsize + 4

        # ====== PAGE 1: Cover + Executive Summary ======
        page = new_page()

        # Header bar
        draw_rect(page, 0, 0, PAGE_W, 90, COLORS["navy"])
        write_text(page, MARGIN, 35, "FINRESEARCH AI", fontsize=20, color=COLORS["white"], fontname="hebo")
        write_text(page, MARGIN, 58, "Multi-Agent Financial Intelligence Report", fontsize=10, color=COLORS["slate300"])
        write_text(page, PAGE_W - 200, 35, f"Generated: {datetime.now().strftime('%Y-%m-%d')}", fontsize=8, color=COLORS["slate300"])
        write_text(page, PAGE_W - 200, 50, f"Risk Level: {overall_risk}", fontsize=9, color=COLORS["gold"], fontname="hebo")
        y = 110

        # Company Title
        y = write_text(page, MARGIN, y, f"Financial Analysis Report", fontsize=16, color=COLORS["navy"], fontname="hebo")
        y = write_text(page, MARGIN, y, f"{company}  —  Fiscal Year {year}", fontsize=13, color=COLORS["blue"], fontname="hebo")
        y += 5

        # Separator
        draw_rect(page, MARGIN, y, CONTENT_W, 2, COLORS["blue"])
        y += 15

        # Section 1: Executive Summary
        y = write_text(page, MARGIN, y, "1. EXECUTIVE SUMMARY", fontsize=12, color=COLORS["navy"], fontname="hebo")
        y += 3

        summary_lines = [
            f"{company} reported total revenue of {rev} for fiscal year {year}.",
            f"Operating income reached {op_inc}, reflecting an operating margin of {op_margin}.",
            f"Net income was {net_inc} (net profit margin: {net_margin}).",
            f"Total assets stood at {assets}; shareholders' equity at {equity}.",
            f"Risk assessment: {total_flags} flag(s) detected — Risk Level: {overall_risk} ({risk_score}/100).",
        ]
        for line in summary_lines:
            page = check_space(page, 18)
            y = write_text(page, MARGIN + 10, y, line, fontsize=9, color=COLORS["slate700"])
            y += 2

        y += 10

        # Section 2: Key Financials Table
        page = check_space(page, 40)
        y = write_text(page, MARGIN, y, "2. KEY FINANCIAL HIGHLIGHTS & RATIOS", fontsize=12, color=COLORS["navy"], fontname="hebo")
        y += 5

        financials_rows = [
            ("Metric", "Value", "Assessment"),
            ("Total Revenue", rev, "Core top-line performance"),
            ("Gross Profit", gross_profit, "Revenue minus COGS"),
            ("Operating Income (EBIT)", op_inc, "Operating profitability"),
            ("Net Income", net_inc, "Bottom-line earnings"),
            ("EBITDA", ebitda, "Pre-depreciation earnings"),
            ("Free Cash Flow", fcf, "OCF minus CapEx"),
            ("Total Assets", assets, "Balance sheet scale"),
            ("Shareholders' Equity", equity, "Net asset backing"),
            ("Total Debt", total_debt, "Debt obligations"),
            ("Cash & Equivalents", cash, "Liquid reserves"),
            ("Diluted EPS", eps, "Earnings per share"),
        ]

        col_widths = [180, 140, 175]
        for i, (c1, c2, c3) in enumerate(financials_rows):
            page = check_space(page, 18)
            bg = COLORS["blue_bg"] if i == 0 else (COLORS["white"] if i % 2 == 0 else (248, 250, 252))
            fc = COLORS["navy"] if i == 0 else COLORS["slate700"]
            fn = "hebo" if i == 0 else "helv"

            draw_rect(page, MARGIN, y - 3, CONTENT_W, 16, bg)
            write_text(page, MARGIN + 5, y + 8, c1, fontsize=8, color=fc, fontname=fn)
            write_text(page, MARGIN + col_widths[0], y + 8, c2, fontsize=8, color=fc, fontname=fn)
            write_text(page, MARGIN + col_widths[0] + col_widths[1], y + 8, c3, fontsize=8, color=fc, fontname=fn)
            y += 16

        y += 8

        # Ratio sub-table
        page = check_space(page, 25)
        y = write_text(page, MARGIN, y, "Ratio Analysis", fontsize=10, color=COLORS["indigo"], fontname="hebo")
        y += 3

        ratio_rows = [
            ("Ratio", "Value", "Benchmark"),
            ("Gross Margin", gross_margin, "Pricing power & cost efficiency"),
            ("Operating Margin", op_margin, "Operational leverage"),
            ("Net Profit Margin", net_margin, "Profitability conversion"),
            ("Debt-to-Equity", debt_to_equity, "Capital structure leverage"),
            ("Return on Assets (ROA)", roa, "Asset utilization efficiency"),
            ("Return on Equity (ROE)", roe, "Shareholder value creation"),
            ("Current Ratio", current_ratio, "Short-term liquidity"),
        ]

        for i, (c1, c2, c3) in enumerate(ratio_rows):
            page = check_space(page, 18)
            bg = COLORS["emerald_bg"] if i == 0 else (COLORS["white"] if i % 2 == 0 else (248, 250, 252))
            fc = COLORS["navy"] if i == 0 else COLORS["slate700"]
            fn = "hebo" if i == 0 else "helv"

            draw_rect(page, MARGIN, y - 3, CONTENT_W, 16, bg)
            write_text(page, MARGIN + 5, y + 8, c1, fontsize=8, color=fc, fontname=fn)
            write_text(page, MARGIN + col_widths[0], y + 8, c2, fontsize=8, color=fc, fontname=fn)
            write_text(page, MARGIN + col_widths[0] + col_widths[1], y + 8, c3, fontsize=8, color=fc, fontname=fn)
            y += 16

        y += 15

        # Section 3: Red Flags
        page = check_space(page, 40)
        y = write_text(page, MARGIN, y, "3. RED FLAG & AUDIT RISK ASSESSMENT", fontsize=12, color=COLORS["navy"], fontname="hebo")
        y += 5

        # Risk summary bar
        page = check_space(page, 30)
        risk_color = COLORS["rose"] if overall_risk == "HIGH" else (COLORS["gold"] if overall_risk == "MEDIUM" else COLORS["emerald"])
        risk_bg = COLORS["rose_bg"] if overall_risk == "HIGH" else (COLORS["amber_bg"] if overall_risk == "MEDIUM" else COLORS["emerald_bg"])
        draw_rect(page, MARGIN, y - 3, CONTENT_W, 25, risk_bg)
        write_text(page, MARGIN + 10, y + 12, f"Overall Risk: {overall_risk}  |  Score: {risk_score}/100  |  Flags: {total_flags} (H:{high_flags} M:{med_flags} L:{low_flags})", fontsize=9, color=risk_color, fontname="hebo")
        y += 30

        # Individual flags
        for f in flags[:6]:
            page = check_space(page, 50)
            sev = f["severity"].upper()
            sev_color = COLORS["rose"] if sev == "HIGH" else (COLORS["gold"] if sev == "MEDIUM" else COLORS["emerald"])

            y = write_text(page, MARGIN + 10, y, f"[{sev}] {f['title']}", fontsize=9, color=sev_color, fontname="hebo")
            y = write_text(page, MARGIN + 20, y, f"Category: {f['category']}", fontsize=8, color=COLORS["slate500"])

            desc = f["description"][:180] + ("..." if len(f["description"]) > 180 else "")
            y = write_text(page, MARGIN + 20, y, desc, fontsize=8, color=COLORS["slate700"], max_width=CONTENT_W - 30)

            prov = f.get("provenance", {})
            cite = f"Source: {prov.get('document', 'N/A')}, Page {prov.get('page_number', 'N/A')}"
            y = write_text(page, MARGIN + 20, y, cite, fontsize=7, color=COLORS["slate500"])
            y += 6

        y += 10

        # Section 4: Comparison
        page = check_space(page, 35)
        y = write_text(page, MARGIN, y, "4. COMPANY COMPARISON & BENCHMARKING", fontsize=12, color=COLORS["navy"], fontname="hebo")
        y += 5

        if comparison and comparison.get("insights"):
            for ins in comparison["insights"][:5]:
                page = check_space(page, 18)
                ins_text = ins[:120] + ("..." if len(ins) > 120 else "")
                y = write_text(page, MARGIN + 10, y, f"• {ins_text}", fontsize=8, color=COLORS["slate700"])
                y += 2
        else:
            y = write_text(page, MARGIN + 10, y, "No peer comparison data included in this report.", fontsize=9, color=COLORS["slate500"])
        y += 15

        # Section 5: Outlook
        page = check_space(page, 60)
        y = write_text(page, MARGIN, y, "5. STRATEGIC OUTLOOK & RECOMMENDATION", fontsize=12, color=COLORS["navy"], fontname="hebo")
        y += 5

        if overall_risk == "HIGH":
            rec_text = f"CAUTION ADVISED: {company} displays multiple high-severity risk signals. Thorough review recommended before capital allocation."
            rec_color = COLORS["rose"]
        elif overall_risk == "MEDIUM":
            rec_text = f"NEUTRAL / SELECTIVE: Moderate risk factors identified for {company}. Monitor capital structure and ongoing litigations."
            rec_color = COLORS["gold"]
        else:
            rec_text = f"FAVORABLE PROFILE: {company} demonstrates healthy margins and absence of severe audit qualifications."
            rec_color = COLORS["emerald"]

        draw_rect(page, MARGIN, y - 3, CONTENT_W, 30, risk_bg)
        write_text(page, MARGIN + 10, y + 12, rec_text, fontsize=9, color=rec_color, fontname="hebo", max_width=CONTENT_W - 20)
        y += 40

        if research_insights:
            page = check_space(page, 25)
            y = write_text(page, MARGIN, y, "Research Agent Insights:", fontsize=10, color=COLORS["indigo"], fontname="hebo")
            for ri in research_insights[:4]:
                page = check_space(page, 18)
                ri_text = ri[:150] + ("..." if len(ri) > 150 else "")
                y = write_text(page, MARGIN + 10, y, f"• {ri_text}", fontsize=8, color=COLORS["slate700"])

        # Footer on each page
        for pi in range(len(doc)):
            pg = doc[pi]
            draw_rect(pg, 0, PAGE_H - 30, PAGE_W, 30, COLORS["navy"])
            pg.insert_text(
                fitz.Point(MARGIN, PAGE_H - 12),
                f"Finora AI  |  {company} ({year})  |  Page {pi + 1} of {len(doc)}  |  Confidential",
                fontsize=7, color=rgb(COLORS["slate300"]), fontname="helv"
            )

        doc.save(pdf_path)
        doc.close()
        print(f"[ReportAgent] PDF saved: {pdf_path}")

    # ------------------------------------------------------------------
    # Utility: get_pdf_path for download API
    # ------------------------------------------------------------------
    def get_report_path(self, company: str, year: str, fmt: str = "pdf") -> Optional[str]:
        """Return the path to a generated report file if it exists."""
        doc_id = f"{company.upper().strip()}_{str(year).strip()}"
        ext_map = {"pdf": ".pdf", "json": ".json", "md": ".md"}
        ext = ext_map.get(fmt, ".pdf")
        path = os.path.join(self.output_dir, f"{doc_id}_report{ext}")
        return path if os.path.exists(path) else None
