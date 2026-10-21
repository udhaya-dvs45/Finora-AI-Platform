import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
"""
app.py
------
CLI entrypoint for the Multi-Agent Financial Analysis System -- Milestone 3.

Usage
-----
  # Session management
  python src/app.py session create "My Research Session"
  python src/app.py session list
  python src/app.py session show <session_id>
  python src/app.py session delete <session_id>

  # Document Agent -- index PDFs into ChromaDB
  python src/app.py document list
  python src/app.py document process DATA/AMAZON_ANNUAL_2023.pdf
  python src/app.py document process DATA/AMAZON_ANNUAL_2023.pdf --session <session_id>
  python src/app.py document process-all
  python src/app.py document process-all --limit 4

  # Extraction Agent -- extract financial metrics
  python src/app.py extract AMAZON 2023
  python src/app.py extract-all

  # Red Flag Agent -- scan for anomalies and disclosure risks
  python src/app.py redflags scan AMAZON 2023
  python src/app.py redflags scan-all

  # Multi-Agent Pipeline -- run Document -> Extraction -> Red Flags end-to-end
  python src/app.py pipeline run DATA/AMAZON_ANNUAL_2023.pdf
  python src/app.py pipeline run-doc AMAZON 2023

  # Research Agent -- grounded RAG reasoning with source citations
  python src/app.py research "What are Amazon's primary revenue drivers and regulatory risks in 2023?"

  # Comparison Agent -- side-by-side benchmarking
  python src/app.py compare AMAZON:2023 TESLA:2023
  python src/app.py compare AMAZON:2023 APPLE:2024 INFOSYS:2023

  # Database stats
  python src/app.py stats
"""

import os
import sys
import argparse
from typing import Optional, List, Tuple

SRC_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from workspace.session_manager import SessionManager
from agents.document_agent import DocumentAgent
from agents.extraction_agent import ExtractionAgent
from agents.red_flag_agent import RedFlagAgent
from agents.research_agent import ResearchAgent
from agents.comparison_agent import ComparisonAgent
from agents.report_agent import ReportAgent
from workflow.orchestrator import OrchestrationPipeline


SESSIONS_DIR = os.path.join(ROOT_DIR, "sessions")


# -----------------------------------------------------------------------------
# Helper -- lazy-load agents
# -----------------------------------------------------------------------------

_session_mgr: Optional[SessionManager] = None
_doc_agent: Optional[DocumentAgent] = None
_ext_agent: Optional[ExtractionAgent] = None
_rf_agent: Optional[RedFlagAgent] = None
_res_agent: Optional[ResearchAgent] = None
_comp_agent: Optional[ComparisonAgent] = None
_report_agent: Optional[ReportAgent] = None
_pipeline: Optional[OrchestrationPipeline] = None


def get_report_agent() -> ReportAgent:
    global _report_agent
    if _report_agent is None:
        _report_agent = ReportAgent(ROOT_DIR)
    return _report_agent


def get_session_manager() -> SessionManager:
    global _session_mgr
    if _session_mgr is None:
        _session_mgr = SessionManager(SESSIONS_DIR)
    return _session_mgr


def get_document_agent() -> DocumentAgent:
    global _doc_agent
    if _doc_agent is None:
        _doc_agent = DocumentAgent(ROOT_DIR, session_manager=get_session_manager())
    return _doc_agent


def get_extraction_agent() -> ExtractionAgent:
    global _ext_agent
    if _ext_agent is None:
        _ext_agent = ExtractionAgent(ROOT_DIR)
    return _ext_agent


def get_red_flag_agent() -> RedFlagAgent:
    global _rf_agent
    if _rf_agent is None:
        _rf_agent = RedFlagAgent(ROOT_DIR)
    return _rf_agent


def get_research_agent() -> ResearchAgent:
    global _res_agent
    if _res_agent is None:
        _res_agent = ResearchAgent(ROOT_DIR)
    return _res_agent


def get_comparison_agent() -> ComparisonAgent:
    global _comp_agent
    if _comp_agent is None:
        _comp_agent = ComparisonAgent(ROOT_DIR)
    return _comp_agent


def get_orchestrator() -> OrchestrationPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = OrchestrationPipeline(ROOT_DIR, session_manager=get_session_manager())
    return _pipeline


# -----------------------------------------------------------------------------
# Handlers
# -----------------------------------------------------------------------------

