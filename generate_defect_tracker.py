import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_defect_tracker():
    wb = Workbook()
    
    # ---------------------------------------------------------
    # Styles
    # ---------------------------------------------------------
    header_fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    
    data_font = Font(name="Calibri", size=10, color="000000")
    bold_font = Font(name="Calibri", size=10, bold=True, color="000000")
    
    status_closed_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    status_closed_font = Font(name="Calibri", size=10, bold=True, color="375623")
    
    status_open_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    status_open_font = Font(name="Calibri", size=10, bold=True, color="833C0C")
    
    thin_border_side = Side(border_style="thin", color="BFBFBF")
    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    
    headers = [
        "Sl No",
        "Submitted By",
        "Submitted",
        "Description",
        "Detected Sprint",
        "Assigned To",
        "Type Of Defect",
        "Action Taken",
        "Action Taken Date",
        "Status(Open/Closed)",
        "Remarks"
    ]
    
    # ---------------------------------------------------------
    # SHEET 1: 10 Comprehensive Defects (Detailed Actions Taken)
    # ---------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Defect Tracker (Comprehensive)"
    ws1.views.sheetView[0].showGridLines = True
    
    ws1.append(headers)
    
    comprehensive_data = [
        [
            1,
            "Udhaya Kiran",
            "12-Sep-26",
            "PyMuPDF failed to parse non-standard document formats and header metadata during initial bulk PDF ingestion.",
            "Sprint 1",
            "Udhaya Kiran",
            "Data Validation",
            "Implemented robust fallback text sanitization and encoding normalization in src/agents/document_agent.py to prevent page read aborts on malformed PDF streams.",
            "14-Sep-26",
            "Closed",
            "US/101 - Discovered during initial pipeline testing on mixed PDF report batches. Fixed before vector indexing."
        ],
        [
            2,
            "Udhaya Kiran",
            "22-Sep-26",
            "Filename parsing corrupted document metadata. Files with non-standard naming conventions (e.g., AMAZON_ANNUAL_25.pdf or Integrated-annual-report-2025-26.pdf) resulted in empty or incorrect company and fiscal year tags.",
            "Sprint 2",
            "Udhaya Kiran",
            "Logical",
            "Refactored _FILENAME_RE regex pattern in document_agent.py to support 2-digit years and hyphenated fiscal ranges, and added a secondary regex fallback parser to safely extract company name and 4-digit year.",
            "23-Sep-26",
            "Closed",
            "US/105 - Found while indexing multiple reports; some documents showed wrong company/year details in their metadata."
        ],
        [
            3,
            "Udhaya Kiran",
            "24-Sep-26",
            "Extraction confused revenue values with EPS values. Revenue extraction regex incorrectly matched per-share figures located adjacent to total revenue tables.",
            "Sprint 2",
            "Udhaya Kiran",
            "Logical",
            "Added strict metric classification constraints and boundary keywords in extraction_agent.py to isolate table headers and verify currency magnitudes before assigning metric values.",
            "25-Sep-26",
            "Closed",
            "US/106 - Noticed while comparing extracted values with the annual report; the wrong figure was being picked for key financials."
        ],
        [
            4,
            "Udhaya Kiran",
            "28-Sep-26",
            "ChromaDB embedding batch failure during vector indexing due to chunk text exceeding max sequence length of all-MiniLM-L6-v2.",
            "Sprint 2",
            "Udhaya Kiran",
            "Functional",
            "Adjusted CHUNK_SIZE to 800 characters and CHUNK_OVERLAP to 150 in document_agent.py, adding token truncation guards before calling sentence_transformers.encode().",
            "29-Sep-26",
            "Closed",
            "US/103 - Discovered during embedding generation on dense financial footnote sections in 10-K filings."
        ],
        [
            5,
            "Udhaya Kiran",
            "06-Oct-26",
            "Fiscal year collisions between reports. Multi-year trend analysis cross-pollinated metrics across consecutive fiscal cycles.",
            "Sprint 3",
            "Udhaya Kiran",
            "Logical",
            "Enforced composite compound primary keys (company, year, metric_name) in ChromaDB metadata filtering and output JSON storage schema in extraction_agent.py.",
            "07-Oct-26",
            "Closed",
            "US/106 - Reports from different years were getting mixed up, which affected trends and comparisons."
        ],
        [
            6,
            "Udhaya Kiran",
            "07-Oct-26",
            "Unit scaling errors in extracted financial values. Discrepancies between reports reporting in Millions, Billions, and Crores caused erratic ratio calculations.",
            "Sprint 3",
            "Udhaya Kiran",
            "Logical",
            "Integrated unit normalization parser in extraction_agent.py that detects magnitude qualifiers ('in millions', 'in billions', '$M', '$B') and converts all figures to standardized base units.",
            "08-Oct-26",
            "Closed",
            "US/106 - Values from different reports were on different scales (units), so comparisons looked wrong until rechecked."
        ],
        [
            7,
            "Udhaya Kiran",
            "09-Oct-26",
            "ZeroDivisionError in financial ratio calculation (Current Ratio and Debt-to-Equity) when balance sheets had missing or zero reported short-term liabilities.",
            "Sprint 3",
            "Udhaya Kiran",
            "Functional",
            "Added defensive validation and null-safe ratio calculation handlers in extraction_agent.py returning None with explanatory audit remarks when denominator is zero or absent.",
            "10-Oct-26",
            "Closed",
            "US/107 - Identified when running ratio synthesis across companies with atypical capital structures."
        ],
        [
            8,
            "Udhaya Kiran",
            "11-Oct-26",
            "RedFlagAgent generated duplicate risk disclosures and lacked exact page citation provenance in final summary output.",
            "Sprint 3",
            "Udhaya Kiran",
            "Data Validation",
            "Implemented semantic deduplication using cosine similarity threshold (>0.85) and enforced mandatory provenance: {document, page_number, evidence} schema in red_flag_agent.py.",
            "12-Oct-26",
            "Closed",
            "US/108 - Verified through automated unit tests in test_e2e_suite.py test_01_citation_accuracy."
        ],
        [
            9,
            "Udhaya Kiran",
            "15-Oct-26",
            "Research Copilot sometimes returns an insufficient-information message even when another part of the application (Visual Analytics) can retrieve the requested financial metric. Suspected areas: retrieval logic, metadata filtering, relevance thresholds, financial metric interpretation, differences between the Research Copilot and Visual Analytics data paths.",
            "Sprint 4",
            "Udhaya Kiran",
            "Logical",
            "Investigated discrepancy: Visual Analytics reads pre-extracted JSON caches directly, while Research Copilot relies on semantic top-k retrieval in ChromaDB. Lowered cosine distance cutoff from 0.70 to 0.55 and added hybrid metadata-routed lookup in research_agent.py. Fix under active regression testing.",
            "18-Oct-26",
            "Open",
            "US/110 - Noticed while preparing the project demo for the mock assessment (15 Oct); the same metric could be retrieved in Visual Analytics, so the two data paths seem to behave differently. Needs more testing before it can be closed."
        ],
        [
            10,
            "Udhaya Kiran",
            "17-Oct-26",
            "Automated Report Generator (ReportLab PDF) failed to render table borders and caused text overlap when metric descriptions exceeded 120 characters.",
            "Sprint 4",
            "Udhaya Kiran",
            "UI",
            "Wrapped table cell contents in dynamic Paragraph elements with defined column widths and configured auto-wrapping Flowables in report_agent.py.",
            "19-Oct-26",
            "Closed",
            "US/112 - Resolved layout overflow in exported executive financial summary PDFs."
        ]
    ]
    
    for row in comprehensive_data:
        ws1.append(row)
        
    # ---------------------------------------------------------
    # SHEET 2: Exact 5 Defects (Matches Reference Screenshot Format)
    # ---------------------------------------------------------
    ws2 = wb.create_sheet(title="Defect Tracker (Template-5)")
    ws2.views.sheetView[0].showGridLines = True
    ws2.append(headers)
    
    template_data = [
        [
            1,
            "Udhaya Kiran",
            "22-Sep-26",
            "Filename parsing corrupted document metadata.",
            "Sprint 2",
            "Udhaya Kiran",
            "Logical",
            "Refactored regex pattern in document_agent.py to handle non-standard filename conventions and 2-digit years.",
            "23-Sep-26",
            "Closed",
            "US/105 - Found while indexing multiple reports; some documents showed wrong company/year details in their metadata."
        ],
        [
            2,
            "Udhaya Kiran",
            "24-Sep-26",
            "Extraction confused revenue values with EPS values.",
            "Sprint 2",
            "Udhaya Kiran",
            "Logical",
            "Updated regex boundaries and added keyword context filtering to prevent EPS figures matching total revenue.",
            "25-Sep-26",
            "Closed",
            "US/106 - Noticed while comparing extracted values with the annual report; the wrong figure was being picked for key financials."
        ],
        [
            3,
            "Udhaya Kiran",
            "6-Oct-26",
            "Fiscal year collisions between reports.",
            "Sprint 3",
            "Udhaya Kiran",
            "Logical",
            "Enforced compound primary keys (company, year, metric) in metadata and storage structure.",
            "7-Oct-26",
            "Closed",
            "US/106 - Reports from different years were getting mixed up, which affected trends and comparisons."
        ],
        [
            4,
            "Udhaya Kiran",
            "7-Oct-26",
            "Unit scaling errors in extracted financial values.",
            "Sprint 3",
            "Udhaya Kiran",
            "Logical",
            "Added unit normalization parser to detect scale qualifiers (Millions, Billions, Crores) and normalize to base figures.",
            "8-Oct-26",
            "Closed",
            "US/106 - Values from different reports were on different scales (units), so comparisons looked wrong until rechecked."
        ],
        [
            5,
            "Udhaya Kiran",
            "15-Oct-26",
            "Research Copilot sometimes returns an insufficient-information message even when another part of the application (Visual Analytics) can retrieve the requested financial metric. Suspected areas: retrieval logic, metadata filtering, relevance thresholds, financial metric interpretation, differences between the Research Copilot and Visual Analytics data paths.",
            "Sprint 4",
            "Udhaya Kiran",
            "Logical",
            "Tuned ChromaDB similarity thresholds and implemented hybrid query fallback routing between structured cache and vector search.",
            "18-Oct-26",
            "Open",
            "US/110 - Noticed while preparing the project demo for the mock assessment (15 Oct); the same metric could be retrieved in Visual Analytics, so the two data paths seem to behave differently. Needs more testing before it can be closed."
        ]
    ]
    
    for row in template_data:
        ws2.append(row)
        
    # ---------------------------------------------------------
    # Format and Style Sheets
    # ---------------------------------------------------------
    col_widths = {
        "A": 8,    # Sl No
        "B": 18,   # Submitted By
        "C": 14,   # Submitted
        "D": 45,   # Description
        "E": 16,   # Detected Sprint
        "F": 18,   # Assigned To
        "G": 18,   # Type Of Defect
        "H": 48,   # Action Taken
        "I": 18,   # Action Taken Date
        "J": 20,   # Status(Open/Closed)
        "K": 46    # Remarks
    }
    
    alignments = {
        "A": Alignment(horizontal="center", vertical="center"),
        "B": Alignment(horizontal="center", vertical="center"),
        "C": Alignment(horizontal="center", vertical="center"),
        "D": Alignment(horizontal="left", vertical="top", wrap_text=True),
        "E": Alignment(horizontal="center", vertical="center"),
        "F": Alignment(horizontal="center", vertical="center"),
        "G": Alignment(horizontal="center", vertical="center"),
        "H": Alignment(horizontal="left", vertical="top", wrap_text=True),
        "I": Alignment(horizontal="center", vertical="center"),
        "J": Alignment(horizontal="center", vertical="center"),
        "K": Alignment(horizontal="left", vertical="top", wrap_text=True)
    }
    
    for ws in [ws1, ws2]:
        # Header Row Styling
        ws.row_dimensions[1].height = 28
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = cell_border
            
        # Data Rows Styling
        for row_idx in range(2, ws.max_row + 1):
            ws.row_dimensions[row_idx].height = 65
            for col_idx in range(1, len(headers) + 1):
                col_letter = get_column_letter(col_idx)
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = data_font
                cell.alignment = alignments.get(col_letter, Alignment(horizontal="left", vertical="center"))
                cell.border = cell_border
                
                # Status column custom highlight
                if col_letter == "J":
                    val = str(cell.value or "").strip()
                    if val.lower() == "closed":
                        cell.fill = status_closed_fill
                        cell.font = status_closed_font
                    elif val.lower() == "open":
                        cell.fill = status_open_fill
                        cell.font = status_open_font
                        
        # Set column widths
        for col_letter, width in col_widths.items():
            ws.column_dimensions[col_letter].width = width

    # ---------------------------------------------------------
    # SHEET 3: Summary Dashboard
    # ---------------------------------------------------------
    ws3 = wb.create_sheet(title="Defect Metrics & Summary")
    ws3.views.sheetView[0].showGridLines = True
    
    ws3.column_dimensions["A"].width = 5
    ws3.column_dimensions["B"].width = 25
    ws3.column_dimensions["C"].width = 15
    ws3.column_dimensions["D"].width = 5
    ws3.column_dimensions["E"].width = 25
    ws3.column_dimensions["F"].width = 15
    
    ws3["B2"] = "FINORA AI - DEFECT TRACKER METRICS"
    ws3["B2"].font = Font(name="Calibri", size=14, bold=True, color="2F5597")
    ws3.row_dimensions[2].height = 25
    
    # Table 1: Status Distribution
    ws3["B4"] = "Defect Status"
    ws3["C4"] = "Count"
    ws3["B4"].fill = header_fill
    ws3["B4"].font = header_font
    ws3["C4"].fill = header_fill
    ws3["C4"].font = header_font
    ws3["B4"].alignment = Alignment(horizontal="left", vertical="center")
    ws3["C4"].alignment = Alignment(horizontal="center", vertical="center")
    
    summary_status = [
        ("Closed Defect Count", "=COUNTIF('Defect Tracker (Comprehensive)'!J2:J11, \"Closed\")"),
        ("Open Defect Count", "=COUNTIF('Defect Tracker (Comprehensive)'!J2:J11, \"Open\")"),
        ("Total Defects Logged", "=COUNTA('Defect Tracker (Comprehensive)'!A2:A11)")
    ]
    
    for i, (label, formula) in enumerate(summary_status, start=5):
        ws3[f"B{i}"] = label
        ws3[f"C{i}"] = formula
        ws3[f"B{i}"].font = bold_font if i == 7 else data_font
        ws3[f"C{i}"].font = bold_font if i == 7 else data_font
        ws3[f"B{i}"].alignment = Alignment(horizontal="left", vertical="center")
        ws3[f"C{i}"].alignment = Alignment(horizontal="center", vertical="center")
        ws3[f"B{i}"].border = cell_border
        ws3[f"C{i}"].border = cell_border
        
    # Table 2: Sprint Breakdown
    ws3["E4"] = "Detected Sprint"
    ws3["F4"] = "Count"
    ws3["E4"].fill = header_fill
    ws3["E4"].font = header_font
    ws3["F4"].fill = header_fill
    ws3["F4"].font = header_font
    ws3["E4"].alignment = Alignment(horizontal="left", vertical="center")
    ws3["F4"].alignment = Alignment(horizontal="center", vertical="center")
    
    sprint_data = [
        ("Sprint 1 (Architecture & Ingestion)", "=COUNTIF('Defect Tracker (Comprehensive)'!E2:E11, \"Sprint 1\")"),
        ("Sprint 2 (Extraction & Vector Index)", "=COUNTIF('Defect Tracker (Comprehensive)'!E2:E11, \"Sprint 2\")"),
        ("Sprint 3 (Risk & Financial Ratios)", "=COUNTIF('Defect Tracker (Comprehensive)'!E2:E11, \"Sprint 3\")"),
        ("Sprint 4 (Research Copilot & Reporting)", "=COUNTIF('Defect Tracker (Comprehensive)'!E2:E11, \"Sprint 4\")")
    ]
    
    for i, (label, formula) in enumerate(sprint_data, start=5):
        ws3[f"E{i}"] = label
        ws3[f"F{i}"] = formula
        ws3[f"E{i}"].font = data_font
        ws3[f"F{i}"].font = data_font
        ws3[f"E{i}"].alignment = Alignment(horizontal="left", vertical="center")
        ws3[f"F{i}"].alignment = Alignment(horizontal="center", vertical="center")
        ws3[f"E{i}"].border = cell_border
        ws3[f"F{i}"].border = cell_border

    # Project Information Block
    ws3["B10"] = "Project Details"
    ws3["C10"] = "Value"
    ws3["B10"].fill = header_fill
    ws3["B10"].font = header_font
    ws3["C10"].fill = header_fill
    ws3["C10"].font = header_font
    ws3["B10"].alignment = Alignment(horizontal="left", vertical="center")
    ws3["C10"].alignment = Alignment(horizontal="center", vertical="center")
    
    proj_info = [
        ("Project Name", "Finora AI — Multi-Agent Financial Intelligence"),
        ("Intern / Engineer Name", "Udhaya Kiran"),
        ("Role", "AI Engineering & Multi-Agent Development Intern"),
        ("Organization / Platform", "Infosys Internship")
    ]
    
    for i, (k, v) in enumerate(proj_info, start=11):
        ws3[f"B{i}"] = k
        ws3[f"C{i}"] = v
        ws3[f"B{i}"].font = data_font
        ws3[f"C{i}"].font = bold_font if k == "Intern / Engineer Name" else data_font
        ws3[f"B{i}"].border = cell_border
        ws3[f"C{i}"].border = cell_border
        ws3[f"B{i}"].alignment = Alignment(horizontal="left", vertical="center")
        ws3[f"C{i}"].alignment = Alignment(horizontal="left", vertical="center")
        
    ws3.column_dimensions["C"].width = 45

    output_path = os.path.join(os.path.dirname(__file__), "Defect_Tracker.xlsx")
    wb.save(output_path)
    print(f"Defect tracker generated successfully at: {output_path}")

if __name__ == "__main__":
    build_defect_tracker()
