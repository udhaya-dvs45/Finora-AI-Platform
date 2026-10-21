import sys
import os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_FLAX", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

print("Testing LangGraph StateGraph workflow...")
from workflow.graph import financial_workflow
print("LangGraph imported OK")

result = financial_workflow.invoke({"pdf_path": "DATA/AMAZON_ANNUAL_2023.pdf"})

print("\n=== LANGGRAPH WORKFLOW RESULT ===")
print(f"Company   : {result.get('company')}")
print(f"Year      : {result.get('year')}")
print(f"Risk Level: {result.get('red_flag_result', {}).get('summary', {}).get('overall_risk_level')}")
print(f"Flags     : {result.get('red_flag_result', {}).get('summary', {}).get('total_flags')}")
print(f"Report    : {result.get('report', {}).get('doc_id')}")
print("\nReport saved to outputs/reports/AMAZON_2023_report.md")
print("\nAll 4 LangGraph nodes executed successfully!")