def cmd_session(args: argparse.Namespace) -> None:
    sm = get_session_manager()
    if args.session_cmd == "create":
        name = " ".join(args.name)
        session = sm.create_session(name)
        sm.print_session_summary(session)
    elif args.session_cmd == "list":
        sessions = sm.list_sessions()
        sm.print_session_list(sessions)
    elif args.session_cmd == "show":
        session = sm.get_session(args.session_id)
        if session:
            sm.print_session_summary(session)
        else:
            print(f"Session not found: {args.session_id}")
    elif args.session_cmd == "delete":
        if sm.delete_session(args.session_id):
            print(f"Session deleted: {args.session_id}")
        else:
            print(f"Failed to delete session: {args.session_id}")


def cmd_document(args: argparse.Namespace) -> None:
    agent = get_document_agent()
    if args.doc_cmd == "list":
        pdfs = agent.list_available_pdfs()
        print(f"\nAvailable PDFs in DATA/ ({len(pdfs)} files):")
        for p in pdfs:
            print(f"  {os.path.basename(p)}")
    elif args.doc_cmd == "process":
        res = agent.process_document(args.pdf_path, session_id=args.session, force=args.force)
        print(f"Status: {res.get('status')} | Chunks: {res.get('total_chunks')}")
    elif args.doc_cmd == "process-all":
        agent.process_all_pdfs(session_id=args.session, limit=args.limit, force=args.force)


def cmd_extract(args: argparse.Namespace) -> None:
    agent = get_extraction_agent()
    res = agent.extract(args.company, args.year)
    print(f"\nExtracted metrics for {args.company} {args.year}:")
    for k, v in res.get("metrics", {}).items():
        if isinstance(v, dict) and v.get("value") is not None:
            print(f"  {k:<22}: {v['value']} (Confidence: {v.get('confidence')})")
    ratios = res.get("calculated_ratios", {})
    if ratios:
        print("\nCalculated Ratios:")
        for rk, rv in ratios.items():
            print(f"  {rk:<22}: {rv}")


def cmd_extract_all(_args: argparse.Namespace) -> None:
    agent = get_extraction_agent()
    agent.extract_all()


def cmd_redflags(args: argparse.Namespace) -> None:
    agent = get_red_flag_agent()
    if args.rf_cmd == "scan":
        res = agent.scan(args.company, args.year)
        summary = res["summary"]
        print(f"\n{'='*60}")
        print(f"  Red Flag Scan: {res['doc_id']}")
        print(f"  Overall Risk Level: {summary['overall_risk_level']} (Score: {summary['risk_score_out_of_100']}/100)")
        print(f"  Total Flags: {summary['total_flags']} [HIGH: {summary['high_severity_count']}, MED: {summary['medium_severity_count']}, LOW: {summary['low_severity_count']}]")
        print(f"{'='*60}")
        for idx, f in enumerate(res.get("red_flags", []), 1):
            sev_badge = f"[{f['severity']}]"
            print(f"{idx}. {sev_badge:<8} {f['title']}")
            print(f"   Category: {f['category']}")
            print(f"   Detail:   {f['description']}")
            prov = f.get("provenance", {})
            print(f"   Source:   Doc: {prov.get('document', 'N/A')}, Page: {prov.get('page_number', 'N/A')}")
            print(f"   Evidence: {f.get('evidence', '')[:120]}...\n")
    elif args.rf_cmd == "scan-all":
        agent.scan_all()


def cmd_pipeline(args: argparse.Namespace) -> None:
    orch = get_orchestrator()
    if args.pipe_cmd == "run":
        res = orch.run_pipeline(args.pdf_path, session_id=args.session, force_reindex=args.force)
        print(f"Pipeline Result: {res.get('pipeline_status')} in {res.get('total_duration_seconds')}s")
    elif args.pipe_cmd == "run-doc":
        res = orch.run_for_doc_id(args.company, args.year)
        print(f"Pipeline completed for {res.get('doc_id')}")


def cmd_research(args: argparse.Namespace) -> None:
    query_text = " ".join(args.query_text) if isinstance(args.query_text, list) else args.query_text
    agent = get_research_agent()
    res = agent.research(query_text)
    print("\n" + res["answer"])


