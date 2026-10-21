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
graph.py
--------
LangGraph Multi-Agent Orchestration Layer for the Financial Multi-Agent System.

Matches the reference repository architecture:
  StateGraph(FinancialState)
    -> document_agent
    -> extraction_agent
    -> red_flag_agent
    -> report_agent
    -> END
"""

from typing import Dict, Any, TypedDict, Optional
from langgraph.graph import StateGraph, END

# Path setup
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from agents.document_agent import DocumentAgent
from agents.extraction_agent import ExtractionAgent
from agents.red_flag_agent import RedFlagAgent
from agents.report_agent import ReportAgent


# -----------------------------------------------------------------------------
# Workflow State (TypedDict)
# -----------------------------------------------------------------------------

class FinancialState(TypedDict, total=False):
    pdf_path: str
    company: str
    year: str
    document_result: Dict[str, Any]
    extracted_metrics: Dict[str, Any]
    red_flag_result: Dict[str, Any]
    report: Dict[str, Any]


# -----------------------------------------------------------------------------
# Initialize Agents
# -----------------------------------------------------------------------------

document_agent = DocumentAgent(ROOT_DIR)
extraction_agent = ExtractionAgent(ROOT_DIR)
red_flag_agent = RedFlagAgent(ROOT_DIR)
report_agent = ReportAgent(ROOT_DIR)


# -----------------------------------------------------------------------------
# Graph Nodes
# -----------------------------------------------------------------------------

def document_node(state: FinancialState) -> Dict[str, Any]:
    """Node 1: Parse, chunk, embed, and index PDF in ChromaDB."""
    pdf_path = state.get("pdf_path", "")
    print(f"\n[LangGraph] ===> Node: document_agent (PDF: {os.path.basename(pdf_path)})")
    
    result = document_agent.process_document(pdf_path)
    company = result.get("company", "")
    year = str(result.get("year", ""))
    
    return {
        "document_result": result,
        "company": company,
        "year": year,
    }


def extraction_node(state: FinancialState) -> Dict[str, Any]:
    """Node 2: Query ChromaDB & extract financial metrics & calculate ratios."""
    company = state.get("company", "")
    year = state.get("year", "")
    print(f"\n[LangGraph] ===> Node: extraction_agent ({company} {year})")
    
    result = extraction_agent.extract(company=company, year=year, force_reextract=True)
    return {
        "extracted_metrics": result,
    }


def red_flag_node(state: FinancialState) -> Dict[str, Any]:
    """Node 3: Scan for quantitative financial anomalies & qualitative audit risks."""
    company = state.get("company", "")
    year = state.get("year", "")
    print(f"\n[LangGraph] ===> Node: red_flag_agent ({company} {year})")
    
    result = red_flag_agent.scan(company=company, year=year, force_rescan=True)
    return {
        "red_flag_result": result,
    }


def report_node(state: FinancialState) -> Dict[str, Any]:
    """Node 4: Synthesize full executive report and recommendations."""
    company = state.get("company", "")
    year = state.get("year", "")
    print(f"\n[LangGraph] ===> Node: report_agent ({company} {year})")
    
    metrics = state.get("extracted_metrics", {})
    red_flags = state.get("red_flag_result", {})
    
    rep = report_agent.generate(
        company=company,
        year=year,
        extracted_metrics=metrics,
        red_flag_result=red_flags,
        force_regenerate=True,
    )
    return {
        "report": rep,
    }


# -----------------------------------------------------------------------------
# LangGraph Workflow Construction
# -----------------------------------------------------------------------------

graph = StateGraph(FinancialState)

# Add Nodes
graph.add_node("document_agent", document_node)
graph.add_node("extraction_agent", extraction_node)
graph.add_node("red_flag_agent", red_flag_node)
graph.add_node("report_agent", report_node)

# Set Entry Point
graph.set_entry_point("document_agent")

# Connect Sequential Edges
graph.add_edge("document_agent", "extraction_agent")
graph.add_edge("extraction_agent", "red_flag_agent")
graph.add_edge("red_flag_agent", "report_agent")
graph.add_edge("report_agent", END)

# Compile Workflow
financial_workflow = graph.compile()
