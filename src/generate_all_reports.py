import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import os
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_FLAX", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import glob
import json
from agents.report_agent import ReportAgent
from agents.extraction_agent import ExtractionAgent
from agents.red_flag_agent import RedFlagAgent

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)

def main():
    print("[BatchReport] Initializing agents...")
    rep_agent = ReportAgent(ROOT_DIR)
    ext_agent = ExtractionAgent(ROOT_DIR)
    rf_agent = RedFlagAgent(ROOT_DIR)

    metrics_dir = os.path.join(ROOT_DIR, "outputs", "financial_metrics")
    files = glob.glob(os.path.join(metrics_dir, "*_metrics.json"))
    print(f"[BatchReport] Found {len(files)} metrics files to compile into PDF reports.")

    success_count = 0
    for f in files:
        base = os.path.basename(f).replace("_metrics.json", "")
        parts = base.split("_")
        if len(parts) >= 2:
            company = parts[0]
            year = parts[1]
        else:
            continue

        try:
            print(f"[BatchReport] Compiling PDF report for {company} {year}...")
            ext = ext_agent.extract(company, year)
            rf = rf_agent.scan(company, year)
            res = rep_agent.generate(company, year, ext, rf, force_regenerate=True)
            pdf_p = res.get("pdf_path")
            if pdf_p and os.path.exists(pdf_p):
                print(f"  --> SUCCESS: {pdf_p} ({os.path.getsize(pdf_p)} bytes)")
                success_count += 1
        except Exception as e:
            print(f"  --> ERROR compiling for {company} {year}: {e}")

    print(f"\n[BatchReport] Completed! Successfully compiled {success_count} PDF reports.")

if __name__ == "__main__":
    main()