def cmd_compare(args: argparse.Namespace) -> None:
    targets: List[Tuple[str, str]] = []
    for item in args.targets:
        if ":" in item:
            comp, yr = item.split(":", 1)
            targets.append((comp.strip(), yr.strip()))
        elif "_" in item:
            comp, yr = item.split("_", 1)
            targets.append((comp.strip(), yr.strip()))
        else:
            print(f"Invalid format '{item}'. Use COMPANY:YEAR (e.g. AMAZON:2023)")
            return

    agent = get_comparison_agent()
    res = agent.compare(targets)
    print("\n" + res["markdown_table"])
    print("\nBenchmarking Insights:")
    for ins in res["insights"]:
        print(f"- {ins}")


def cmd_report(args: argparse.Namespace) -> None:
    agent = get_report_agent()
    if args.rep_cmd == "generate":
        ext = get_extraction_agent().extract(args.company, args.year)
        rf = get_red_flag_agent().scan(args.company, args.year)
        res = agent.generate(args.company, args.year, ext, rf, force_regenerate=getattr(args, "force", False))
        print(f"\nReport Generated for {args.company} {args.year}:")
        print(f"  PDF:  {res.get('pdf_path')}")
        print(f"  JSON: {res.get('json_path')}")
        print(f"  MD:   {res.get('markdown_path')}")
        print(f"  Recommendation: {res.get('recommendation')}")
    elif args.rep_cmd == "show":
        doc_id = f"{args.company.upper()}_{args.year}"
        md_path = os.path.join(ROOT_DIR, "outputs", "reports", f"{doc_id}_report.md")
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                print("\n" + f.read())
        else:
            print(f"No report found for {doc_id}. Run 'python src/app.py report generate {args.company} {args.year}' first.")
    elif args.rep_cmd == "list":
        rep_dir = os.path.join(ROOT_DIR, "outputs", "reports")
        if not os.path.exists(rep_dir):
            print("No reports directory found.")
            return
        files = sorted(os.listdir(rep_dir))
        print(f"\nGenerated Reports in outputs/reports/ ({len(files)} files):")
        for f in files:
            print(f"  {f}")


