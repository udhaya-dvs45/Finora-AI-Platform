import sys
import os

# Robust Path configuration — ensure both ROOT and SRC are at front of sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR) if os.path.basename(CURRENT_DIR) == "frontend" else CURRENT_DIR
SRC_DIR = os.path.join(ROOT_DIR, "src")

for p in [ROOT_DIR, SRC_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Suppress noisy env vars
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_FLAX", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import json
import streamlit as st
import pandas as pd

# Multi-Agent Workflow and Agents imports with fallback
try:
    from workflow.graph import financial_workflow
except ImportError:
    from src.workflow.graph import financial_workflow

try:
    from agents.research_agent import ResearchAgent
    from agents.comparison_agent import ComparisonAgent
    from agents.red_flag_agent import RedFlagAgent
    from agents.extraction_agent import ExtractionAgent
    from agents.report_agent import ReportAgent
    from agents.document_agent import parse_document_metadata
except ImportError:
    from src.agents.research_agent import ResearchAgent
    from src.agents.comparison_agent import ComparisonAgent
    from src.agents.red_flag_agent import RedFlagAgent
    from src.agents.extraction_agent import ExtractionAgent
    from src.agents.report_agent import ReportAgent
    from src.agents.document_agent import parse_document_metadata



# Streamlit Page Setup
st.set_page_config(
    page_title="Financial Multi-Agent AI System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 16px;
        color: white;
        margin-bottom: 12px;
        border: 1px solid #334155;
    }
    .badge-high {
        background-color: #ef4444;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-medium {
        background-color: #f59e0b;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-low {
        background-color: #10b981;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .citation-box {
        background-color: #0f172a;
        border-left: 4px solid #3b82f6;
        padding: 10px 14px;
        border-radius: 4px;
        margin: 8px 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Agents in Session State
@st.cache_resource
def load_research_agent():
    return ResearchAgent(ROOT_DIR)

@st.cache_resource
def load_comparison_agent():
    return ComparisonAgent(ROOT_DIR)

@st.cache_resource
def load_extraction_agent():
    return ExtractionAgent(ROOT_DIR)

@st.cache_resource
def load_red_flag_agent():
    return RedFlagAgent(ROOT_DIR)

@st.cache_resource
def load_report_agent():
    return ReportAgent(ROOT_DIR)


# Helper: list processed documents
def get_available_documents():
    metrics_dir = os.path.join(ROOT_DIR, "outputs", "financial_metrics")
    docs = []
    if os.path.exists(metrics_dir):
        for f in os.listdir(metrics_dir):
            if f.endswith("_metrics.json"):
                try:
                    with open(os.path.join(metrics_dir, f), "r", encoding="utf-8") as jf:
                        d = json.load(jf)
                        if "company" in d and "year" in d:
                            docs.append((d["company"].upper(), str(d["year"])))
                            continue
                except Exception:
                    pass
                stem = f.replace("_metrics.json", "")
                parts = stem.rsplit("_", 1)
                if len(parts) == 2:
                    docs.append((parts[0].upper(), parts[1]))

    # Also include any filings present in DATA directory
    data_dir = os.path.join(ROOT_DIR, "DATA")
    if os.path.exists(data_dir):
        for f in os.listdir(data_dir):
            if f.lower().endswith(".pdf"):
                c, y = parse_document_metadata(os.path.join(data_dir, f))
                if c and y and y != "unknown":
                    docs.append((c.upper(), str(y)))

    if not docs:
        docs = [("AMAZON", "2023"), ("APPLE", "2024"), ("META", "2024"), ("TESLA", "2023"), ("INFOSYS", "2023")]
    return sorted(list(set(docs)))


# App Header
st.title("📈 Multi-Agent Financial Analysis System")
st.caption("Milestone 3: LangGraph Orchestration • Red Flag Audit • Multi-Hop Research • Benchmarking")

# Clear any legacy locked widget keys from previous runs
st.session_state.pop("dropdown_selection", None)

available_docs = get_available_documents()
doc_options = [f"{c} ({y})" for c, y in available_docs]

# Sidebar
st.sidebar.header("📁 Document Ingestion & Selection")

uploaded_file = st.sidebar.file_uploader("Upload New Financial PDF", type=["pdf"], key="pdf_file_uploader")
up_doc_key = None
if uploaded_file is not None:
    save_path = os.path.join(ROOT_DIR, "DATA", uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Detect entity and fiscal year from uploaded PDF
    up_company, up_year = parse_document_metadata(save_path)
    up_doc_key = f"{up_company} ({up_year})"

    metrics_file = os.path.join(ROOT_DIR, "outputs", "financial_metrics", f"{up_company}_{up_year}_metrics.json")
    is_indexed = os.path.exists(metrics_file)

    # If this is a newly uploaded file or user switched files
    if st.session_state.get("current_uploaded_filename") != uploaded_file.name:
        st.session_state["current_uploaded_filename"] = uploaded_file.name
        st.session_state["selected_doc"] = up_doc_key
        if not is_indexed:
            with st.spinner(f"🚀 New filing detected! Executing LangGraph Multi-Agent Pipeline for {up_company} {up_year}..."):
                res = financial_workflow.invoke({"pdf_path": save_path})
                st.session_state["selected_doc"] = f"{res.get('company', up_company)} ({res.get('year', up_year)})"
                st.sidebar.success(f"✅ Ingestion complete for {up_company} {up_year}!")
        st.rerun()

    # Status & Controls for the uploaded file
    if is_indexed:
        st.sidebar.success(f"✅ Active Uploaded Filing: **{up_doc_key}**")
        col_btn1, col_btn2 = st.sidebar.columns(2)
        if col_btn1.button(f"👁️ View {up_company}", width="stretch"):
            st.session_state["selected_doc"] = up_doc_key
            st.rerun()
        if col_btn2.button(f"🔄 Re-analyze", width="stretch"):
            with st.spinner(f"Re-running LangGraph Pipeline for {up_company} {up_year}..."):
                res = financial_workflow.invoke({"pdf_path": save_path})
                st.session_state["selected_doc"] = up_doc_key
                st.sidebar.success(f"Re-orchestration complete!")
                st.rerun()
    else:
        st.sidebar.info(f"📄 Detected: **{up_company} ({up_year})**")
        if st.sidebar.button(f"🚀 Analyze {up_company} ({up_year})", type="primary", width="stretch"):
            with st.spinner(f"Executing LangGraph Pipeline for {up_company} {up_year}..."):
                res = financial_workflow.invoke({"pdf_path": save_path})
                st.session_state["selected_doc"] = up_doc_key
                st.sidebar.success(f"Completed!")
                st.rerun()

st.sidebar.markdown("---")

# Refresh options after potential upload / ingestion
available_docs = get_available_documents()
doc_options = [f"{c} ({y})" for c, y in available_docs]

# Ensure uploaded doc is in doc_options
if up_doc_key and up_doc_key not in doc_options:
    doc_options.append(up_doc_key)
    doc_options = sorted(list(set(doc_options)))

# Default to uploaded document if present, otherwise first available
if "selected_doc" not in st.session_state:
    st.session_state["selected_doc"] = up_doc_key if up_doc_key else (doc_options[0] if doc_options else "AMAZON (2023)")

if st.session_state.get("selected_doc") not in doc_options and doc_options:
    st.session_state["selected_doc"] = up_doc_key if (up_doc_key and up_doc_key in doc_options) else doc_options[0]

current_idx = doc_options.index(st.session_state["selected_doc"]) if st.session_state.get("selected_doc") in doc_options else 0

selected_doc_str = st.sidebar.selectbox(
    "Select Analyzed Filing:",
    doc_options,
    index=current_idx,
)
st.session_state["selected_doc"] = selected_doc_str

if selected_doc_str:
    sel_company, sel_year = selected_doc_str.replace(")", "").split(" (")
else:
    sel_company, sel_year = "META", "2024"

# Load Selected Document Data
metrics_agent = load_extraction_agent()
rf_agent = load_red_flag_agent()
rep_agent = load_report_agent()

# Load / Cache results
metrics_data = metrics_agent.extract(sel_company, sel_year)
red_flags_data = rf_agent.scan(sel_company, sel_year)
report_data = rep_agent.generate(sel_company, sel_year, metrics_data, red_flags_data)


# Main Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Report",
    "📈 Financial Metrics",
    "🚩 Red Flags & Audit",
    "⚖️ Side-by-Side Comparison",
    "🔍 Grounded Research",
])


# -----------------------------------------------------------------------------
# TAB 1: Executive Report
# -----------------------------------------------------------------------------
with tab1:
    st.subheader(f"Executive Analysis: {sel_company} ({sel_year})")
    
    col1, col2, col3, col4 = st.columns(4)
    rev_val = metrics_data.get("metrics", {}).get("revenue", {}).get("value")
    op_val = metrics_data.get("metrics", {}).get("operating_income", {}).get("value")
    net_val = metrics_data.get("metrics", {}).get("net_income", {}).get("value")
    risk_level = red_flags_data.get("summary", {}).get("overall_risk_level", "LOW")
    
    col1.metric("Revenue", f"{rev_val:,.1f}" if isinstance(rev_val, (int, float)) else "N/A")
    col2.metric("Operating Income", f"{op_val:,.1f}" if isinstance(op_val, (int, float)) else "N/A")
    col3.metric("Net Income", f"{net_val:,.1f}" if isinstance(net_val, (int, float)) else "N/A")
    col4.metric("Risk Level", risk_level, delta=f"{red_flags_data.get('summary', {}).get('total_flags', 0)} Flags", delta_color="inverse")

    st.markdown("---")
    
    # Download Report Actions
    pdf_path = report_data.get("pdf_path")
    json_path = report_data.get("json_path")
    md_path = report_data.get("markdown_path")

    btn_col1, btn_col2, btn_col3 = st.columns(3)
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f_pdf:
            btn_col1.download_button(
                label="📥 Download Executive PDF Report",
                data=f_pdf.read(),
                file_name=f"{sel_company}_{sel_year}_Executive_Report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
    elif "pdf_bytes" in report_data:
        btn_col1.download_button(
            label="📥 Download Executive PDF Report",
            data=report_data["pdf_bytes"],
            file_name=f"{sel_company}_{sel_year}_Executive_Report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    else:
        btn_col1.button("⏳ PDF Ready on Demand", disabled=True, use_container_width=True)

    if json_path and os.path.exists(json_path):
        with open(json_path, "rb") as f_json:
            btn_col2.download_button(
                label="📄 Download Report JSON",
                data=f_json.read(),
                file_name=f"{sel_company}_{sel_year}_report.json",
                mime="application/json",
                use_container_width=True
            )

    if md_path and os.path.exists(md_path):
        with open(md_path, "rb") as f_md:
            btn_col3.download_button(
                label="📝 Download Markdown",
                data=f_md.read(),
                file_name=f"{sel_company}_{sel_year}_report.md",
                mime="text/markdown",
                use_container_width=True
            )

    st.markdown("---")
    st.markdown(report_data.get("markdown_report", "No report generated."))


# -----------------------------------------------------------------------------
# TAB 2: Financial Metrics
# -----------------------------------------------------------------------------
with tab2:
    st.subheader(f"Extracted Metrics & Provenance: {sel_company} ({sel_year})")
    
    m_entries = []
    for k, v in metrics_data.get("metrics", {}).items():
        if isinstance(v, dict):
            m_entries.append({
                "Metric": k.replace("_", " ").title(),
                "Value": f"{v.get('value'):,}" if isinstance(v.get('value'), (int, float)) else str(v.get('value')),
                "Confidence": v.get("confidence", "N/A"),
                "Source Page": v.get("page_number", "N/A"),
                "Document": v.get("document", "N/A"),
            })
    df_m = pd.DataFrame(m_entries)
    st.dataframe(df_m, use_container_width=True)

    st.subheader("Calculated Financial Ratios")
    ratios_dict = metrics_data.get("ratios", metrics_data.get("calculated_ratios", {}))
    r_cols = st.columns(len(ratios_dict) if ratios_dict else 1)
    for idx, (rk, rv) in enumerate(ratios_dict.items()):
        val_str = rv.get("percentage") if isinstance(rv, dict) and "percentage" in rv else (f"{rv.get('value'):.2f}" if isinstance(rv, dict) else str(rv))
        r_cols[idx % len(r_cols)].metric(rk.replace("_", " ").title(), val_str)


# -----------------------------------------------------------------------------
# TAB 3: Red Flags & Risk Audit
# -----------------------------------------------------------------------------
with tab3:
    st.subheader(f"Audit & Anomaly Scanner: {sel_company} ({sel_year})")
    
    rf_sum = red_flags_data.get("summary", {})
    st.info(f"**Overall Assessment:** `{rf_sum.get('overall_risk_level')}` (Risk Score: {rf_sum.get('risk_score_out_of_100')}/100) — Total {rf_sum.get('total_flags')} flag(s) identified.")

    for f in red_flags_data.get("red_flags", []):
        badge = "badge-high" if f["severity"] == "HIGH" else "badge-medium" if f["severity"] == "MEDIUM" else "badge-low"
        with st.expander(f"[{f['severity']}] {f['title']} — {f['category']}"):
            st.markdown(f"**Description:** {f['description']}")
            prov = f.get("provenance", {})
            st.markdown(f"**Grounding:** `Document: {prov.get('document', 'N/A')}`, `Page: {prov.get('page_number', 'N/A')}`")
            st.markdown(f"**Evidence Snippet:**")
            st.caption(f.get("evidence", ""))


# -----------------------------------------------------------------------------
# TAB 4: Side-by-Side Comparison
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("Cross-Document Financial Benchmarking")
    st.write("Select two or more companies to compare side-by-side:")
    
    # Intelligently default to including the currently selected company
    default_benchmarks = []
    if selected_doc_str in doc_options:
        default_benchmarks.append(selected_doc_str)
    for opt in doc_options:
        if opt != selected_doc_str and len(default_benchmarks) < 2:
            default_benchmarks.append(opt)

    selected_benchmarks = st.multiselect(
        "Companies to Benchmark:",
        doc_options,
        default=default_benchmarks,
    )

    if len(selected_benchmarks) >= 2:
        targets = []
        for b in selected_benchmarks:
            c, y = b.replace(")", "").split(" (")
            targets.append((c, y))
        
        comp_agent = load_comparison_agent()
        with st.spinner("Comparing financials..."):
            comp_res = comp_agent.compare(targets)
        
        st.markdown(comp_res.get("markdown_table", ""))
        
        st.subheader("Key Benchmarking Takeaways")
        for ins in comp_res.get("insights", []):
            st.success(ins)
    else:
        st.warning("Please select at least 2 entities to benchmark.")


# -----------------------------------------------------------------------------
# TAB 5: Grounded Research
# -----------------------------------------------------------------------------
with tab5:
    st.subheader("Interactive Financial Research Agent (Grounded RAG)")
    st.caption("Ask questions across all indexed annual filings. Answers are verified with exact document and page citations.")

    res_agent = load_research_agent()
    
    example_prompts = [
        f"What are {sel_company}'s primary revenue drivers in {sel_year}?",
        f"What litigations, regulatory investigations, or risk factors are disclosed for {sel_company} in {sel_year}?",
        f"Analyze {sel_company}'s operating cash flow and profitability in {sel_year}.",
    ]
    
    st.write(f"**Quick Example Questions for {sel_company} ({sel_year}):**")
    q_col1, q_col2, q_col3 = st.columns(3)
    clicked_prompt = None
    if q_col1.button(example_prompts[0]):
        clicked_prompt = example_prompts[0]
    if q_col2.button(example_prompts[1]):
        clicked_prompt = example_prompts[1]
    if q_col3.button(example_prompts[2]):
        clicked_prompt = example_prompts[2]

    user_query = st.text_input("Enter your research question:", value=clicked_prompt or "")

    if st.button("🔍 Run Research Agent", type="primary") and user_query:
        with st.spinner("Decomposing query, querying ChromaDB vector store, and synthesizing cited findings..."):
            ans_res = res_agent.research(user_query)
        
        st.markdown("### Synthesized Grounded Answer")
        st.markdown(ans_res.get("answer", "No answer found."))

        with st.expander("🔎 View Step-by-Step Reasoning Trace"):
            for step in ans_res.get("reasoning_steps", []):
                st.write(f"- {step}")

        with st.expander("📚 Verified Source Citations"):
            for cit in ans_res.get("citations", []):
                st.markdown(f"**{cit['citation_tag']}**")
                st.caption(f"Excerpt: \"{cit['excerpt']}\"")

