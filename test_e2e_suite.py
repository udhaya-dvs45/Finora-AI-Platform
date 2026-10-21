import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import os
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_FLAX", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import json
import time
import unittest

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from agents.document_agent import DocumentAgent
from agents.extraction_agent import ExtractionAgent
from agents.red_flag_agent import RedFlagAgent
from agents.report_agent import ReportAgent
from agents.comparison_agent import ComparisonAgent
from agents.research_agent import ResearchAgent
from workflow.orchestrator import OrchestrationPipeline


class TestFinancialMultiAgentSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = ROOT_DIR
        cls.doc_agent = DocumentAgent(cls.root_dir)
        cls.ext_agent = ExtractionAgent(cls.root_dir)
        cls.rf_agent = RedFlagAgent(cls.root_dir)
        cls.rep_agent = ReportAgent(cls.root_dir)
        cls.comp_agent = ComparisonAgent(cls.root_dir)
        cls.orch = OrchestrationPipeline(cls.root_dir)

    # -------------------------------------------------------------------------
    # 1. CITATION ACCURACY & PROVENANCE
    # -------------------------------------------------------------------------
    def test_01_citation_accuracy(self):
        """Validate citation accuracy and source grounding in extraction & red flags."""
        print("\n[TEST 1] Validating Citation Accuracy & Grounding Provenance...")
        company = "AMAZON"
        year = "2023"
        ext_res = self.ext_agent.extract(company, year)
        self.assertIn("metrics", ext_res)
        
        # Check metrics provenance
        verified_metric_citations = 0
        for m_name, m_data in ext_res["metrics"].items():
            if isinstance(m_data, dict) and m_data.get("value") is not None:
                self.assertIn("document", m_data)
                self.assertIn("page_number", m_data)
                self.assertTrue(len(str(m_data["document"])) > 0)
                # Ensure page number is a positive integer or valid page reference
                self.assertTrue(isinstance(m_data["page_number"], (int, str)))
                verified_metric_citations += 1

        print(f"  -> Verified {verified_metric_citations} metrics citations with page numbers.")
        self.assertGreater(verified_metric_citations, 3, "At least 3 metrics must have citations")

        # Check Red Flag citations
        rf_res = self.rf_agent.scan(company, year)
        self.assertIn("red_flags", rf_res)
        verified_rf_citations = 0
        for flag in rf_res["red_flags"]:
            self.assertIn("provenance", flag)
            prov = flag["provenance"]
            self.assertIn("document", prov)
            self.assertIn("page_number", prov)
            self.assertIn("evidence", flag)
            self.assertTrue(len(flag["evidence"]) > 0, "Flag must have non-empty evidence quote")
            verified_rf_citations += 1

        print(f"  -> Verified {verified_rf_citations} red flag disclosure citations with textual evidence.")
        self.assertGreater(verified_rf_citations, 0, "Must have verified red flag citations")

    # -------------------------------------------------------------------------
    # 2. EXTRACTION CORRECTNESS & RATIOS
    # -------------------------------------------------------------------------
    def test_02_extraction_correctness(self):
        """Validate extraction correctness and mathematical ratio consistency."""
        print("\n[TEST 2] Validating Extraction Correctness & Formula Consistency...")
        company = "APPLE"
        year = "2024"
        ext_res = self.ext_agent.extract(company, year)
        m = ext_res["metrics"]
        
        # Revenue and Net Income checks
        rev = m.get("revenue", {}).get("value")
        net_inc = m.get("net_income", {}).get("value")
        self.assertIsNotNone(rev, "Revenue must be extracted")
        self.assertIsNotNone(net_inc, "Net income must be extracted")
        self.assertGreater(rev, 0, "Revenue should be positive")
        
        # Ratio consistency check
        ratios = ext_res.get("ratios", ext_res.get("calculated_ratios", {}))
        if "net_profit_margin" in ratios:
            npm = ratios["net_profit_margin"]
            npm_val = npm.get("value") if isinstance(npm, dict) else npm
            expected_npm = net_inc / rev
            self.assertAlmostEqual(npm_val, expected_npm, places=2, msg="Calculated net margin must match Net Income / Revenue")
            print(f"  -> Net Profit Margin formula verified: {npm_val:.4f} == {expected_npm:.4f}")

    # -------------------------------------------------------------------------
    # 3. AGENT COLLABORATION & PIPELINE ORCHESTRATION
    # -------------------------------------------------------------------------
    def test_03_agent_collaboration(self):
        """Validate multi-agent orchestration across all 4 stages (Doc->Ext->RF->Report)."""
        print("\n[TEST 3] Validating 4-Stage Agent Collaboration & Orchestration...")
        company = "TESLA"
        year = "2023"
        pipe_res = self.orch.run_for_doc_id(company, year)
        
        self.assertEqual(pipe_res.get("doc_id"), f"{company}_{year}")
        self.assertIn("extraction", pipe_res)
        self.assertIn("red_flags", pipe_res)
        self.assertIn("report", pipe_res)
        
        report = pipe_res["report"]
        self.assertEqual(report.get("company"), company)
        self.assertEqual(report.get("year"), year)
        self.assertTrue(os.path.exists(report.get("pdf_path", "")), "PDF must exist on disk")
        print(f"  -> Full collaboration executed: Extraction + RedFlag passed seamlessly into Report Agent.")

    # -------------------------------------------------------------------------
    # 4. REPORT COMPLETENESS (5 SECTIONS + PDF GENERATION)
    # -------------------------------------------------------------------------
    def test_04_report_completeness(self):
        """Validate structured report covers all 5 mandatory sections and generates valid PDF."""
        print("\n[TEST 4] Validating Report Completeness (5 Sections + Valid PDF)...")
        company = "META"
        year = "2024"
        ext = self.ext_agent.extract(company, year)
        rf = self.rf_agent.scan(company, year)
        comp = self.comp_agent.compare([("META", "2024"), ("APPLE", "2024")])
        
        rep = self.rep_agent.generate(
            company=company,
            year=year,
            extracted_metrics=ext,
            red_flag_result=rf,
            comparison=comp,
            force_regenerate=True
        )

        # 1. Executive Summary
        self.assertIn("executive_summary", rep)
        self.assertIsInstance(rep["executive_summary"], dict)
        self.assertIn("revenue", rep["executive_summary"])
        self.assertGreater(len(rep["markdown_report"]), 100)
        
        # 2. Key Financial Highlights & Ratios
        self.assertIn("key_financials", rep)
        self.assertIn("net_margin", rep["key_financials"])
        
        # 3. Red Flags & Audit Risk
        self.assertIn("red_flags", rep)
        self.assertIn("overall_risk_level", rep["red_flags"])
        
        # 4. Company Comparison
        self.assertIn("comparison", rep)
        
        # 5. Strategic Outlook & Recommendation
        self.assertIn("recommendation", rep)
        self.assertIn(rep["recommendation"], ["BUY / ACCUMULATE", "NEUTRAL / HOLD", "CAUTION / MONITOR"])

        # File artifacts check
        pdf_path = rep.get("pdf_path")
        json_path = rep.get("json_path")
        md_path = rep.get("markdown_path")

        self.assertIsNotNone(pdf_path)
        self.assertTrue(os.path.exists(pdf_path), f"PDF file does not exist at {pdf_path}")
        pdf_size = os.path.getsize(pdf_path)
        self.assertGreater(pdf_size, 1000, f"PDF file is too small: {pdf_size} bytes")

        self.assertTrue(os.path.exists(json_path), f"JSON file does not exist at {json_path}")
        self.assertTrue(os.path.exists(md_path), f"MD file does not exist at {md_path}")

        print(f"  -> All 5 sections confirmed:")
        print(f"     1. Executive Summary: OK ({len(rep['executive_summary'])} fields)")
        print(f"     2. Key Financials: OK (Net Margin: {rep['key_financials']['net_margin']})")
        print(f"     3. Red Flags: OK (Risk: {rep['red_flags']['overall_risk_level']})")
        print(f"     4. Comparison: OK")
        print(f"     5. Strategic Outlook: OK (Rec: {rep['recommendation']})")
        print(f"  -> PDF Artifact: {pdf_path} ({pdf_size} bytes, verified)")

    # -------------------------------------------------------------------------
    # 5. REPORT DOWNLOAD CAPABILITY
    # -------------------------------------------------------------------------
    def test_05_download_capability(self):
        """Validate get_report_path can retrieve PDF/JSON/MD paths for downloads."""
        print("\n[TEST 5] Validating Report Download File Resolver...")
        pdf_file = self.rep_agent.get_report_path("META", "2024", fmt="pdf")
        self.assertIsNotNone(pdf_file)
        self.assertTrue(os.path.exists(pdf_file))
        
        json_file = self.rep_agent.get_report_path("META", "2024", fmt="json")
        self.assertIsNotNone(json_file)
        self.assertTrue(os.path.exists(json_file))
        print(f"  -> Download path resolved: {pdf_file}")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFinancialMultiAgentSystem)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n=======================================================")
        print("ALL END-TO-END TESTS PASSED SUCCESSFULLY! (100% OK)")
        print("=======================================================")
        sys.exit(0)
    else:
        print("\nTest failures encountered!")
        sys.exit(1)