def cmd_query(args: argparse.Namespace) -> None:
    query_text = " ".join(args.query_text) if isinstance(args.query_text, list) else args.query_text
    company = getattr(args, "company", None)
    year = getattr(args, "year", None)
    limit = getattr(args, "limit", 5)

    print(f"\n[Query] Searching ChromaDB for: '{query_text}'")
    agent = get_extraction_agent()
    query_emb = agent.embedder.encode(query_text).tolist()

    clauses = []
    if company:
        clauses.append({"company": company.upper()})
    if year:
        clauses.append({"year": str(year)})

    where_filter = clauses[0] if len(clauses) == 1 else ({"$and": clauses} if len(clauses) > 1 else None)

    results = agent.chroma.query(
        query_embeddings=[query_emb],
        n_results=limit,
        where=where_filter,
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not docs:
        print("\n[Query] No matching chunks found.")
        return

    print(f"\nFound {len(docs)} matching chunk(s):\n")
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
        comp = meta.get("company", "?")
        yr = meta.get("year", "?")
        pg = meta.get("page_number", "?")
        doc_name = meta.get("doc_name", "?")
        score = 1.0 - dist if dist is not None else 0.0
        print(f"--- Result {i} (Similarity: {score:.3f} | {comp} {yr} | Page {pg} | {doc_name}) ---")
        preview = doc.strip().replace("\n", " ")
        if len(preview) > 300:
            preview = preview[:300] + "..."
        print(f"{preview}\n")


def cmd_stats(_args: argparse.Namespace) -> None:
    from database.chroma_manager import ChromaManager
    chroma = ChromaManager(os.path.join(ROOT_DIR, "chroma_db"))
    stats = chroma.get_collection_stats()

    print(f"\n{'='*55}")
    print("  ChromaDB Collection Statistics")
    print(f"{'='*55}")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Documents indexed: {len(stats['documents'])}")
    print(f"{'-'*55}")
    for doc_key, count in sorted(stats["documents"].items()):
        print(f"  {doc_key:<35} {count:>6} chunks")
    print(f"{'='*55}\n")


# -----------------------------------------------------------------------------
# Parser
# -----------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="app.py",
        description="Multi-Agent AI Financial Analysis System -- Milestone 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # session
    s_parser = sub.add_parser("session", help="Manage research sessions")
    s_sub    = s_parser.add_subparsers(dest="session_cmd", required=True)
    sc = s_sub.add_parser("create", help="Create a new session")
    sc.add_argument("name", nargs="+", help="Session name")
    s_sub.add_parser("list", help="List all sessions")
    ss = s_sub.add_parser("show", help="Show session details")
    ss.add_argument("session_id", help="Session UUID")
    sd = s_sub.add_parser("delete", help="Delete a session")
    sd.add_argument("session_id", help="Session UUID")

    # document
    d_parser = sub.add_parser("document", help="Document Agent operations")
    d_sub    = d_parser.add_subparsers(dest="doc_cmd", required=True)
    d_sub.add_parser("list", help="List available PDFs")
    dp = d_sub.add_parser("process", help="Process a single PDF")
    dp.add_argument("pdf_path", help="Path to PDF")
    dp.add_argument("--session", default=None, help="Session ID")
    dp.add_argument("--force", action="store_true", help="Force re-indexing")
    da = d_sub.add_parser("process-all", help="Process all PDFs")
    da.add_argument("--session", default=None, help="Session ID")
    da.add_argument("--limit", type=int, default=None, help="Limit number")
    da.add_argument("--force", action="store_true", help="Force re-indexing")

    # extract
    e_parser = sub.add_parser("extract", help="Extract financial metrics")
    e_parser.add_argument("company", help="Company name (e.g. AMAZON)")
    e_parser.add_argument("year",    help="Year (e.g. 2023)")
    sub.add_parser("extract-all", help="Extract metrics for all documents")

    # red flags
    rf_parser = sub.add_parser("redflags", help="Red Flag Agent anomaly & risk scan")
    rf_sub = rf_parser.add_subparsers(dest="rf_cmd", required=True)
    rfc = rf_sub.add_parser("scan", help="Scan red flags for a document")
    rfc.add_argument("company", help="Company name (e.g. AMAZON)")
    rfc.add_argument("year", help="Year (e.g. 2023)")
    rf_sub.add_parser("scan-all", help="Scan red flags across all documents")

    # pipeline
    pipe_parser = sub.add_parser("pipeline", help="Multi-agent orchestration pipeline")
    pipe_sub = pipe_parser.add_subparsers(dest="pipe_cmd", required=True)
    pr = pipe_sub.add_parser("run", help="Run full pipeline on a PDF")
    pr.add_argument("pdf_path", help="Path to PDF")
    pr.add_argument("--session", default=None, help="Session ID")
    pr.add_argument("--force", action="store_true", help="Force re-index")
    pd = pipe_sub.add_parser("run-doc", help="Run downstream agents on indexed doc")
    pd.add_argument("company", help="Company name")
    pd.add_argument("year", help="Year")

    # research
    res_parser = sub.add_parser("research", help="Research Agent multi-hop RAG with citations")
    res_parser.add_argument("query_text", nargs="+", help="Research question")

    # compare
    cmp_parser = sub.add_parser("compare", help="Comparison Agent side-by-side benchmarking")
    cmp_parser.add_argument("targets", nargs="+", help="List of COMPANY:YEAR targets (e.g. AMAZON:2023 APPLE:2024)")

    # report
    rep_parser = sub.add_parser("report", help="Report Agent structured executive report & PDF compiler")
    rep_sub = rep_parser.add_subparsers(dest="rep_cmd", required=True)
    rg = rep_sub.add_parser("generate", help="Generate full JSON/MD/PDF report for a company")
    rg.add_argument("company", help="Company name (e.g. AMAZON)")
    rg.add_argument("year", help="Year (e.g. 2023)")
    rg.add_argument("--force", action="store_true", help="Force regenerate")
    rs = rep_sub.add_parser("show", help="Display markdown report in console")
    rs.add_argument("company", help="Company name")
    rs.add_argument("year", help="Year")
    rep_sub.add_parser("list", help="List all generated reports")

    # query
    q_parser = sub.add_parser("query", help="Semantic vector search")
    q_parser.add_argument("query_text", nargs="+", help="Search query")
    q_parser.add_argument("--company", default=None)
    q_parser.add_argument("--year", default=None)
    q_parser.add_argument("--limit", type=int, default=3)

    # stats
    sub.add_parser("stats", help="Show ChromaDB statistics")

    return parser


def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    dispatch = {
        "session":     cmd_session,
        "document":    cmd_document,
        "extract":     cmd_extract,
        "extract-all": cmd_extract_all,
        "redflags":    cmd_redflags,
        "pipeline":    cmd_pipeline,
        "report":      cmd_report,
        "research":    cmd_research,
        "compare":     cmd_compare,
        "query":       cmd_query,
        "stats":       cmd_stats,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
