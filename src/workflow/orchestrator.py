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
orchestrator.py
---------------
Multi-Agent Orchestration Layer for the Financial Multi-Agent System (Milestone 3).

Coordinates the agents sequentially on document upload or batch execution:
  Stage 1: DocumentAgent   -> Ingestion, chunking, embedding, vector DB indexing
  Stage 2: ExtractionAgent -> Financial metrics extraction, ratio calculation, provenance
  Stage 3: RedFlagAgent    -> Quantitative anomaly & qualitative risk scan, severity scoring

Provides:
- `OrchestrationPipeline.run_pipeline(pdf_path, session_id=None)`
- `OrchestrationPipeline.run_for_doc_id(company, year, session_id=None)`
- `OrchestrationPipeline.run_batch(pdf_paths, session_id=None)`
"""

import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from workspace.session_manager import SessionManager
from agents.document_agent import DocumentAgent
from agents.extraction_agent import ExtractionAgent
from agents.red_flag_agent import RedFlagAgent
from agents.report_agent import ReportAgent


class OrchestrationPipeline:
    """
    Sequential Orchestration Pipeline for Document, Extraction, Red Flag, and Report Agents.
    """

    def __init__(self, root_dir: str = ROOT_DIR, session_manager: Optional[SessionManager] = None):
        self.root_dir = os.path.abspath(root_dir)
        self.sessions_dir = os.path.join(self.root_dir, "sessions")
        self.session_manager = session_manager or SessionManager(self.sessions_dir)

        # Initialize agents (lazy models inside each agent)
        self.document_agent = DocumentAgent(self.root_dir, session_manager=self.session_manager)
        self.extraction_agent = ExtractionAgent(self.root_dir)
        self.red_flag_agent = RedFlagAgent(self.root_dir)
        self.report_agent = ReportAgent(self.root_dir)

    def run_pipeline(
        self,
        pdf_path: str,
        session_id: Optional[str] = None,
        force_reindex: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute full multi-agent pipeline for a single PDF.

        Parameters
        ----------
        pdf_path      : Path to the PDF file (e.g., 'DATA/AMAZON_ANNUAL_2023.pdf')
        session_id    : Optional session ID to attach results to
        force_reindex : Whether to force document re-extraction & re-embedding

        Returns
        -------
        Dict with comprehensive execution state, timings, and outputs from all agents.
        """
        start_time = time.time()
        filename = os.path.basename(pdf_path)
        print("=" * 70)
        print(f"[Orchestrator] Starting Multi-Agent Pipeline for: {filename}")
        print("=" * 70)

        pipeline_result: Dict[str, Any] = {
            "pipeline_status": "in_progress",
            "pdf_path": pdf_path,
            "filename": filename,
            "session_id": session_id,
            "started_at": datetime.now().isoformat(),
            "stages": {},
        }

        # -------------------------------------------------------------
        # STAGE 1: Document Agent (Ingest, Chunk, Embed, ChromaDB)
        # -------------------------------------------------------------
        print("\n--> [Stage 1/3] Executing Document Agent...")
        t0 = time.time()
        try:
            doc_result = self.document_agent.process_document(
                pdf_path=pdf_path,
                session_id=session_id,
                force_reprocess=force_reindex,
            )
            is_ok = doc_result.get("status") in ("indexed", "already_indexed", "already_processed", "success")
            stage1_status = "success" if is_ok else "failed"
            company = doc_result.get("company", "")
            year = str(doc_result.get("year", ""))
            doc_id = doc_result.get("doc_id", f"{company}_{year}")

            pipeline_result["stages"]["document_agent"] = {
                "status": stage1_status,
                "duration_seconds": round(time.time() - t0, 2),
                "doc_id": doc_id,
                "company": company,
                "year": year,
                "total_chunks": doc_result.get("total_chunks", 0),
                "page_count": doc_result.get("total_pages", doc_result.get("page_count", 0)),
            }
            if not is_ok:
                pipeline_result["pipeline_status"] = "failed"
                pipeline_result["error_stage"] = "document_agent"
                return pipeline_result

            print(f"--> [Stage 1/3] Document Agent Complete: {doc_id} ({doc_result.get('total_chunks', 0)} chunks)")

        except Exception as e:
            pipeline_result["stages"]["document_agent"] = {
                "status": "error",
                "error": str(e),
                "duration_seconds": round(time.time() - t0, 2),
            }
            pipeline_result["pipeline_status"] = "failed"
            pipeline_result["error_stage"] = "document_agent"
            return pipeline_result

        # -------------------------------------------------------------
        # STAGE 2: Extraction Agent (Query ChromaDB, Extract Ratios)
        # -------------------------------------------------------------
        print(f"\n--> [Stage 2/3] Executing Extraction Agent for {company} {year}...")
        t0 = time.time()
        try:
            extraction_result = self.extraction_agent.extract(company=company, year=year)
            metrics_found = sum(
                1 for m in extraction_result.get("metrics", {}).values()
                if isinstance(m, dict) and m.get("confidence") in ("high", "medium", "low")
            )
            ratios_count = len(extraction_result.get("calculated_ratios", {}))

            pipeline_result["stages"]["extraction_agent"] = {
                "status": "success",
                "duration_seconds": round(time.time() - t0, 2),
                "metrics_extracted_count": metrics_found,
                "ratios_calculated_count": ratios_count,
                "metrics_output_file": f"outputs/financial_metrics/{doc_id}_metrics.json",
                "summary_metrics": {
                    k: v.get("value") for k, v in extraction_result.get("metrics", {}).items()
                    if isinstance(v, dict) and v.get("value") is not None
                },
                "calculated_ratios": extraction_result.get("calculated_ratios", {}),
            }
            print(f"--> [Stage 2/3] Extraction Agent Complete: {metrics_found} metrics, {ratios_count} ratios")

        except Exception as e:
            pipeline_result["stages"]["extraction_agent"] = {
                "status": "error",
                "error": str(e),
                "duration_seconds": round(time.time() - t0, 2),
            }
            print(f"--> [Stage 2/3] Extraction Agent Warning/Error: {e}")

        # -------------------------------------------------------------
        # STAGE 3: Red Flag Agent (Scan Anomaly & Risk Patterns)
        # -------------------------------------------------------------
        print(f"\n--> [Stage 3/4] Executing Red Flag Agent for {company} {year}...")
        t0 = time.time()
        red_flag_result = {}
        try:
            red_flag_result = self.red_flag_agent.scan(company=company, year=year)
            summary = red_flag_result.get("summary", {})

            pipeline_result["stages"]["red_flag_agent"] = {
                "status": "success",
                "duration_seconds": round(time.time() - t0, 2),
                "overall_risk_level": summary.get("overall_risk_level", "UNKNOWN"),
                "risk_score": summary.get("risk_score_out_of_100", 0),
                "total_flags": summary.get("total_flags", 0),
                "high_severity_count": summary.get("high_severity_count", 0),
                "medium_severity_count": summary.get("medium_severity_count", 0),
                "low_severity_count": summary.get("low_severity_count", 0),
                "red_flags_output_file": f"outputs/red_flags/{doc_id}_red_flags.json",
                "top_flags": [
                    {
                        "title": f["title"],
                        "severity": f["severity"],
                        "category": f["category"],
                        "page": f.get("provenance", {}).get("page_number", "N/A"),
                    }
                    for f in red_flag_result.get("red_flags", [])[:5]
                ]
            }
            print(f"--> [Stage 3/4] Red Flag Agent Complete: {summary.get('total_flags', 0)} flags (Risk: {summary.get('overall_risk_level')})")

        except Exception as e:
            pipeline_result["stages"]["red_flag_agent"] = {
                "status": "error",
                "error": str(e),
                "duration_seconds": round(time.time() - t0, 2),
            }
            print(f"--> [Stage 3/4] Red Flag Agent Warning/Error: {e}")

        # -------------------------------------------------------------
        # STAGE 4: Report Agent (Compile into JSON, Markdown & PDF)
        # -------------------------------------------------------------
        print(f"\n--> [Stage 4/4] Executing Report Agent for {company} {year}...")
        t0 = time.time()
        try:
            report_result = self.report_agent.generate(
                company=company,
                year=year,
                extracted_metrics=extraction_result if "extraction_result" in locals() and isinstance(extraction_result, dict) else {},
                red_flag_result=red_flag_result if isinstance(red_flag_result, dict) else {},
                force_regenerate=True,
            )
            pipeline_result["stages"]["report_agent"] = {
                "status": "success",
                "duration_seconds": round(time.time() - t0, 2),
                "pdf_path": report_result.get("pdf_path"),
                "json_path": report_result.get("json_path"),
                "markdown_path": report_result.get("markdown_path"),
                "recommendation": report_result.get("recommendation"),
                "overall_risk_level": report_result.get("overall_risk_level"),
            }
            pipeline_result["report_pdf"] = report_result.get("pdf_path")
            pipeline_result["report_json"] = report_result.get("json_path")
            pipeline_result["report_markdown"] = report_result.get("markdown_path")
            print(f"--> [Stage 4/4] Report Agent Complete: PDF compiled at {report_result.get('pdf_path')}")

        except Exception as e:
            pipeline_result["stages"]["report_agent"] = {
                "status": "error",
                "error": str(e),
                "duration_seconds": round(time.time() - t0, 2),
            }
            print(f"--> [Stage 4/4] Report Agent Warning/Error: {e}")

        # -------------------------------------------------------------
        # Finish Pipeline
        # -------------------------------------------------------------
        total_duration = round(time.time() - start_time, 2)
        pipeline_result["pipeline_status"] = "completed"
        pipeline_result["total_duration_seconds"] = total_duration
        pipeline_result["completed_at"] = datetime.now().isoformat()

        print("\n" + "=" * 70)
        print(f"[Orchestrator] Multi-Agent Pipeline Completed in {total_duration}s for {doc_id}")
        print("=" * 70 + "\n")

        return pipeline_result

    def run_for_doc_id(self, company: str, year: str) -> Dict[str, Any]:
        """
        Run Extraction + Red Flag + Report stages for an already indexed document.
        """
        company_clean = company.upper().strip()
        year_clean = str(year).strip()
        doc_id = f"{company_clean}_{year_clean}"
        print(f"[Orchestrator] Running downstream agents for indexed doc: {doc_id}")

        ext_result = self.extraction_agent.extract(company=company_clean, year=year_clean)
        rf_result = self.red_flag_agent.scan(company=company_clean, year=year_clean)
        rep_result = self.report_agent.generate(
            company=company_clean,
            year=year_clean,
            extracted_metrics=ext_result,
            red_flag_result=rf_result,
            force_regenerate=True,
        )

        return {
            "doc_id": doc_id,
            "extraction": ext_result,
            "red_flags": rf_result,
            "report": rep_result,
        }

    def run_batch(self, pdf_paths: List[str], session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Run orchestration pipeline over a list of PDF documents.
        """
        results = []
        for pdf_path in pdf_paths:
            res = self.run_pipeline(pdf_path, session_id=session_id)
            results.append(res)
        return results
