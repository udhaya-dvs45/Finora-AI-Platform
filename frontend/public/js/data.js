// Finora AI - Core Data Engine
// Mirrors all extracted data, outputs, documents, and reference platform records

const FIN_DATA = {
  user: {
    name: "Udhaya Kiran",
    initials: "UK",
    email: "demo@finora.ai",
    role: "Lead Financial Analyst"
  },
  agents: [
    { id: "doc_agent", name: "Document Agent", role: "Parse & chunk", status: "Ready", color: "#38bdf8", badge: "cyan" },
    { id: "ext_agent", name: "Extraction Agent", role: "KPIs & ratios", status: "Ready", color: "#34d399", badge: "emerald" },
    { id: "risk_agent", name: "Risk Agent", role: "Red flags", status: "Ready", color: "#f87171", badge: "rose" },
    { id: "bench_agent", name: "Benchmark Agent", role: "Comparison", status: "Ready", color: "#c084fc", badge: "purple" },
    { id: "res_agent", name: "Research Agent", role: "Q&A with citations", status: "Ready", color: "#fbbf24", badge: "amber" }
  ],
  stats: {
    companiesCount: 14,
    documentsCount: 20,
    sessionsCount: 3,
    reportsCount: 6,
    riskFlagsCount: 40
  },
  financialOverview: [
    { ticker: "N/A", name: "Consolidated Tech", revenue: "$128.00K", netMargin: "7.9%", growth: "+4.9%" },
    { ticker: "TCS", name: "Tata Consultancy Services", revenue: "$31.40K", netMargin: "22.5%", growth: "+4.3%" },
    { ticker: "Tesla", name: "Tesla Inc.", revenue: "$88.00K", netMargin: "0.6%", growth: "-4.3%" },
    { ticker: "INFOYS", name: "Infosys Ltd.", revenue: "$0", netMargin: "N/A", growth: "+0.0%" },
    { ticker: "Amazon", name: "Amazon.com Inc.", revenue: "$705.00B", netMargin: "9.4%", growth: "+10.5%" },
    { ticker: "Apple", name: "Apple Inc.", revenue: "$394.33B", netMargin: "24.6%", growth: "-0.3%" },
    { ticker: "Microsoft", name: "Microsoft Corp.", revenue: "$211.91B", netMargin: "34.1%", growth: "+6.9%" }
  ],
  agentActivity: [
    { id: 1, agent: "Research Agent", action: "Question answered with validated cited evidence", latency: "4.7s", time: "Just now", status: "success" },
    { id: 2, agent: "Research Agent", action: "Processing research question", latency: "2.1s", time: "2m ago", status: "processing" },
    { id: 3, agent: "Research Agent", action: "Question answered with validated cited evidence", latency: "5.4s", time: "14m ago", status: "success" },
    { id: 4, agent: "Research Agent", action: "Processing research question", latency: "1.9s", time: "22m ago", status: "processing" },
    { id: 5, agent: "Research Agent", action: "Question answered with validated cited evidence", latency: "3.4s", time: "1h ago", status: "success" },
    { id: 6, agent: "Extraction Agent", action: "KPI & ratio vector verification complete", latency: "6.8s", time: "2h ago", status: "success" },
    { id: 7, agent: "Risk Agent", action: "Scanned 18 filings for going-concern and antitrust risks", latency: "8.2s", time: "3h ago", status: "success" }
  ],
  sessions: [
    {
      id: "9ef07039-6609-4817-bffb-a89525b6f5ad",
      name: "Big Tech Financial Analysis 2023",
      description: "Comprehensive analysis of FAANG/Big Tech companies using 2023 annual reports",
      tags: ["Technology", "2023", "FAANG"],
      docsCount: 11,
      msgsCount: 218,
      status: "active",
      date: "Sep 19, 2026"
    },
    {
      id: "78ac3120-1a22-4fe1-bb32-9012384a8bc9",
      name: "Global IT Services & Consulting Benchmarking",
      description: "Comparative study of TCS, Infosys, and Cognizant operational efficiency & cloud growth",
      tags: ["IT Services", "FY2024", "Margins"],
      docsCount: 5,
      msgsCount: 84,
      status: "active",
      date: "Oct 02, 2026"
    },
    {
      id: "3e592df8-6c0b-4191-8fa7-cb384210a562",
      name: "Automotive & Clean Energy Disruption",
      description: "Deep dive into Tesla gross margin compression and European EV competitive shifts",
      tags: ["Automotive", "CleanTech", "Risk"],
      docsCount: 4,
      msgsCount: 52,
      status: "completed",
      date: "Oct 08, 2026"
    }
  ],
  documents: [
    {
      id: "cf2b478d-9eaa-4bbc-a552-42087bd91cb1",
      name: "Reliance-Industries_Annual_Report_FY2026.pdf",
      company: "Reliance",
      type: "Annual Report (10-K)",
      year: "FY2026",
      chunks: 6,
      date: "Oct 12, 2026",
      size: "9.7 MB",
      format: "pdf"
    },
    {
      id: "4d65528d-7652-4458-9b98-e78e025af9c4",
      name: "Microsoft_Annual_Report_FY2023.pdf",
      company: "Microsoft",
      type: "Annual Report (10-K)",
      year: "FY2026",
      chunks: 6,
      date: "Oct 11, 2026",
      size: "2.4 MB",
      format: "pdf"
    },
    {
      id: "fad10426-cfa0-4602-9396-96d2e7dc9514",
      name: "TCS_Annual_Report_FY2026.pdf",
      company: "TCS",
      type: "Annual Report (10-K)",
      year: "FY2026",
      chunks: 6,
      date: "Oct 10, 2026",
      size: "3.1 MB",
      format: "pdf"
    },
    {
      id: "d47e78ca-c73f-4581-9df6-36610702cf45",
      name: "Tesla_Annual_Report_FY2026.pdf",
      company: "Tesla",
      type: "Annual Report (10-K)",
      year: "FY2026",
      chunks: 6,
      date: "Oct 10, 2026",
      size: "1.0 MB",
      format: "pdf"
    },
    {
      id: "a18db553-4c39-492f-8852-4fc3470cd877",
      name: "Amazon_Annual_Report_FY2025.pdf",
      company: "Amazon",
      type: "Annual Report (10-K)",
      year: "FY2025",
      chunks: 6,
      date: "Oct 10, 2026",
      size: "1.6 MB",
      format: "pdf"
    },
    {
      id: "820d69f4-c727-4397-b5d3-fa1c6670987e",
      name: "Amazon_23.pdf",
      company: "Amazon",
      type: "Annual Report (10-K)",
      year: "FY2023",
      chunks: 205,
      date: "Oct 10, 2026",
      size: "1.3 MB",
      format: "pdf"
    },
    {
      id: "ae91ad37-d626-4514-9011-57d3a9473838",
      name: "APPLE_25.pdf",
      company: "Apple",
      type: "Annual Report (10-K)",
      year: "FY2026",
      chunks: 214,
      date: "Oct 10, 2026",
      size: "1.8 MB",
      format: "pdf"
    },
    {
      id: "5b1a4c5e-1285-417f-b420-7ec1300483d4",
      name: "Tesla_25.pdf",
      company: "Tesla",
      type: "Annual Report (10-K)",
      year: "FY2026",
      chunks: 363,
      date: "Oct 8, 2026",
      size: "1.7 MB",
      format: "pdf"
    },
    {
      id: "d2483692-f857-4cc3-ba51-300c80845990",
      name: "Amazon_23.pdf",
      company: "reliance",
      type: "Annual Report (10-K)",
      year: "FY2023",
      chunks: 205,
      date: "Oct 8, 2026",
      size: "1.3 MB",
      format: "pdf"
    },
    {
      id: "793b522c-5f7b-4e61-a906-d7d051c2f67e",
      name: "Infosys_Annual_Report_FY2023_Finora_Analysis.pdf",
      company: "INFOSYS",
      type: "Annual Report (10-K)",
      year: "FY2023",
      chunks: 15,
      date: "Oct 7, 2026",
      size: "11.3 MB",
      format: "pdf"
    },
    {
      id: "f318fe4a-639c-4fe1-86b1-573887ad394a",
      name: "APPLE_25.pdf",
      company: "relince",
      type: "Annual Report (10-K)",
      year: "FY2025",
      chunks: 216,
      date: "Oct 7, 2026",
      size: "1.8 MB",
      format: "pdf"
    },
    {
      id: "0532f246-9e03-4f4b-bb71-0d49ce12fbd6",
      name: "Amazon_23.pdf",
      company: "reliace",
      type: "Annual Report (10-K)",
      year: "FY2023",
      chunks: 205,
      date: "Oct 7, 2026",
      size: "1.3 MB",
      format: "pdf"
    },
    {
      id: "9ea2a261-8881-4579-af17-6a77733eb24d",
      name: "Infosys_Financial_Report_FY2024.pdf",
      company: "INFOYS",
      type: "Annual Report (10-K)",
      year: "FY2026",
      chunks: 1,
      date: "Oct 6, 2026",
      size: "8.9 MB",
      format: "pdf"
    },
    {
      id: "d458dde5-ee64-4ef0-873c-ba4de2ed3deb",
      name: "Infosys_Annual_Report_FY2023_Finora_Analysis.pdf",
      company: "Infosys",
      type: "Annual Report (10-K)",
      year: "FY2024",
      chunks: 15,
      date: "Sep 20, 2026",
      size: "11.3 MB",
      format: "pdf"
    },
    {
      id: "92ad91d4-5afe-4bc2-bc26-364406af0bbb",
      name: "Infosys_Financial_Report_FY2025.pdf",
      company: "INFOSYS",
      type: "Annual Report (10-K)",
      year: "FY2025",
      chunks: 1,
      date: "Sep 20, 2026",
      size: "7.0 MB",
      format: "pdf"
    },
    {
      id: "6cd5df3f-7fd9-4ed1-bc83-37d51eeb4085",
      name: "Microsoft_24.docx",
      company: "Microsoft",
      type: "Annual Report (10-K)",
      year: "FY2024",
      chunks: 404,
      date: "Sep 19, 2026",
      size: "2.5 MB",
      format: "docx"
    },
    {
      id: "98dd15e6-e9c3-4d33-8808-92753ef90fde",
      name: "AMZN_2023_Annual_Report.txt",
      company: "Amazon.com, Inc. AMZN",
      type: "Annual Report (10-K)",
      year: "FY2023 Pre-loaded",
      chunks: 3,
      date: "Sep 19, 2026",
      size: "450 KB",
      format: "txt"
    },
    {
      id: "0a06231b-4242-4489-b53c-ae9276d08230",
      name: "TSLA_2023_Annual_Report.txt",
      company: "Tesla, Inc. TSLA",
      type: "Annual Report (10-K)",
      year: "FY2023 Pre-loaded",
      chunks: 3,
      date: "Sep 19, 2026",
      size: "380 KB",
      format: "txt"
    },
    {
      id: "416edb60-b8cb-4e4e-a06f-ad23b2c06cff",
      name: "MSFT_2023_Annual_Report.txt",
      company: "Microsoft Corporation MSFT",
      type: "Annual Report (10-K)",
      year: "FY2023 Pre-loaded",
      chunks: 3,
      date: "Sep 19, 2026",
      size: "410 KB",
      format: "txt"
    },
    {
      id: "fb0e2ccc-d162-4851-b7f3-760438faa16a",
      name: "AAPL_2023_Annual_Report.txt",
      company: "Apple Inc. AAPL",
      type: "Annual Report (10-K)",
      year: "FY2023 Pre-loaded",
      chunks: 3,
      date: "Sep 19, 2026",
      size: "520 KB",
      format: "txt"
    }
  ],
  companies: [
    {
      id: "wipro-ltd-fy26-integrated",
      name: "Wipro Limited",
      badge: "WP",
      ticker: "WIPRO",
      sector: "IT Services & Consulting",
      docsCount: 1,
      description: "Global AI-powered information technology, consulting, and business process services company headquartered in Bengaluru. Extracted from Integrated Annual Report 2025-26.",
      revenue: "$11.16B (₹928B)",
      netMargin: "14.22%",
      grossMargin: "29.30%",
      opMargin: "16.30%",
      eps: "₹12.56",
      roe: "14.86%",
      deRatio: "0.19",
      currentRatio: "1.42",
      growth: "+4.17% YoY",
      hasMetrics: true
    },
    {
      id: "df5204fd-100f-413e-b05c-ff481911336a",
      name: "Amazon",
      badge: "Am",
      ticker: "AMZN",
      sector: "E-Commerce & Cloud",
      docsCount: 27,
      description: "Global e-commerce marketplace and AWS cloud computing infrastructure leader.",
      revenue: "$705.00B",
      netMargin: "9.40%",
      grossMargin: "47.40%",
      opMargin: "11.10%",
      eps: "$6.10",
      roe: "19.70%",
      deRatio: "0.36",
      currentRatio: "1.07",
      growth: "+10.5% YoY",
      hasMetrics: true
    },
    {
      id: "bd69a0f1-a99a-446c-aa43-9eb815e7685c",
      name: "Amazon.com, Inc.",
      badge: "AM",
      ticker: "AMZN",
      sector: "Technology",
      docsCount: 12,
      description: "Amazon.com, Inc. engages in the retail sale of consumer products and subscriptions through online and physical stores.",
      revenue: "$574.78B",
      netMargin: "5.29%",
      grossMargin: "46.99%",
      opMargin: "6.41%",
      eps: "$2.90",
      roe: "15.07%",
      deRatio: "0.29",
      currentRatio: "1.13",
      growth: "+11.8% YoY",
      hasMetrics: true
    },
    {
      id: "2f8064c1-4a42-4947-a423-b6c7fdfa4a0f",
      name: "Apple Inc.",
      badge: "AA",
      ticker: "AAPL",
      sector: "Technology",
      docsCount: 13,
      description: "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
      revenue: "$394.33B",
      netMargin: "24.60%",
      grossMargin: "42.90%",
      opMargin: "29.00%",
      eps: "$6.13",
      roe: "156.08%",
      deRatio: "1.53",
      currentRatio: "0.99",
      growth: "-0.3% YoY",
      hasMetrics: true
    },
    {
      id: "bc660065-695b-4f11-aa02-1375e669fab5",
      name: "INFOSYS",
      badge: "IN",
      ticker: "INFY",
      sector: "IT Services",
      docsCount: 20,
      description: "Global consulting and next-generation digital technology services provider.",
      revenue: "$0",
      netMargin: "N/A",
      grossMargin: "N/A",
      opMargin: "N/A",
      eps: "N/A",
      roe: "N/A",
      deRatio: "N/A",
      currentRatio: "N/A",
      growth: "+0.0% YoY",
      hasMetrics: true
    },
    {
      id: "53cd9844-53e4-46f0-9fbf-56e80db393df",
      name: "INFOYS",
      badge: "IN",
      ticker: "INFOYS",
      sector: "Technology",
      docsCount: 10,
      description: "Infosys technology consulting and digital transformation services subsidiary.",
      revenue: "$0",
      netMargin: "N/A",
      grossMargin: "N/A",
      opMargin: "N/A",
      eps: "N/A",
      roe: "N/A",
      deRatio: "N/A",
      currentRatio: "N/A",
      growth: "+0.0% YoY",
      hasMetrics: true
    },
    {
      id: "9736f31b-3f89-45e0-88a7-d231950bac9d",
      name: "Infosys",
      badge: "In",
      ticker: "INFY",
      sector: "IT Services",
      docsCount: 11,
      description: "Infosys Limited is an Indian multinational information technology company providing business consulting and IT.",
      revenue: "$0",
      netMargin: "N/A",
      grossMargin: "N/A",
      opMargin: "N/A",
      eps: "N/A",
      roe: "N/A",
      deRatio: "N/A",
      currentRatio: "N/A",
      growth: "+15.4% YoY",
      hasMetrics: true
    },
    {
      id: "dde770ea-07de-407c-a297-e12035036de9",
      name: "Microsoft",
      badge: "Mi",
      ticker: "MSFT",
      sector: "Software & Cloud",
      docsCount: 22,
      description: "Global technology corporation providing Windows, Office 365, Azure, and enterprise productivity software.",
      revenue: "$211.91B",
      netMargin: "34.10%",
      grossMargin: "68.90%",
      opMargin: "41.80%",
      eps: "$9.68",
      roe: "35.10%",
      deRatio: "0.39",
      currentRatio: "1.77",
      growth: "+6.9% YoY",
      hasMetrics: true
    },
    {
      id: "4655ef25-518b-4adf-a037-317193fa64f9",
      name: "Microsoft Corporation",
      badge: "MS",
      ticker: "MSFT",
      sector: "Technology",
      docsCount: 12,
      description: "Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide.",
      revenue: "$211.91B",
      netMargin: "34.14%",
      grossMargin: "68.90%",
      opMargin: "41.80%",
      eps: "$9.72",
      roe: "35.09%",
      deRatio: "0.20",
      currentRatio: "1.77",
      growth: "+6.9% YoY",
      hasMetrics: true
    },
    {
      id: "3f9510a8-fd06-4b1a-9d07-4e138a7c7ee2",
      name: "TCS",
      badge: "TC",
      ticker: "TCS",
      sector: "IT Consulting",
      docsCount: 15,
      description: "Tata Consultancy Services is an Indian multinational IT services and consulting company headquartered in Mumbai.",
      revenue: "$31.40B",
      netMargin: "22.50%",
      grossMargin: "30.00%",
      opMargin: "23.50%",
      eps: "$1.95",
      roe: "44.50%",
      deRatio: "0.03",
      currentRatio: "2.30",
      growth: "+4.3% YoY",
      hasMetrics: true
    },
    {
      id: "06de592b-e084-4136-bc71-e26f721c9612",
      name: "Tesla",
      badge: "Te",
      ticker: "TSLA",
      sector: "Automotive & Energy",
      docsCount: 26,
      description: "Electric vehicle design, energy storage manufacturing, and solar roof development.",
      revenue: "$88.00B",
      netMargin: "0.60%",
      grossMargin: "13.80%",
      opMargin: "1.00%",
      eps: "$0.15",
      roe: "1.10%",
      deRatio: "0.36",
      currentRatio: "0.95",
      growth: "-4.3% YoY",
      hasMetrics: true
    },
    {
      id: "ee60145a-4a93-4666-be28-3158c8230b79",
      name: "Tesla, Inc.",
      badge: "TS",
      ticker: "TSLA",
      sector: "Automotive",
      docsCount: 13,
      description: "Tesla, Inc. designs, develops, manufactures, leases, and sells electric vehicles, energy generation and storage systems.",
      revenue: "$96.77B",
      netMargin: "15.50%",
      grossMargin: "18.26%",
      opMargin: "9.19%",
      eps: "$3.53",
      roe: "23.95%",
      deRatio: "0.05",
      currentRatio: "1.73",
      growth: "+18.8% YoY",
      hasMetrics: true
    },
    {
      id: "0440672a-203c-4fc4-be16-35724dd07581",
      name: "reliace",
      badge: "re",
      ticker: "RELIANCE",
      sector: "Conglomerate",
      docsCount: 12,
      description: "Reliance Industries energy, petrochemicals, telecommunications and retail conglomerate.",
      revenue: "$0",
      netMargin: "N/A",
      grossMargin: "N/A",
      opMargin: "N/A",
      eps: "N/A",
      roe: "N/A",
      deRatio: "N/A",
      currentRatio: "N/A",
      growth: "+0.0% YoY",
      hasMetrics: true
    },
    {
      id: "1085e037-d7eb-4979-b78d-bab76c2863f0",
      name: "reliance",
      badge: "re",
      ticker: "RELIANCE",
      sector: "Diversified",
      docsCount: 10,
      description: "Reliance corporate group operations across refining, retail, and Jio digital services.",
      revenue: "$0",
      netMargin: "N/A",
      grossMargin: "N/A",
      opMargin: "N/A",
      eps: "N/A",
      roe: "N/A",
      deRatio: "N/A",
      currentRatio: "N/A",
      growth: "+0.0% YoY",
      hasMetrics: true
    },
    {
      id: "6b8b7fff-1d4c-428e-92b4-8a0ef8fe1b56",
      name: "relince",
      badge: "re",
      ticker: "RELIANCE",
      sector: "Holding",
      docsCount: 10,
      description: "Reliance group filing and subsidiary holdings.",
      revenue: "$0",
      netMargin: "N/A",
      grossMargin: "N/A",
      opMargin: "N/A",
      eps: "N/A",
      roe: "N/A",
      deRatio: "N/A",
      currentRatio: "N/A",
      growth: "+0.0% YoY",
      hasMetrics: false
    }
  ],
  metricsTable: [
    { company: "Wipro Limited", ticker: "WIPRO", revenue: "$11.16B (₹928B)", revNum: 11160, ebitda: 2180, growth: "+4.17%", grossMargin: "29.30%", opMargin: "16.30%", netMargin: "14.22%", currentRatio: "1.42", de: "0.19", roe: "14.86%", eps: "₹12.56" },
    { company: "Apple Inc.", ticker: "AAPL", revenue: "$394.33B", revNum: 394330, ebitda: 123000, growth: "-0.3%", grossMargin: "42.90%", opMargin: "29.00%", netMargin: "24.60%", currentRatio: "0.99", de: "1.53", roe: "156.08%", eps: "$6.13" },
    { company: "Microsoft Corporation", ticker: "MSFT", revenue: "$211.91B", revNum: 211910, ebitda: 88500, growth: "+6.9%", grossMargin: "68.90%", opMargin: "41.80%", netMargin: "34.14%", currentRatio: "1.77", de: "0.20", roe: "35.09%", eps: "$9.72" },
    { company: "Tesla, Inc.", ticker: "TSLA", revenue: "$96.77B", revNum: 96770, ebitda: 14200, growth: "+18.8%", grossMargin: "18.26%", opMargin: "9.19%", netMargin: "15.50%", currentRatio: "1.73", de: "0.05", roe: "23.95%", eps: "$3.53" },
    { company: "Amazon.com, Inc.", ticker: "AMZN", revenue: "$574.78B", revNum: 574780, ebitda: 85500, growth: "+11.8%", grossMargin: "46.99%", opMargin: "6.41%", netMargin: "5.29%", currentRatio: "1.13", de: "0.29", roe: "15.07%", eps: "$2.90" },
    { company: "Amazon", ticker: "AMZN", revenue: "$705.00B", revNum: 705000, ebitda: 104000, growth: "+10.5%", grossMargin: "47.40%", opMargin: "11.10%", netMargin: "9.40%", currentRatio: "1.07", de: "0.36", roe: "19.70%", eps: "$6.10" },
    { company: "Tesla", ticker: "TSLA", revenue: "$88.00B", revNum: 88000, ebitda: 7200, growth: "-4.3%", grossMargin: "13.80%", opMargin: "1.00%", netMargin: "0.60%", currentRatio: "0.95", de: "0.36", roe: "1.10%", eps: "$0.15" },
    { company: "Microsoft", ticker: "MSFT", revenue: "$211.91B", revNum: 211910, ebitda: 88500, growth: "+6.9%", grossMargin: "68.90%", opMargin: "41.80%", netMargin: "34.10%", currentRatio: "1.77", de: "0.39", roe: "35.10%", eps: "$9.68" },
    { company: "TCS", ticker: "TCS", revenue: "$31.40B", revNum: 31400, ebitda: 8160, growth: "+4.3%", grossMargin: "30.00%", opMargin: "23.50%", netMargin: "22.50%", currentRatio: "2.30", de: "0.03", roe: "44.50%", eps: "$1.95" },
    { company: "Consolidated Tech", ticker: "N/A", revenue: "$128.00B", revNum: 128000, ebitda: 28000, growth: "+4.9%", grossMargin: "31.30%", opMargin: "13.60%", netMargin: "7.90%", currentRatio: "1.00", de: "0.64", roe: "10.50%", eps: "$7.45" },
    { company: "Infosys", ticker: "INFY", revenue: "$0", revNum: 0, ebitda: 0, growth: "+15.4%", grossMargin: "N/A", opMargin: "N/A", netMargin: "N/A", currentRatio: "N/A", de: "N/A", roe: "N/A", eps: "N/A" },
    { company: "INFOSYS", ticker: "INFY", revenue: "$0", revNum: 0, ebitda: 0, growth: "+0.0%", grossMargin: "N/A", opMargin: "N/A", netMargin: "N/A", currentRatio: "N/A", de: "N/A", roe: "N/A", eps: "N/A" },
    { company: "reliance", ticker: "RELIANCE", revenue: "$0", revNum: 0, ebitda: 0, growth: "+0.0%", grossMargin: "N/A", opMargin: "N/A", netMargin: "N/A", currentRatio: "N/A", de: "N/A", roe: "N/A", eps: "N/A" },
    { company: "reliace", ticker: "RELIANCE", revenue: "$0", revNum: 0, ebitda: 0, growth: "+0.0%", grossMargin: "N/A", opMargin: "N/A", netMargin: "N/A", currentRatio: "N/A", de: "N/A", roe: "N/A", eps: "N/A" }
  ],
  radarData: {
    labels: ["Gross Margin", "Op Margin", "Net Margin", "ROE", "Current Ratio"],
    companies: {
      "Apple Inc.": [42.9, 29.0, 24.6, 95.0, 19.8],
      "Microsoft Corporation": [68.9, 41.8, 34.1, 35.1, 35.4],
      "Tesla, Inc.": [18.3, 9.2, 15.5, 23.9, 34.6],
      "Amazon.com, Inc.": [47.0, 6.4, 5.3, 15.1, 22.6],
      "TCS": [30.0, 23.5, 22.5, 44.5, 46.0],
      "Wipro Limited": [29.3, 16.3, 14.2, 14.9, 14.2]
    }
  },
  risks: [
    {
      id: "risk-wipro-1",
      severity: "high",
      type: "Margin Risk",
      company: "Wipro Limited (WIPRO)",
      title: "Discretionary IT Spending Slowdown (Americas 2)",
      description: "Client discretionary budget delays from macroeconomic challenges and geopolitical friction compressed operating margin by 68 bps from 16.98% to 16.30%, with contraction observed in Americas 2 vertical.",
      evidence: "Operating margin decreased by 68 bps from 16.98% to 16.30%... revenue from Americas 2 declined due to discretionary spending cuts.",
      recommendation: "Accelerate Wipro Intelligence AI-led deals and cost rationalization to defend margins above 16.5%."
    },
    {
      id: "risk-wipro-2",
      severity: "medium",
      type: "Market Risk",
      company: "Wipro Limited (WIPRO)",
      title: "Foreign Currency Cross-Rate Volatility",
      description: "Over 85% of revenue originates in USD, EUR, GBP, and AUD. Exchange rate swings directly influence reported operational results and margin predictability.",
      evidence: "Growth was driven by depreciation of INR against major foreign currencies... exposed to cross-currency movements.",
      recommendation: "Maintain systematic forward hedging coverage for near-term foreign currency operational cash flows."
    },
    {
      id: "risk-wipro-3",
      severity: "medium",
      type: "Operational Risk",
      company: "Wipro Limited (WIPRO)",
      title: "Client Concentration in Top 5 Accounts (14.3%)",
      description: "Top 5 enterprise clients represent 14.3% of total IT Services revenues, with the single largest anchor client contributing 4.6% of IT Services turnover.",
      evidence: "Largest client accounted for 4.6% of revenues; top five clients accounted for 14.3% of IT Services revenues in FY26.",
      recommendation: "Deepen relationships across mid-tier accounts ($5M-$50M bucket) to reduce revenue vulnerability from single-client budget cycles."
    },
    {
      id: "risk-1",
      severity: "critical",
      type: "Margin Risk",
      company: "Tesla, Inc. (TSLA)",
      title: "Gross Margin Compression (28.5% → 18.2%)",
      description: "Tesla's automotive gross margin declined dramatically from 28.5% to 18.1% in 2023 due to aggressive price cuts, new factory ramp costs, and rising material costs. This is a critical red flag requiring immediate attention.",
      evidence: "Gross profit: $17,660 million (gross margin 18.2%, down from 25.6%)",
      recommendation: "Critical watch item. Monitor Q4 2023 and 2024 margins closely. Price cuts may not be sustainable."
    },
    {
      id: "risk-2",
      severity: "critical",
      type: "Regulatory Risk",
      company: "Amazon.com, Inc. (AMZN)",
      title: "FTC Antitrust Lawsuit — Monopoly Allegations",
      description: "The FTC filed suit against Amazon alleging illegal monopoly maintenance in online marketplace operations. A successful prosecution could force fundamental business model changes.",
      evidence: "The FTC filed suit against Amazon alleging illegal monopoly maintenance. Potential regulatory action could force business model changes",
      recommendation: "Monitor litigation progress; assess potential impact on third-party seller practices."
    },
    {
      id: "risk-3",
      severity: "critical",
      type: "Market Risk",
      company: "Amazon",
      title: "Exposure to litigation and regulatory investigations",
      description: "Ongoing and potential class action lawsuits and regulatory probes could result in significant costs and adverse outcomes.",
      evidence: "Litigation and regulatory investigations, including class action lawsuits relating to product and commercial matters, could result in significant costs and adverse outcomes.",
      recommendation: "Allocate sufficient legal reserves, strengthen compliance programs, and proactively engage with regulators."
    },
    {
      id: "risk-4",
      severity: "critical",
      type: "Liquidity Risk",
      company: "Amazon",
      title: "High debt level relative to cash holdings",
      description: "The company holds $95,000 million in cash and equivalents but carries $122,000 million of total debt, indicating leverage that could strain liquidity under adverse conditions.",
      evidence: "Cash and equivalents were $95,000 million at the end of fiscal year, and total debt stood at $122,000 million.",
      recommendation: "Implement a debt reduction strategy, improve cash flow forecasting, and maintain access to committed credit facilities."
    },
    {
      id: "risk-5",
      severity: "critical",
      type: "Auditor Qualification",
      company: "Tesla",
      title: "Auditor opinion qualification disclosed",
      description: "The document contains explicit qualified, adverse, disclaimer, or except-for audit opinion language. The stated limitation should be reviewed with the auditor's report.",
      evidence: "issued a qualified audit opinion with respect to these matters. The company is currently in breach of a debt",
      recommendation: "Review the auditor's opinion, basis for qualification, affected balances, and remediation plan with a qualified professional."
    },
    {
      id: "risk-6",
      severity: "critical",
      type: "Going Concern",
      company: "Tesla",
      title: "Going-concern disclosure present",
      description: "The source document contains going-concern language. This is a material disclosure to assess in its full context; mention alone does not determine the company's current viability.",
      evidence: "substantial doubt about the company's ability to continue as a going concern, and the independent auditors",
      recommendation: "Review the exact disclosure, liquidity forecasts, management plans, and auditor conclusion."
    },
    {
      id: "risk-7",
      severity: "high",
      type: "Geographic Concentration Risk",
      company: "Apple Inc. (AAPL)",
      title: "China Revenue Dependency (~19% of Sales)",
      description: "Apple generates approximately 19% of total net sales from China, creating significant exposure to geopolitical tensions, trade wars, and Chinese regulatory actions that could impair market access.",
      evidence: "Revenue generated from China accounted for approximately 19% of total net sales in 2023",
      recommendation: "Monitor geopolitical developments; diversify manufacturing to India and Vietnam as strategic hedge."
    },
    {
      id: "risk-8",
      severity: "high",
      type: "Market Risk",
      company: "Microsoft Corporation (MSFT)",
      title: "AI Infrastructure Investment Uncertainty",
      description: "Microsoft has committed tens of billions to AI infrastructure and OpenAI partnership. These investments create significant execution risk and uncertainty about return on capital.",
      evidence: "Microsoft has committed significant capital to AI infrastructure, including its multi-billion dollar investment in OpenAI",
      recommendation: "Track Azure AI revenue growth as leading indicator of ROI; monitor capex-to-revenue ratio quarterly."
    },
    {
      id: "risk-9",
      severity: "high",
      type: "Revenue Risk",
      company: "Tesla, Inc. (TSLA)",
      title: "Intensifying EV Competition from BYD",
      description: "Chinese manufacturer BYD surpassed Tesla in quarterly EV deliveries in Q4 2023, signaling a fundamental shift in competitive dynamics. Tesla's premium positioning is under threat.",
      evidence: "Chinese competitor BYD surpassed Tesla in quarterly deliveries in Q4 2023",
      recommendation: "Monitor pricing strategy and market share trends; evaluate next-gen affordable vehicle timeline."
    },
    {
      id: "risk-10",
      severity: "high",
      type: "Operational Risk",
      company: "Tesla, Inc. (TSLA)",
      title: "Simultaneous Multi-Product Launch Risk",
      description: "Tesla is managing Cybertruck launch, Semi production, and next-generation vehicle development simultaneously, creating significant execution risk across operations.",
      evidence: "Tesla is simultaneously managing multiple major product launches including the Cybertruck, Semi, and next-generation affordable vehicle",
      recommendation: "Track Cybertruck delivery rates and gross margin contribution quarterly."
    },
    {
      id: "risk-11",
      severity: "high",
      type: "Market Risk",
      company: "Infosys",
      title: "Execution risk of extensive digital, AI and ESG investments",
      description: "The filing highlights “continuing investment in digital capabilities, talent, AI, cybersecurity, and ESG,” indicating substantial capital allocation that may not deliver expected returns if execution falters.",
      evidence: "continuing investment in digital capabilities, talent, AI, cybersecurity, and ESG",
      recommendation: "Implement rigorous project governance, milestone tracking, and risk-adjusted budgeting for each strategic initiative."
    },
    {
      id: "risk-12",
      severity: "high",
      type: "Market Risk",
      company: "Global Equities",
      title: "Exposure to adverse macroeconomic conditions",
      description: "The company's results and stock price are vulnerable to slow growth, recession, high unemployment, inflation, tighter credit, higher interest rates, and currency fluctuations.",
      evidence: "Adverse macroeconomic conditions, including slow growth or recession, high unemployment, inflation, tighter credit, higher interest rates, and currency fluctuations.",
      recommendation: "Implement macroeconomic scenario planning, diversify revenue streams across regions, and consider hedging strategies for currency exposure."
    },
    {
      id: "risk-13",
      severity: "high",
      type: "Market Risk",
      company: "Global Supply Chain",
      title: "Risk of supply chain interruptions",
      description: "Supplier facilities and retail stores face interruption risks from fire, power shortages, nuclear accidents, terrorist attacks, ransomware, labor disputes, public health issues, and other events beyond control.",
      evidence: "suppliers’ operations, retail stores and facilities are subject to the risk of interruption by fire, power shortages, nuclear power plant accidents and other industrial accidents, terrorist attacks...",
      recommendation: "Develop multi-sourcing strategies, increase inventory buffers for critical components, and enhance cybersecurity and business continuity plans."
    },
    {
      id: "risk-14",
      severity: "high",
      type: "Regulatory Risk",
      company: "reliace",
      title: "Exposure to Foreign Regulatory Changes",
      description: "The company operates in jurisdictions such as China and India where regulatory restrictions on ownership, licensing, and cybersecurity could lead to fines, loss of licenses, or shutdown.",
      evidence: "Violation of any existing or future PRC, Indian, or other laws or regulations or changes in the interpretations of those laws could result in businesses being subject to fines...",
      recommendation: "Implement a robust monitoring program for regulatory developments in key foreign markets, establish contingency plans for operational restructuring."
    },
    {
      id: "risk-15",
      severity: "high",
      type: "Regulatory Risk",
      company: "Amazon",
      title: "Potential increase in compliance costs due to trade regulations",
      description: "The company may face higher compliance expenses if new or existing trade regulations become more stringent, impacting margins.",
      evidence: "trade regulations, could increase compliance costs.",
      recommendation: "Monitor regulatory developments and build a compliance cost reserve; consider diversifying supply chain to mitigate exposure."
    },
    {
      id: "risk-16",
      severity: "high",
      type: "Market Risk",
      company: "Amazon",
      title: "Dependence on limited key suppliers and contract manufacturers",
      description: "Reliance on a small number of suppliers creates vulnerability to disruptions that could delay product shipments and affect revenue.",
      evidence: "The company depends on a limited number of key suppliers and contract manufacturers; disruption could delay product shipments.",
      recommendation: "Develop secondary supplier relationships and increase inventory buffers for critical components."
    },
    {
      id: "risk-17",
      severity: "high",
      type: "Market Risk",
      company: "Amazon",
      title: "Risk of cybersecurity incidents or service outages",
      description: "Cyber attacks or outages could damage customer trust and the company's reputation, leading to loss of business.",
      evidence: "Cybersecurity incidents or service outages could harm customers and reputation.",
      recommendation: "Enhance security monitoring, conduct regular penetration testing, and maintain an incident response plan."
    },
    {
      id: "risk-18",
      severity: "high",
      type: "Accounting Control Risk",
      company: "Tesla",
      title: "Accounting or internal-control issue disclosed",
      description: "The source text contains explicit accounting-control, restatement, non-reliance, or financial-reporting concern language.",
      evidence: "During fiscal year 2026 the company identified a material weakness in internal control over financial reporting",
      recommendation: "Review the related filing, auditor discussion, restatement scope, and control remediation disclosures."
    },
    {
      id: "risk-19",
      severity: "high",
      type: "Liquidity Risk",
      company: "Tesla",
      title: "Explicit liquidity, covenant, or default warning",
      description: "The document contains explicit language about a covenant breach, debt default, liquidity shortfall, or inability to meet obligations.",
      evidence: "issued a qualified audit opinion with respect to these matters. The company is currently in breach of a debt covenant under its revolving credit facility and is negotiating amendments...",
      recommendation: "Review maturity schedules, covenant headroom, available facilities, and management's remediation plan."
    },
    {
      id: "risk-20",
      severity: "high",
      type: "Market Risk",
      company: "Microsoft",
      title: "Dependence on limited key suppliers",
      description: "The company relies on a limited number of key suppliers and contract manufacturers; any disruption could delay product shipments, impacting revenue and operations.",
      evidence: "depends on a limited number of key suppliers and contract manufacturers; disruption could delay product shipments.",
      recommendation: "Diversify the supplier base and develop contingency plans for alternative sourcing."
    },
    {
      id: "risk-21",
      severity: "high",
      type: "Market Risk",
      company: "Microsoft",
      title: "Potential cyber incidents and service outages",
      description: "Cybersecurity incidents or service outages could harm customers and the company's reputation, leading to loss of business and legal exposure.",
      evidence: "Cybersecurity incidents or service outages could harm customers and reputation.",
      recommendation: "Implement robust cybersecurity controls, regular penetration testing, and incident response procedures."
    },
    {
      id: "risk-22",
      severity: "high",
      type: "Market Risk",
      company: "TCS",
      title: "Increased compliance costs from trade regulations",
      description: "The company may face higher compliance expenses as new or existing trade regulations impose additional requirements, potentially affecting profitability.",
      evidence: "trade regulations, could increase compliance costs",
      recommendation: "Implement a regulatory monitoring program and allocate budget for compliance initiatives to mitigate cost impacts."
    },
    {
      id: "risk-23",
      severity: "high",
      type: "Market Risk",
      company: "TCS",
      title: "Dependence on limited key suppliers",
      description: "Reliance on a small number of suppliers and contract manufacturers creates vulnerability to disruptions that could delay product shipments.",
      evidence: "depends on a limited number of key suppliers and contract manufacturers; disruption could delay product shipments",
      recommendation: "Develop alternative sourcing strategies and maintain safety stock to reduce exposure to supplier disruptions."
    },
    {
      id: "risk-24",
      severity: "high",
      type: "Market Risk",
      company: "TCS",
      title: "Potential cybersecurity incidents or service outages",
      description: "Cyber attacks or service interruptions could damage customer trust and the company's reputation, leading to financial and operational harm.",
      evidence: "Cybersecurity incidents or service outages could harm customers and reputation",
      recommendation: "Enhance security controls, conduct regular penetration testing, and establish an incident response plan."
    },
    {
      id: "risk-25",
      severity: "high",
      type: "Market Risk",
      company: "TCS",
      title: "Litigation and regulatory investigations",
      description: "Ongoing and potential class action lawsuits and regulatory probes could result in significant costs and adverse outcomes for the company.",
      evidence: "Litigation and regulatory investigations, including class action lawsuits relating to product and commercial matters, could result in significant costs and adverse outcomes",
      recommendation: "Set aside reserves for legal contingencies and strengthen compliance and product quality oversight."
    },
    {
      id: "risk-26",
      severity: "high",
      type: "Market Risk",
      company: "Cross-Industry",
      title: "Dependence on Limited Key Suppliers",
      description: "The company relies on a limited number of key suppliers and contract manufacturers, making it vulnerable to disruptions that could delay product shipments.",
      evidence: "limited number of key suppliers and contract manufacturers; disruption could delay product shipments",
      recommendation: "Develop a diversified supplier base, establish backup contracts, and create contingency plans for supply chain interruptions."
    },
    {
      id: "risk-27",
      severity: "high",
      type: "Market Risk",
      company: "Cross-Industry",
      title: "Potential Cybersecurity Incidents and Service Outages",
      description: "Cybersecurity incidents or service outages could harm customers and damage the company's reputation, leading to loss of business and possible regulatory scrutiny.",
      evidence: "Cybersecurity incidents or service outages could harm customers and reputation",
      recommendation: "Invest in robust cybersecurity controls, regular penetration testing, and an incident-response plan to mitigate and quickly address breaches."
    },
    {
      id: "risk-28",
      severity: "medium",
      type: "Revenue Risk",
      company: "Apple Inc. (AAPL)",
      title: "iPhone Revenue Stagnation",
      description: "iPhone revenue declined 2% in 2023 amid macroeconomic headwinds and market saturation in key markets. With iPhone comprising 52% of revenues, any sustained decline poses material risk.",
      evidence: "iPhone net sales: $205,489 million (52.0% of total net sales)",
      recommendation: "Watch Services segment growth as offset; track iPhone upgrade cycles carefully."
    },
    {
      id: "risk-29",
      severity: "medium",
      type: "Liquidity Risk",
      company: "Apple Inc. (AAPL)",
      title: "Current Ratio Below 1.0x",
      description: "Apple's current ratio of 0.99x indicates current liabilities exceed current assets, though this is actively managed through commercial paper programs and strong operating cash flows.",
      evidence: "Total current assets: $143,566 million; Total current liabilities: $145,308 million",
      recommendation: "Not immediately concerning given $114B operating cash flow; monitor if cash position deteriorates."
    },
    {
      id: "risk-30",
      severity: "medium",
      type: "Regulatory Risk",
      company: "Microsoft Corporation (MSFT)",
      title: "Antitrust Scrutiny Post-Activision",
      description: "Following the $69 billion Activision Blizzard acquisition, Microsoft faces ongoing regulatory scrutiny in the EU and US that could restrict future M&A activities and business practices.",
      evidence: "Microsoft is subject to increasingly burdensome regulations globally, including antitrust scrutiny following the Activision Blizzard acquisition",
      recommendation: "Monitor regulatory outcomes; evaluate integration execution and gaming segment performance."
    },
    {
      id: "risk-31",
      severity: "medium",
      type: "Revenue Risk",
      company: "Amazon.com, Inc. (AMZN)",
      title: "International Segment Ongoing Losses",
      description: "Amazon's international segment generated operating losses of $(2,656) million in 2023, representing a long-running drag on consolidated profitability requiring substantial ongoing investment.",
      evidence: "International operating loss: $(2,656) million (improving from $(7,746) million in 2022)",
      recommendation: "Track path to international profitability; evaluate market-specific investment thesis."
    },
    {
      id: "risk-32",
      severity: "medium",
      type: "Market Risk",
      company: "Cross-Industry",
      title: "Potential product liability and warranty claims",
      description: "The company may incur costs from product liability claims, recalls, replacements, warranty expenses, litigation, and regulatory fines.",
      evidence: "product liability claims, recalls, product replacements or modifications, write-offs of inventory, property, plant and equipment...",
      recommendation: "Strengthen quality assurance processes, maintain robust product testing, and set aside adequate reserves for potential liability and warranty expenses."
    },
    {
      id: "risk-33",
      severity: "medium",
      type: "Operational Risk",
      company: "reliace",
      title: "Demand Volatility Impacting Fulfillment and Data Centers",
      description: "Significant fluctuations in product and service demand due to seasonality or economic events can strain fulfillment and data center capacity, leading to higher costs.",
      evidence: "Demand for our products and services can fluctuate significantly for many reasons, including as a result of seasonality, promotions...",
      recommendation: "Enhance demand forecasting models, increase flexibility in inventory and staffing, and invest in scalable infrastructure."
    },
    {
      id: "risk-34",
      severity: "medium",
      type: "Operational Risk",
      company: "Amazon",
      title: "Demand Variability Impacting Fulfillment and Data Center Capacity",
      description: "Fluctuations in customer demand can lead to excess or insufficient fulfillment capacity, causing service interruptions and cost overruns.",
      evidence: "result in excess or insufficient fulfillment or data center capacity, service interruptions, increased costs, and impairment charges...",
      recommendation: "Invest in advanced demand-forecasting analytics, flexible staffing models, and scalable infrastructure."
    },
    {
      id: "risk-35",
      severity: "medium",
      type: "Liquidity Risk",
      company: "Amazon",
      title: "Significant Lease and Financing Obligations",
      description: "The company reported lease and financing obligations of $20.7 billion and $53.0 billion, representing substantial liabilities that could strain cash flows.",
      evidence: "leases, and financing obligations of $20.7 billion and $53.0 billion in 2021 and 2022.",
      recommendation: "Conduct a detailed cash-flow stress test incorporating lease payments and maintain adequate liquidity buffers."
    },
    {
      id: "risk-36",
      severity: "medium",
      type: "Market Risk",
      company: "Tesla",
      title: "Foreign exchange rate volatility",
      description: "Fluctuations in foreign currency exchange rates could materially affect the company's reported results, impacting earnings and cash flow.",
      evidence: "Fluctuations in foreign currency exchange rates may materially affect reported results.",
      recommendation: "Implement hedging strategies and monitor currency exposure to mitigate impact on financial performance."
    },
    {
      id: "risk-37",
      severity: "medium",
      type: "Market Risk",
      company: "Tesla",
      title: "Potential increase in compliance costs",
      description: "Regulatory changes, including data privacy, environmental, and trade regulations, could raise compliance costs and affect profitability.",
      evidence: "Regulatory changes, including data privacy, environmental, and trade regulations, could increase compliance costs.",
      recommendation: "Enhance regulatory monitoring and allocate resources for compliance programs."
    },
    {
      id: "risk-38",
      severity: "medium",
      type: "Market Risk",
      company: "TCS",
      title: "High customer concentration in certain segments",
      description: "A concentration of sales in specific customer segments could amplify the impact of demand fluctuations, affecting overall performance.",
      evidence: "Customer concentration in certain segments may amplify the effect of demand changes",
      recommendation: "Diversify the customer base across additional segments and geographies to reduce reliance on any single group."
    },
    {
      id: "risk-39",
      severity: "medium",
      type: "Market Risk",
      company: "Sector Peer",
      title: "High Dependence on Certain Customer Segments",
      description: "Customer concentration in specific segments may amplify the impact of demand fluctuations, increasing earnings volatility.",
      evidence: "Customer concentration in certain segments may amplify the effect of demand changes",
      recommendation: "Monitor segment exposure, pursue diversification of the customer base, and adjust sales strategies."
    },
    {
      id: "risk-40",
      severity: "medium",
      type: "Market Risk",
      company: "International Trade",
      title: "Increasing Trade Regulation Costs",
      description: "Changes in trade regulations could raise compliance costs, affecting margins and operational efficiency.",
      evidence: "trade regulations, could increase compliance costs",
      recommendation: "Implement a regulatory monitoring function, allocate resources for compliance, and engage with policymakers."
    }
  ],
  reports: [
    {
      id: "rep-wipro-fy26-integrated",
      company: "Wipro Limited",
      title: "Integrated Performance Analysis — Wipro Limited (FY2025-26)",
      status: "completed",
      date: "Oct 12, 2026",
      recommendation: "Hold / Accumulate",
      summary: "Wipro Limited demonstrated steady operational resilience in FY2025-26, reporting ₹928,093 Million ($11.16B) in gross revenue (+4.17% YoY) and ₹131,974 Million ($1.59B) in net profit (net margin 14.22%). Operating income was ₹151,251 Million with an operating margin of 16.30%. The balance sheet is exceptionally well-capitalized with a net worth of ₹887,877 Million, gross cash of ₹551,809 Million, and a low debt-to-equity ratio of 0.19, providing a net cash surplus of ₹383,935 Million (~$4.6B). Diluted EPS reached ₹12.56 with an ROE of 14.86%. Recommendation: Hold / Accumulate given fortress balance sheet liquidity and expanding AI-led pipeline.",
      source: "Integrated-annual-report-2025-26.pdf"
    },
    {
      id: "e566bc90-f64a-43f7-a2c7-10ea3abcc6ae",
      company: "TCS",
      title: "Financial Analysis Report — TCS",
      status: "completed",
      date: "Oct 10, 2026",
      recommendation: "Buy",
      summary: "Tata Consultancy Services (TCS) delivered a solid FY 2026 performance, posting **$31.4 bn** of revenue—a **4.3%** year-over-year increase—while maintaining high profitability. Net income rose to **$7.05 bn** (net margin **22.5%**) and EBITDA reached **$8.16 bn** (EBITDA margin **26.0%**). The balance sheet remains exceptionally strong, with a **debt-to-equity ratio of 0.03**, a **current and quick ratio of 2.30**, and **$6.75 bn** of free cash flow, underscoring ample liquidity and low financial risk. Despite the robust fundamentals, the company faces several material risks. High customer concentration in specific segments, reliance on a limited set of key suppliers, and exposure to cybersecurity incidents could pressure revenue stability and margins. Additionally, tightening trade regulations may increase compliance costs, eroding profitability. These headwinds are offset by the firm's high return metrics—**ROE 44.5%** and **ROA 30.3%**—and a modest valuation of **P/E 24.8x**, suggesting upside potential if risk mitigation is successful. **Recommendation: Buy** – the combination of strong cash generation, superior returns on capital, and a reasonable valuation outweighs the identified risks, which management appears positioned to manage through its strong balance sheet and operational discipline.",
      source: "TCS_Annual_Report_FY2026.pdf"
    },
    {
      id: "6faeaaed-cbd9-422b-a140-f3c0eb390213",
      company: "Apple Inc.",
      title: "Financial Analysis Report — AAPL",
      status: "completed",
      date: "Oct 10, 2026",
      recommendation: "Hold / Accumulate",
      summary: "Apple Inc. delivered a solid 2023 fiscal year, posting **$394.3 bn** of revenue and **$96.9 bn** of net income, translating to a net margin of **24.6%**. Operating performance remained robust with an operating margin of **29.0%** and EBITDA margin of **31.2%**, while free cash flow (FCF) reached **$103.2 bn**, underscoring the company's ability to generate cash despite a modest revenue contraction of **-0.26%** year-over-year. Balance-sheet metrics reveal a mixed picture. Apple's total debt stands at **$110 bn**, yielding a debt-to-equity ratio of **1.53×**, and its current ratio slipped to **0.99×**, indicating that current liabilities marginally exceed current assets. Nonetheless, the company's massive cash pile of **$29.97 bn** and strong operating cash flow of **$114.2 bn** provide ample liquidity to service debt and fund ongoing investments. Key risks include a high-severity geographic concentration in China (≈19% of sales), medium-severity iPhone revenue stagnation (iPhone accounts for 52% of revenue and declined 2% YoY), and a medium-severity liquidity pressure reflected in the sub-1.0 current ratio.",
      source: "AAPL_2023_Annual_Report.txt"
    },
    {
      id: "558b896f-c946-4198-a046-beea9d1b1a76",
      company: "Apple Inc.",
      title: "Financial Analysis Report — AAPL",
      status: "completed",
      date: "Oct 9, 2026",
      recommendation: "Neutral",
      summary: "This report is grounded in metrics and risk flags extracted from the selected uploaded documents. Gemini was unavailable, so no unsupported external claims were added. Evaluated balance sheet liquidity, Services segment growth resilience, and supply chain diversification vectors.",
      source: "APPLE_ANNUAL_2024.pdf"
    },
    {
      id: "8e1c13ce-89bc-46f0-a550-230398887491",
      company: "relince",
      title: "Financial Analysis Report — relince",
      status: "completed",
      date: "Oct 9, 2026",
      recommendation: "Watch",
      summary: "This report is grounded in metrics and risk flags extracted from the selected uploaded documents. Evaluates debt service coverage, telecom capital expenditures, and foreign regulatory changes in retail and refining jurisdictions.",
      source: "REALIANCE_ANNUAL_2025.pdf"
    },
    {
      id: "78fe0e5b-b210-41af-8eb3-db006238f7a7",
      company: "Infosys",
      title: "Financial Analysis Report — Infosys",
      status: "completed",
      date: "Oct 6, 2026",
      recommendation: "Accumulate",
      summary: "This report is grounded in metrics and risk flags extracted from the selected uploaded documents. Highlights 15.4% YoY digital constant-currency growth, expanding generative AI client pipeline, and resilient cash flow conversion with zero debt leverage.",
      source: "INFOSYS_ANNUAL_2023.pdf"
    },
    {
      id: "b572fe4e-b1ed-460b-a9c4-d23c8bb175d4",
      company: "Amazon.com, Inc.",
      title: "Financial Analysis Report — AMZN",
      status: "completed",
      date: "Sep 20, 2026",
      recommendation: "Buy",
      summary: "Amazon demonstrated accelerated operating income expansion from $12.2B in 2022 to $36.8B in 2023, powered by AWS operating margins rebound and regional fulfillment network efficiencies. Free cash flow surged back to positive territory at $36.8B.",
      source: "AMZN_2023_Annual_Report.txt"
    }
  ],
  qaKnowledgeBase: [
    {
      keywords: ["top 3", "financial risks", "all loaded companies", "across all"],
      question: "Identify the top 3 financial risks across all loaded companies",
      answer: `Based on automated cross-document audit analysis across 20 indexed filings, the top 3 critical financial risks are:

1. **Severe Gross Margin Compression & Price War Pressures (Tesla & E-commerce)** [S1]
   - Tesla's automotive gross margin plunged from 28.5% down to 18.2% following aggressive price cuts, factory scaling costs, and rising input costs.
   - Amazon continues to absorb high fulfillment costs and ongoing international segment operating losses.

2. **Regulatory & Antitrust Prosecution (Amazon & Apple)** [S2]
   - The US FTC filed landmark antitrust suits alleging illegal monopoly maintenance in marketplace operations.
   - Apple faces intensified European Digital Markets Act investigations and severe geographic concentration in China (~19% of total net sales exposed to trade friction).

3. **Liquidity Structure & Debt Refinancing Vulnerability** [S3] [S4]
   - Amazon maintains $122.0B in total debt against $95.0B in cash reserves with $73.7B in aggregate lease and financing obligations.
   - Apple operates with a sub-1.0x current ratio (0.99x), creating reliance on commercial paper roll-overs despite strong operating cash flows.`,
      sources: [
        { id: "S1", doc: "Tesla_Annual_Report_FY2026.pdf", page: 48, quote: "Gross profit: $17,660 million (gross margin 18.2%, down from 25.6%). Pricing reductions impacted average selling price." },
        { id: "S2", doc: "Amazon_23.pdf", page: 27, quote: "The FTC filed suit against Amazon alleging illegal monopoly maintenance. Potential regulatory action could force business model changes." },
        { id: "S3", doc: "Amazon_Annual_Report_FY2025.pdf", page: 61, quote: "Cash and equivalents were $95,000 million at the end of fiscal year, and total debt stood at $122,000 million." },
        { id: "S4", doc: "APPLE_2023_Annual_Report.txt", page: 12, quote: "Total current assets: $143,566 million; Total current liabilities: $145,308 million yielding current ratio of 0.99x." }
      ],
      retrievalPlan: "Identify the top 3 financial risks across all loaded companies. Searched 20 session documents using semantic keyword fallback retrieval; validated exact source quotes and numeric tokens for 4 cited passages. This is a method summary, not hidden chain-of-thought.",
      latency: "4.7s"
    },
    {
      keywords: ["apple", "revenue growth", "gross margin", "trend"],
      question: "What is Apple's revenue growth trend and gross margin?",
      answer: `Apple Inc. (AAPL) reported the following core top-line and margin trajectory:

- **Revenue & Growth Trend:** In FY2023, Apple generated **$394.33 Billion** in total net sales, representing a modest decline of **-0.26% (-0.3%) YoY** compared to $394.33B vs prior peak levels. This slight contraction was primarily driven by a 2% decline in iPhone hardware net sales ($205.49B, 52% of sales) amid consumer electronics market headwinds [S1].
- **Gross Margin Strength:** Apple maintained exceptional pricing power with a **Gross Margin of 42.90%**, supported by expanding high-margin Services revenue (App Store, Cloud, Apple Pay) surpassing 71% gross margin [S2].
- **Operating & Net Conversion:** Operating margin recorded **29.00%** with a **Net Margin of 24.60%** ($96.9B net income) [S3].`,
      sources: [
        { id: "S1", doc: "AAPL_2023_Annual_Report.txt", page: 22, quote: "Total net sales were $394,328 million compared to $394,328 million with iPhone net sales of $205,489 million." },
        { id: "S2", doc: "APPLE_25.pdf", page: 34, quote: "Products gross margin was 36.5% and Services gross margin was 70.8%, for total consolidated gross margin of 42.9%." },
        { id: "S3", doc: "APPLE_ANNUAL_2024.pdf", page: 18, quote: "Net income was $96,995 million, reflecting net profit margin of 24.60%." }
      ],
      retrievalPlan: "Queried ChromaDB financial_documents collection for Apple FY2023 revenue, revenue growth YoY, and gross profit margins. Corroborated with audited 10-K statement of operations.",
      latency: "3.4s"
    },
    {
      keywords: ["tesla", "apple", "free cash flow", "cash flow", "compare"],
      question: "Compare the free cash flow generation of Tesla vs Apple",
      answer: `Comparison of Free Cash Flow (FCF) generation between Apple and Tesla reveals stark capital intensity contrasts:

- **Apple Inc. (AAPL):**
  - **Operating Cash Flow:** $114.2 Billion [S1]
  - **Capital Expenditures (CapEx):** $11.0 Billion
  - **Free Cash Flow (FCF):** **$103.2 Billion** (FCF Conversion of ~26.2% of Revenue)
  - Apple's asset-light outsourced manufacturing model and high Services revenue generate unprecedented cash yields, facilitating over $80B annually in share buybacks.

- **Tesla, Inc. (TSLA):**
  - **Operating Cash Flow:** $13.26 Billion [S2]
  - **Capital Expenditures (CapEx):** $8.90 Billion
  - **Free Cash Flow (FCF):** **$4.36 Billion** (FCF Conversion of ~4.5% of Revenue)
  - Tesla's FCF was severely constrained by aggressive Giga-factory expansions, Cybertruck tooling, and next-gen platform R&D, coupled with lower vehicle margins [S3].`,
      sources: [
        { id: "S1", doc: "AAPL_2023_Annual_Report.txt", page: 41, quote: "Cash generated by operating activities was $114,217 million; payments for property, plant and equipment were $10,959 million." },
        { id: "S2", doc: "Tesla_Annual_Report_FY2026.pdf", page: 55, quote: "Net cash provided by operating activities was $13,256 million, capital expenditures were $8,898 million." },
        { id: "S3", doc: "TSLA_2023_Annual_Report.txt", page: 14, quote: "Free cash flow was $4,358 million, down 42% from prior year due to ramp expenditures and pricing actions." }
      ],
      retrievalPlan: "Retrieved cash flow statements for Apple and Tesla. Extracted Cash from Operations and CapEx line items; calculated net FCF and FCF margin ratios.",
      latency: "4.1s"
    },
    {
      keywords: ["wipro", "integrated", "2025-26", "2026", "wit", "integrated annual report"],
      question: "What are the key financial performance highlights and metrics from Wipro's Integrated Annual Report 2025-26?",
      answer: `Based on Wipro Limited's **Integrated Annual Report 2025-26 (FY26)** [S1]:

- **Gross Revenue:** **₹928,093 Million (~$11.16B USD)**, representing a **+4.17% YoY** growth compared to ₹890,916M in FY25 [S1].
- **Operating Income (EBIT):** **₹151,251 Million (~$1.82B USD)** with an **Operating Margin of 16.30%** (marginally lower by 68 bps from 16.98% in FY25 due to discretionary spending headwinds) [S2].
- **Net Profit:** **₹131,974 Million (~$1.59B USD)** attributable to equity holders (Net Margin: **14.22%**) [S1].
- **Diluted EPS:** **₹12.56 per share** (+0.32% YoY) [S1].
- **Balance Sheet & Cash Reserves:**
  - Net Worth: **₹887,877 Million**
  - Gross Cash: **₹551,809 Million**
  - Total Debt: **₹167,874 Million** (D/E ratio: **0.19**)
  - **Net Cash Position:** **₹383,935 Million (~$4.6B USD)** in surplus liquidity [S2].
- **Key Risks:** Client discretionary budget delays in Americas 2 vertical and foreign currency cross-rate fluctuations, mitigated by large deal wins and the Wipro Intelligence unified AI suite [S1].`,
      sources: [
        { id: "S1", doc: "Integrated-annual-report-2025-26.pdf", page: 25, quote: "Revenue ₹928,093 million, up 4.17% YoY; Gross Profit ₹271,901 million; Net profit attributable to equity holders ₹131,974 million; Diluted EPS ₹12.56." },
        { id: "S2", doc: "Integrated-annual-report-2025-26.pdf", page: 26, quote: "Operating margin was 16.30%. Net cash position stood at ₹383,935 million with gross cash of ₹551,809 million." }
      ],
      retrievalPlan: "Identified query intent for Wipro Integrated Annual Report 2025-26. Retrieved audited consolidated financials from Leadership Insights & Outlook (Page 25-27), verified currency values (INR millions / USD billions), and grounded EPS, margin, and liquidity figures.",
      latency: "1.4s"
    }
  ]
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = FIN_DATA;
}
