# Finora AI — Financial Intelligence & Multi-Agent Research Terminal

[![Platform](https://img.shields.io/badge/Platform-Finora%20AI-0F172A?style=for-the-badge&logo=probot)](https://github.com/udhaya-dvs45/Finora-AI-Platform)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933?style=for-the-badge&logo=nodedotjs)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python)](https://python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF6F00?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Vector DB](https://img.shields.io/badge/Vector%20DB-ChromaDB-blue?style=for-the-badge)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Finora AI** is an institutional-grade, multi-agent financial intelligence terminal built to ingest, analyze, cross-examine, and report on corporate 10-K filings and annual reports. Powered by a collaborative swarm of specialized AI agents, Finora AI extracts critical financial metrics, detects governance and liquidity red flags, benchmarks peer competitors, and generates executive-ready PDF intelligence dossiers.

Developed as part of the **Infosys Springboard Internship** by **Udhaya Kiran**.

---

## 🏛️ Multi-Agent Architecture

Finora AI adopts a decoupled, event-driven multi-agent orchestration architecture coordinated via **LangGraph**:

```
                       ┌────────────────────────┐
                       │  Annual Report (PDF)   │
                       └───────────┬────────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │     Document Agent     │
                       │ (PyMuPDF & Chunking)   │
                       └───────────┬────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
       ┌────────────────────────┐    ┌────────────────────────┐
       │   ChromaDB Vectors     │    │    Extraction Agent    │
       │ (all-MiniLM-L6-v2)     │    │ (Regex & Unit Scaling) │
       └────────────┬───────────┘    └────────────┬───────────┘
                    │                             │
                    ├─────────────────────────────┤
                    ▼                             ▼
       ┌────────────────────────┐    ┌────────────────────────┐
       │     Research Agent     │    │     Red Flag Agent     │
       │  (Hybrid Query RAG)    │    │ (Risk & Disclosure)    │
       └────────────┬───────────┘    └────────────┬───────────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   ▼
                       ┌────────────────────────┐
                       │    Comparison Agent    │
                       │ (Cross-Company Matrix) │
                       └───────────┬────────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │      Report Agent      │
                       │ (ReportLab Executive)  │
                       └───────────┬────────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │ Finora Web Terminal UI │
                       └────────────────────────┘
```

### Specialized Agents

| Agent | Module | Core Functionality |
|---|---|---|
| **Document Agent** | `src/agents/document_agent.py` | Extracts raw PDF text page-by-page using PyMuPDF, chunks text with sliding overlap, and generates dense vector embeddings. |
| **Extraction Agent** | `src/agents/extraction_agent.py` | Captures financial metrics (Revenue, Net Income, EPS, Assets, Liabilities) and computes derived financial ratios. |
| **Red Flag Agent** | `src/agents/red_flag_agent.py` | Scans for auditor qualifications, debt surges, litigation hazards, and going-concern risks with exact source citations. |
| **Research Agent** | `src/agents/research_agent.py` | Grounded RAG reasoning engine for multi-part financial inquiries with inline provenance attribution. |
| **Comparison Agent** | `src/agents/comparison_agent.py` | Benchmarks multiple companies side-by-side across fiscal years without multi-year collisions. |
| **Report Agent** | `src/agents/report_agent.py` | Compiles multi-agent outputs into publication-grade, 5-section executive summary PDF reports via ReportLab. |

---

## ✨ Key Features

- **Institutional Financial Terminal**: High-density UI featuring dark-mode aesthetics, responsive navigation, Chart.js multi-currency performance visualizations, and live agent telemetry.
- **Strict Grounding & Provenance**: Every extracted ratio, disclosure risk, and research answer includes document name, fiscal year, and exact page number.
- **Multi-Company Coverage**: Seeded with real filings from Amazon, Apple, Tesla, Meta, Microsoft, Infosys, and Reliance Industries (FY2023–2025).
- **Vercel & Cloud Ready**: Zero-config Vercel serverless deployment (`vercel.json`) serving the frontend SPA and Node.js REST API.

---

## 📁 Agile & Quality Assurance Documentation

The project includes formal Agile and testing documentation located in [`agile_documents/`](agile_documents/):

1. **[`Agile_Template.xlsx`](agile_documents/Agile_Template.xlsx)**:
   - Complete 16 User Stories across Sprints 1 to 4 (`US/101` to `US/116`).
   - Fields: `Planned Sprint`, `Actual Sprint`, `US ID`, `User Story Description`, `MOSCOW`, `Dependency`, `Assignee` (`Udhaya Kiran`), and `Status` (`3- Completed`).
2. **[`Defect_Tracker.xlsx`](agile_documents/Defect_Tracker.xlsx)**:
   - Comprehensive bug logging across all development sprints.
   - Includes root-cause diagnostics, classification, and technical resolutions for regex boundary fixes, unit scaling, and vector sequence lengths.
3. **[`Unit_Test_Plan.xlsx`](agile_documents/Unit_Test_Plan.xlsx)**:
   - 12 Unit Test Cases (`UTC_001` through `UTC_012`) validating citation faithfulness, numerical calculations, and 4-stage pipeline execution.
   - 100% Pass Rate with an official intern sign-off block.

---

## 🛠️ Repository Directory Structure

```plaintext
INFOSYS_INTERN/
├── agile_documents/             # Official Agile & QA Deliverables
│   ├── Agile_Template.xlsx      # User Stories & Sprint Backlog
│   ├── Defect_Tracker.xlsx      # QA Defect Resolution Tracker
│   ├── Unit_Test_Plan.xlsx      # Test Specification & Verification Matrix
│   └── README.md                # Agile Documentation Index
├── DATA/                        # Source Company Annual Reports (PDFs)
├── frontend/                    # Web Application & API
│   ├── public/                  # Static SPA (HTML5, Vanilla CSS, JS)
│   │   ├── css/style.css        # Financial Terminal Glassmorphic Theme
│   │   ├── js/app.js            # Client UI Logic & Routing
│   │   ├── js/data.js           # Client-side Data Stores
│   │   └── index.html           # Main Application Shell
│   ├── server.js                # Express Server & Vercel Handler
│   └── package.json             # Frontend Dependencies
├── processed/                   # Parsed JSON and Vector Chunks
├── outputs/                     # Generated Dossiers & PDF Reports
├── src/                         # Python Agent Core Engine
│   ├── agents/                  # Individual Agent Implementations
│   ├── database/                # ChromaDB Vector Store Client
│   ├── workflow/                # LangGraph StateGraph Orchestration
│   └── app.py                   # Python CLI Entrypoint
├── test_e2e_suite.py            # End-to-End Automated Test Suite
├── vercel.json                  # Vercel Serverless Deployment Config
├── package.json                 # Project Root Configuration
├── requirements.txt             # Python Dependencies
└── README.md                    # Project Documentation
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Node.js**: v18.x or higher
- **Python**: v3.10 or higher
- **Git**

---

### 1. Run the Web Terminal (Node.js)

```bash
# Clone the repository
git clone https://github.com/udhaya-dvs45/Finora-AI-Platform.git
cd Finora-AI-Platform

# Install dependencies
npm install

# Start the application server
npm start
```
The terminal will be accessible at `http://localhost:3000`.

---

### 2. Run the Multi-Agent Python Engine (CLI)

```bash
# Set up Python virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS / Linux

# Install Python requirements
pip install -r requirements.txt

# Run the full automated test suite
python test_e2e_suite.py

# Process a filing end-to-end (Doc -> Extract -> Red Flags -> Report)
python src/app.py pipeline run DATA/AMAZON_ANNUAL_2023.pdf

# Run cross-company peer benchmark
python src/app.py compare AMAZON:2023 APPLE:2024
```

---

## ☁️ Deployment to Vercel

This repository is pre-configured with [`vercel.json`](vercel.json) for 1-click deployment:

1. Import this repository into [Vercel](https://vercel.com).
2. Leave root directory as `./`.
3. (Optional) Set `GEMINI_API_KEY` under Environment Variables.
4. Click **Deploy**.

---

## 👨‍💻 Author

- **Udhaya Kiran**
- **Project**: Finora AI — Financial Intelligence Terminal
- **Program**: Infosys Springboard Internship
- **GitHub**: [@udhaya-dvs45](https://github.com/udhaya-dvs45)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
