// Finora AI — Financial Intelligence Terminal
// Client Application Engine v2 — Premium Business Design

let currentRoute = 'dashboard';
let barChartInst = null;
let radarChartInst = null;
let activeRadarComps = ['Apple Inc.', 'Microsoft Corporation', 'TCS'];
let benchSelected = ['Amazon.com, Inc.', 'Apple Inc.', 'Microsoft Corporation', 'TCS'];
let selectedFile = null;
let selectedUploadFile = null;

// Company multi-selection state for Financial Metrics
let selectedMetricsComps = []; // empty array means "All Companies"
let activeMetricsTab = 'revenue'; // 'revenue', 'margins', 'ratios', 'cashflow'

// Research Agent mode state
let currentResearchMode = 'advanced'; // 'default' or 'advanced'

// DuPont analysis target company
let currentDuPontComp = 'Apple Inc.';

// Route name map
const ROUTE_NAMES = {
  dashboard: 'Overview',
  sessions: 'Research Sessions',
  documents: 'Documents',
  companies: 'Companies',
  metrics: 'Financial Metrics',
  risks: 'Risk Analysis',
  benchmark: 'Benchmarking',
  reports: 'Reports',
  research: 'Research Agent'
};

// ========== INIT ==========
document.addEventListener('DOMContentLoaded', () => {
  initTime();
  initRouting();
  renderAll();
  initChat();
  initDropZone();
  syncServerData();
  initDuPontView();
});

async function syncServerData() {
  try {
    const res = await fetch('/api/documents');
    const docs = await res.json();
    if (Array.isArray(docs) && docs.length > 0) {
      FIN_DATA.documents = docs;
      renderDocsTable();
      const kd = document.getElementById('kpiDocs');
      if (kd) kd.textContent = docs.length;
      const bd = document.getElementById('navBadgeDocs');
      if (bd) bd.textContent = docs.length;
    }
  } catch (e) {
    // Keep local data
  }
}

// ========== TICKER ==========
function initTicker() {
  const track = document.getElementById('tickerTrack');
  if (!track) return;

  // Build ticker items (duplicated for infinite loop)
  const items = TICKER_DATA.map(t => `
    <span class="ticker-item">
      <span class="ticker-sym">${t.sym}</span>
      <span class="ticker-sep">|</span>
      <span class="ticker-val">${t.val}</span>
      <span class="ticker-chg ${t.pos ? 'pos' : 'neg'}">${t.pos ? '▲' : '▼'} ${t.chg}</span>
    </span>
  `).join('');

  track.innerHTML = items + items; // duplicate for seamless loop
}

// ========== CLOCK ==========
function initTime() {
  function updateClock() {
    const now = new Date();
    const el = document.getElementById('marketTime');
    if (el) {
      el.textContent = 'IST ' + now.toLocaleTimeString('en-IN', { hour12: false });
    }
  }
  updateClock();
  setInterval(updateClock, 1000);
}

// ========== ROUTING ==========
function initRouting() {
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const r = link.getAttribute('data-route');
      if (r) switchRoute(r);
    });
  });

  const hash = window.location.hash.replace('#', '') || 'dashboard';
  switchRoute(hash, false);
  window.addEventListener('hashchange', () => {
    switchRoute(window.location.hash.replace('#', '') || 'dashboard', false);
  });
}

function switchRoute(route, updateHash = true) {
  currentRoute = route;
  if (updateHash) window.location.hash = route;

  document.querySelectorAll('.nav-link').forEach(l => l.classList.toggle('active', l.getAttribute('data-route') === route));
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

  const view = document.getElementById(`view-${route}`);
  if (view) view.classList.add('active');

  const bcPage = document.getElementById('bcPage');
  if (bcPage) bcPage.textContent = ROUTE_NAMES[route] || 'Overview';

  if (route === 'metrics') setTimeout(() => { renderMetricsCompanyChips(); renderMetricsCharts(); renderDuPontView(); }, 60);
  if (route === 'benchmark') renderBenchMatrix();
}

// ========== RENDER ALL ==========
function renderAll() {
  renderPipeline();
  renderMarketCards();
  renderActivityLog();
  renderDashSessions();
  renderDashReports();
  renderSessionsGrid();
  renderDocsTable();
  renderCompanies();
  renderMetricsCompanyChips();
  renderMetricsTable();
  renderRisks();
  renderBenchChips();
  renderReports();
}

// ========== PIPELINE ==========
function renderPipeline() {
  const row = document.getElementById('pipelineRow');
  if (!row) return;

  row.innerHTML = FIN_DATA.agents.map(a => `
    <div class="pipeline-agent-pill">
      <span class="agent-pill-dot" style="background:${a.color};box-shadow:0 0 6px ${a.color};"></span>
      <div class="agent-pill-info">
        <div class="agent-pill-name">${a.name}</div>
        <div class="agent-pill-role">${a.role}</div>
      </div>
      <span class="agent-pill-badge">READY</span>
    </div>
  `).join('');
}

// ========== MARKET CARDS (DASHBOARD) ==========
function sparkBars(n = 7) {
  const heights = Array.from({length: n}, (_, i) =>
    i === n-1 ? 100 : Math.floor(30 + Math.random() * 70)
  );
  return heights.map((h, i) =>
    `<div class="spark-bar ${i === n-1 ? 'last' : ''}" style="height:${h}%"></div>`
  ).join('');
}

function renderMarketCards() {
  const grid = document.getElementById('marketCardsGrid');
  if (!grid) return;

  grid.innerHTML = FIN_DATA.financialOverview.slice(0, 4).map(item => `
    <div class="market-card" onclick="switchRoute('metrics')">
      <div class="market-card-header">
        <span class="mkt-ticker">${item.ticker}</span>
        <span class="mkt-chg ${item.growth.startsWith('-') ? 'dn' : 'up'}">${item.growth}</span>
      </div>
      <div class="mkt-revenue">${item.revenue}</div>
      <div class="mkt-margin-row">
        <span>Revenue</span>
        <span style="color:var(--text-secondary);">Net Mgn ${item.netMargin}</span>
      </div>
      <div class="sparkline">${sparkBars()}</div>
    </div>
  `).join('');
}

// ========== ACTIVITY LOG ==========
function renderActivityLog() {
  const el = document.getElementById('activityLog');
  if (!el) return;

  el.innerHTML = FIN_DATA.agentActivity.slice(0, 8).map(a => `
    <div class="log-row">
      <div class="log-dot ${a.status}"></div>
      <span class="log-agent">${a.agent.split(' ')[0]}</span>
      <span class="log-action">${a.action}</span>
      ${a.latency ? `<span class="log-latency">${a.latency}</span>` : ''}
      <span class="log-time">${a.time}</span>
    </div>
  `).join('');
}

// ========== DASH SESSIONS ==========
function renderDashSessions() {
  const el = document.getElementById('dashSessions');
  if (!el) return;

  el.innerHTML = FIN_DATA.sessions.slice(0, 2).map(s => `
    <div class="item-row" onclick="switchRoute('sessions')">
      <div class="item-row-dot"></div>
      <span class="item-row-title">${s.name}</span>
      <span class="status-pill status-active">${s.status}</span>
      <span class="item-row-meta">${s.date}</span>
    </div>
  `).join('');
}

// ========== DASH REPORTS ==========
function renderDashReports() {
  const el = document.getElementById('dashReports');
  if (!el) return;

  el.innerHTML = FIN_DATA.reports.slice(0, 3).map(r => `
    <div class="item-row" onclick="openViewReport('${r.id}')">
      <div class="item-row-dot" style="background:var(--gold)"></div>
      <span class="item-row-title">${r.company}</span>
      <span class="status-pill status-completed">${r.status}</span>
      <span class="item-row-meta">${r.date}</span>
    </div>
  `).join('');
}

// ========== SESSIONS GRID ==========
function renderSessionsGrid() {
  const el = document.getElementById('sessionsGrid');
  if (!el) return;

  el.innerHTML = FIN_DATA.sessions.map(s => `
    <div class="session-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
        <div class="session-title">${s.name}</div>
        <span class="status-pill status-${s.status}">${s.status}</span>
      </div>
      <div class="session-desc">${s.description}</div>
      <div class="session-tags">
        ${s.tags.map(t => `<span class="session-tag">${t}</span>`).join('')}
      </div>
      <div class="session-footer">
        <span>${s.docsCount} docs · ${s.msgsCount} messages</span>
        <span>${s.date}</span>
      </div>
    </div>
  `).join('');
}

// ========== DOCUMENTS TABLE ==========
function renderDocsTable() {
  const body = document.getElementById('docsTableBody');
  if (!body) return;

  const searchVal = (document.getElementById('docSearch')?.value || '').toLowerCase();
  const typeVal = document.getElementById('docTypeFilter')?.value || 'all';

  const filtered = FIN_DATA.documents.filter(d => {
    const matchS = d.name.toLowerCase().includes(searchVal) || d.company.toLowerCase().includes(searchVal);
    const matchT = typeVal === 'all' || d.type.toLowerCase().includes(typeVal.toLowerCase());
    return matchS && matchT;
  });

  const chip = document.getElementById('docCountChip');
  if (chip) chip.textContent = `${filtered.length} documents`;

  body.innerHTML = filtered.map(d => `
    <div class="doc-row ${d._isNew ? 'newly-added' : ''}">
      <div class="doc-filename">
        <div class="doc-ext-badge doc-ext-${d.format}">${d.format.toUpperCase()}</div>
        <span class="doc-name-text" title="${d.name}">${d.name}</span>
        ${d._isNew ? '<span class="just-indexed-badge">JUST INDEXED</span>' : ''}
      </div>
      <div class="doc-cell company">${d.company}</div>
      <div class="doc-cell" style="text-align:center;">${d.year}</div>
      <div class="doc-cell" style="text-align:center;"><span class="chunks-tag">${d.chunks} chunks</span></div>
      <div class="doc-cell" style="text-align:center;">${d.format.toUpperCase()}</div>
      <div class="doc-cell" style="text-align:center;">${d.date}</div>
      <div class="doc-cell" style="text-align:center;">
        <button class="btn-gold" style="padding:4px 9px;font-size:0.68rem;display:inline-flex;align-items:center;gap:4px;" onclick="downloadReportForDoc('${escapeHTML(d.name)}', '${escapeHTML(d.company)}', '${escapeHTML(d.year)}')">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
          PDF Report
        </button>
      </div>
    </div>
  `).join('');

  const searchEl = document.getElementById('docSearch');
  if (searchEl && !searchEl.dataset.bound) {
    searchEl.dataset.bound = 'true';
    searchEl.addEventListener('input', renderDocsTable);
  }
  const filterEl = document.getElementById('docTypeFilter');
  if (filterEl && !filterEl.dataset.bound) {
    filterEl.dataset.bound = 'true';
    filterEl.addEventListener('change', renderDocsTable);
  }
}

// ========== COMPANIES (CARDS & TABLE) ==========
const COMPANY_COLORS = {
  'apple': '#8b5cf6',
  'microsoft': '#0284c7',
  'amazon': '#f59e0b',
  'tesla': '#ef4444',
  'tcs': '#10b981',
  'infosys': '#2563eb',
  'infoys': '#2563eb',
  'reliance': '#ea580c',
  'meta': '#6366f1',
  'nvidia': '#059669',
  'wipro': '#0d9488',
  'integrated': '#0d9488'
};

function getCoColor(name) {
  const lower = (name || '').toLowerCase();
  for (const [key, color] of Object.entries(COMPANY_COLORS)) {
    if (lower.includes(key)) return color;
  }
  return '#4f46e5';
}

let isCompanyTableView = false;
function toggleCompanyView() {
  isCompanyTableView = !isCompanyTableView;
  const grid = document.getElementById('companiesGrid');
  const table = document.getElementById('companiesTableCard');
  const btn = document.getElementById('btnToggleCompView');
  if (grid) grid.style.display = isCompanyTableView ? 'none' : 'grid';
  if (table) table.style.display = isCompanyTableView ? 'block' : 'none';
  if (btn) {
    btn.innerHTML = isCompanyTableView ? 
      `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg> Card View` :
      `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg> Table View`;
  }
}

function renderCompanies() {
  const searchVal = (document.getElementById('compSearch')?.value || '').toLowerCase();
  const filtered = FIN_DATA.companies.filter(c =>
    c.name.toLowerCase().includes(searchVal) || 
    c.ticker.toLowerCase().includes(searchVal) ||
    c.sector.toLowerCase().includes(searchVal)
  );

  const chip = document.getElementById('compCountChip');
  if (chip) chip.textContent = `${filtered.length} companies`;

  // 1. Render Cards Grid (Matches Reference UI)
  const grid = document.getElementById('companiesGrid');
  if (grid) {
    grid.innerHTML = filtered.map(c => {
      const color = getCoColor(c.name);
      const isPos = !c.growth.startsWith('-') && !c.growth.startsWith('+0');
      const isNeg = c.growth.startsWith('-');
      const growthClass = isPos ? 'growth-pos' : (isNeg ? 'growth-neg' : 'growth-neutral');
      const growthArrow = isPos ? '▲' : (isNeg ? '▼' : '—');

      return `
        <div class="company-card">
          <div class="company-card-top">
            <div class="company-badge-lg" style="background:${color};">
              ${c.badge}
            </div>
            <div class="company-header-info">
              <div class="company-header-name">${c.name}</div>
              <div class="company-header-meta">
                <span class="company-sector-badge">${c.sector}</span>
                <span>•</span>
                <span>${c.ticker}</span>
                <span>•</span>
                <span>${c.docsCount || 1} filings</span>
              </div>
            </div>
          </div>

          <div class="company-metrics-grid">
            <div class="metric-cell">
              <span class="metric-cell-label">Revenue</span>
              <span class="metric-cell-val ${c.revenue === '$0' ? 'na' : ''}">${c.revenue}</span>
            </div>
            <div class="metric-cell">
              <span class="metric-cell-label">Net Margin</span>
              <span class="metric-cell-val ${c.netMargin === 'N/A' ? 'na' : ''}">${c.netMargin}</span>
            </div>
            <div class="metric-cell">
              <span class="metric-cell-label">Gross Margin</span>
              <span class="metric-cell-val ${c.grossMargin === 'N/A' ? 'na' : ''}">${c.grossMargin}</span>
            </div>
            <div class="metric-cell">
              <span class="metric-cell-label">EPS</span>
              <span class="metric-cell-val ${c.eps === 'N/A' ? 'na' : ''}">${c.eps}</span>
            </div>
            <div class="metric-cell">
              <span class="metric-cell-label">ROE</span>
              <span class="metric-cell-val ${c.roe === 'N/A' ? 'na' : ''}">${c.roe}</span>
            </div>
            <div class="metric-cell">
              <span class="metric-cell-label">D/E Ratio</span>
              <span class="metric-cell-val ${c.deRatio === 'N/A' ? 'na' : ''}">${c.deRatio}</span>
            </div>
          </div>

          <div class="company-growth-row ${growthClass}">
            <span>Revenue Growth</span>
            <span>${growthArrow} ${c.growth}</span>
          </div>

          <div class="company-actions-row">
            <button class="co-action-btn btn-m" onclick="goMetrics('${c.name}')">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
              Metrics
            </button>
            <button class="co-action-btn btn-r" onclick="goRisks('${c.name}')">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              Risks
            </button>
            <button class="co-action-btn btn-c" onclick="goCompare('${c.name}')">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
              Compare
            </button>
          </div>
        </div>
      `;
    }).join('');
  }

  // 2. Render Table View
  const tbody = document.getElementById('companiesTableBody');
  if (tbody) {
    tbody.innerHTML = filtered.map(c => `
      <tr>
        <td class="company-name-cell">
          <span class="company-badge-sm" style="background:${getCoColor(c.name)}">${c.badge}</span>
          ${c.name}
          <span class="company-ticker-cell">${c.ticker} · ${c.sector}</span>
        </td>
        <td class="${c.revenue === '$0' ? 'val-na' : ''}">${c.revenue}</td>
        <td class="${c.netMargin === 'N/A' ? 'val-na' : ''}">${c.netMargin}</td>
        <td class="${c.grossMargin === 'N/A' ? 'val-na' : ''}">${c.grossMargin}</td>
        <td class="${c.roe === 'N/A' ? 'val-na' : ''}">${c.roe}</td>
        <td class="${c.deRatio === 'N/A' ? 'val-na' : ''}">${c.deRatio}</td>
        <td class="${c.eps === 'N/A' ? 'val-na' : ''}">${c.eps}</td>
        <td class="${c.growth.startsWith('-') ? 'val-neg' : c.growth.startsWith('+0') ? 'val-na' : 'val-pos'}">${c.growth}</td>
        <td style="text-align:center;white-space:nowrap;">
          <button class="action-btn-sm" onclick="goMetrics('${c.name}')">Metrics</button>
          <button class="action-btn-sm" onclick="goRisks('${c.name}')">Risks</button>
          <button class="action-btn-sm" onclick="goCompare('${c.name}')">Compare</button>
        </td>
      </tr>
    `).join('');
  }

  // Bind search once
  const searchEl = document.getElementById('compSearch');
  if (searchEl && !searchEl.dataset.bound) {
    searchEl.dataset.bound = 'true';
    searchEl.addEventListener('input', renderCompanies);
  }
}

function goMetrics(name) { switchRoute('metrics'); const f = document.getElementById('metricsFilter'); if (f) { f.value = name; renderMetricsTable(); } }
function goRisks(name) { switchRoute('risks'); setRiskFilter('all'); const el = document.getElementById('risksList'); if (el) { el.innerHTML = FIN_DATA.risks.filter(r => r.company.toLowerCase().includes(name.toLowerCase())).map(renderRiskCard).join(''); } }
function goCompare(name) { if (!benchSelected.includes(name)) benchSelected.push(name); switchRoute('benchmark'); }

// ========== COMPANY FILTER CHIPS FOR METRICS ==========
function renderMetricsCompanyChips() {
  const container = document.getElementById('metricsCompanyChips');
  if (!container) return;

  const allComps = FIN_DATA.metricsTable.map(m => ({
    name: m.company,
    ticker: m.ticker || m.company.substring(0, 4).toUpperCase()
  }));

  const allBtn = document.getElementById('btnSelectAllComps');
  if (allBtn) {
    allBtn.classList.toggle('active', selectedMetricsComps.length === 0);
  }

  container.innerHTML = allComps.map(c => {
    const isSelected = selectedMetricsComps.includes(c.name);
    return `
      <button class="mcp-chip ${isSelected ? 'active' : ''}" onclick="toggleMetricsCompany('${escapeHTML(c.name)}')">
        <span class="mcp-chip-ticker">${c.ticker}</span>
        <span class="mcp-chip-name">${c.name}</span>
        ${isSelected ? '<span class="mcp-check">✓</span>' : ''}
      </button>
    `;
  }).join('');

  const hint = document.getElementById('metricsFilterHint');
  if (hint) {
    if (selectedMetricsComps.length === 0) {
      hint.textContent = 'Showing all companies. Click 1 company to isolate its graphs, or select multiple to compare.';
    } else if (selectedMetricsComps.length === 1) {
      hint.textContent = `Isolated: ${selectedMetricsComps[0]}. Detailed revenue, profit & margin breakdown active.`;
    } else {
      hint.textContent = `Comparing ${selectedMetricsComps.length} selected companies side-by-side.`;
    }
  }
}

function toggleMetricsCompany(compName) {
  if (selectedMetricsComps.includes(compName)) {
    selectedMetricsComps = selectedMetricsComps.filter(c => c !== compName);
  } else {
    selectedMetricsComps.push(compName);
  }

  renderMetricsCompanyChips();
  renderMetricsCharts();
  renderMetricsTable();

  // If 1 company is selected, auto-update the DuPont stress tester to it
  if (selectedMetricsComps.length === 1) {
    updateDuPontView(selectedMetricsComps[0]);
  }
}

function resetMetricsCompanyFilter() {
  selectedMetricsComps = [];
  renderMetricsCompanyChips();
  renderMetricsCharts();
  renderMetricsTable();
}

function clearMetricsCompanyFilter() {
  selectedMetricsComps = [];
  renderMetricsCompanyChips();
  renderMetricsCharts();
  renderMetricsTable();
}

// ========== METRICS TABLE ==========
function renderMetricsTable() {
  const tbody = document.getElementById('metricsTableBody');
  if (!tbody) return;

  const q = (document.getElementById('metricsFilter')?.value || '').toLowerCase();
  
  // Filter by selected companies if any are selected, otherwise show all
  let rows = FIN_DATA.metricsTable;
  if (selectedMetricsComps.length > 0) {
    rows = rows.filter(r => selectedMetricsComps.includes(r.company));
  }
  
  if (q) {
    rows = rows.filter(r =>
      r.company.toLowerCase().includes(q) || r.ticker.toLowerCase().includes(q)
    );
  }

  tbody.innerHTML = rows.map(r => `
    <tr class="${selectedMetricsComps.includes(r.company) ? 'highlight-row' : ''}">
      <td class="company-name-cell">
        ${r.company}
        <span class="company-ticker-cell">${r.ticker}</span>
      </td>
      <td>${r.revenue}</td>
      <td class="${r.growth.startsWith('-') ? 'val-neg' : r.growth.startsWith('+0') ? 'val-na' : 'val-pos'}">${r.growth}</td>
      <td>${r.grossMargin}</td>
      <td>${r.opMargin}</td>
      <td>${r.netMargin}</td>
      <td>${r.currentRatio}</td>
      <td>${r.de}</td>
      <td>${r.roe}</td>
      <td style="font-weight:600;">${r.eps}</td>
    </tr>
  `).join('');

  const filterInput = document.getElementById('metricsFilter');
  if (filterInput && !filterInput.dataset.bound) {
    filterInput.dataset.bound = 'true';
    filterInput.addEventListener('input', renderMetricsTable);
  }
}

// ========== METRICS CHARTS ==========
function renderMetricsCharts() {
  renderBarChart();
  renderRadarPills();
  renderRadarChart();
}

function renderBarChart() {
  const canvas = document.getElementById('barChart');
  if (!canvas) return;
  if (barChartInst) barChartInst.destroy();

  const titleEl = document.getElementById('barChartTitle');
  const tagEl = document.getElementById('barChartTag');

  // Determine active companies for the chart
  let activeData = FIN_DATA.metricsTable.filter(m => m.revNum > 0);
  if (selectedMetricsComps.length > 0) {
    activeData = FIN_DATA.metricsTable.filter(m => selectedMetricsComps.includes(m.company));
  } else {
    activeData = activeData.slice(0, 8);
  }

  // CASE 1: EXACTLY 1 COMPANY SELECTED -> ISOLATED DEEP-DIVE GRAPHS
  if (selectedMetricsComps.length === 1 && activeData.length === 1) {
    const comp = activeData[0];
    if (titleEl) titleEl.textContent = `${comp.company} — Financial & Earnings Breakdown ($M)`;
    if (tagEl) tagEl.textContent = 'Single Company Deep-Dive';

    const rev = comp.revNum || 1000;
    const gmPercent = parseFloat((comp.grossMargin || '40').replace('%', '')) || 40;
    const opPercent = parseFloat((comp.opMargin || '20').replace('%', '')) || 20;
    const netPercent = parseFloat((comp.netMargin || '15').replace('%', '')) || 15;

    const grossProfit = Math.round(rev * (gmPercent / 100));
    const ebitda = comp.ebitda || Math.round(rev * 0.28);
    const opIncome = Math.round(rev * (opPercent / 100));
    const netIncome = Math.round(rev * (netPercent / 100));

    barChartInst = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: ['Net Revenue', 'Gross Profit', 'EBITDA', 'Operating Income', 'Net Income'],
        datasets: [
          {
            label: `${comp.company} ($ Millions USD)`,
            data: [rev, grossProfit, ebitda, opIncome, netIncome],
            backgroundColor: [
              '#3b82f6',
              '#06b6d4',
              '#10b981',
              '#8b5cf6',
              '#f59e0b'
            ],
            borderColor: [
              '#2563eb',
              '#0891b2',
              '#059669',
              '#7c3aed',
              '#d97706'
            ],
            borderWidth: 1.5,
            borderRadius: 6,
            barPercentage: 0.55
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#94a3b8', font: { size: 11, family: 'Inter', weight: '600' } } },
          tooltip: {
            backgroundColor: '#1e293b',
            titleColor: '#f8fafc',
            bodyColor: '#cbd5e1',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            padding: 10,
            callbacks: {
              label: (ctx) => ` $${ctx.parsed.y.toLocaleString()} M USD`
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 11, family: 'Inter', weight: '600' } } },
          y: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#94a3b8', font: { size: 10, family: 'Inter' } } }
        }
      }
    });
    return;
  }

  // CASE 2: MULTIPLE COMPANIES (2+) OR ALL SELECTED -> COMPARATIVE SIDE-BY-SIDE GRAPHS
  const isMulti = selectedMetricsComps.length > 1;
  if (titleEl) {
    titleEl.textContent = isMulti 
      ? `Comparative Metrics (${selectedMetricsComps.length} Selected Entities)` 
      : `Revenue & EBITDA Comparison (All Entities)`;
  }
  if (tagEl) {
    tagEl.textContent = isMulti ? 'Multi-Company Comparison' : 'Extraction Agent';
  }

  const labels = activeData.map(m => m.ticker || m.company.split(' ')[0]);

  // Handle Tab-based datasets
  let datasets = [];
  if (activeMetricsTab === 'revenue') {
    datasets = [
      {
        label: 'Revenue ($M)',
        data: activeData.map(m => m.revNum),
        backgroundColor: '#3b82f6',
        borderColor: '#2563eb',
        borderWidth: 1,
        borderRadius: 5,
        barPercentage: 0.55
      },
      {
        label: 'EBITDA ($M)',
        data: activeData.map(m => m.ebitda),
        backgroundColor: '#10b981',
        borderColor: '#059669',
        borderWidth: 1,
        borderRadius: 5,
        barPercentage: 0.55
      }
    ];
  } else if (activeMetricsTab === 'margins') {
    datasets = [
      {
        label: 'Gross Margin %',
        data: activeData.map(m => parseFloat((m.grossMargin || '0').replace('%', '')) || 0),
        backgroundColor: '#06b6d4',
        borderColor: '#0891b2',
        borderWidth: 1,
        borderRadius: 5,
        barPercentage: 0.55
      },
      {
        label: 'Net Margin %',
        data: activeData.map(m => parseFloat((m.netMargin || '0').replace('%', '')) || 0),
        backgroundColor: '#8b5cf6',
        borderColor: '#7c3aed',
        borderWidth: 1,
        borderRadius: 5,
        barPercentage: 0.55
      }
    ];
  } else if (activeMetricsTab === 'ratios') {
    datasets = [
      {
        label: 'ROE %',
        data: activeData.map(m => parseFloat((m.roe || '0').replace('%', '')) || 0),
        backgroundColor: '#f59e0b',
        borderColor: '#d97706',
        borderWidth: 1,
        borderRadius: 5,
        barPercentage: 0.55
      },
      {
        label: 'Debt / Equity (x10)',
        data: activeData.map(m => (parseFloat(m.de) || 0) * 10),
        backgroundColor: '#ef4444',
        borderColor: '#dc2626',
        borderWidth: 1,
        borderRadius: 5,
        barPercentage: 0.55
      }
    ];
  } else {
    // Cash Flow Tab
    datasets = [
      {
        label: 'Free Cash Flow ($M)',
        data: activeData.map(m => Math.round((m.ebitda || 0) * 0.72)),
        backgroundColor: '#10b981',
        borderColor: '#059669',
        borderWidth: 1,
        borderRadius: 5,
        barPercentage: 0.55
      }
    ];
  }

  barChartInst = new Chart(canvas, {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8', font: { size: 11, family: 'Inter', weight: '600' }, boxWidth: 12 } },
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#f8fafc',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          padding: 10
        }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10, family: 'Inter', weight: '600' } } },
        y: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#94a3b8', font: { size: 10, family: 'Inter' } } }
      }
    }
  });
}

function renderRadarPills() {
  const el = document.getElementById('radarPills');
  if (!el) return;

  const allComps = Object.keys(FIN_DATA.radarData.companies);
  el.innerHTML = allComps.map(name => `
    <span class="r-pill ${activeRadarComps.includes(name) ? 'on' : ''}" onclick="toggleRadar('${name}')">
      ${name.split(' ')[0]}
    </span>
  `).join('');
}

function toggleRadar(name) {
  if (activeRadarComps.includes(name)) {
    if (activeRadarComps.length > 1) activeRadarComps = activeRadarComps.filter(n => n !== name);
  } else {
    activeRadarComps.push(name);
  }
  renderRadarPills();
  renderRadarChart();
}

function renderRadarChart() {
  const canvas = document.getElementById('radarChart');
  if (!canvas) return;
  if (radarChartInst) radarChartInst.destroy();

  const palette = [
    { b: '#3b82f6', bg: 'rgba(59,130,246,0.18)' },
    { b: '#10b981', bg: 'rgba(16,185,129,0.18)' },
    { b: '#f59e0b', bg: 'rgba(245,158,11,0.18)' },
    { b: '#8b5cf6', bg: 'rgba(139,92,246,0.18)' },
    { b: '#ec4899', bg: 'rgba(236,72,153,0.18)' }
  ];

  // If user selected companies in metrics filter, prioritize them on radar
  let radarEntities = activeRadarComps;
  if (selectedMetricsComps.length > 0) {
    const matched = selectedMetricsComps.filter(c => FIN_DATA.radarData.companies[c]);
    if (matched.length > 0) radarEntities = matched;
  }

  radarChartInst = new Chart(canvas, {
    type: 'radar',
    data: {
      labels: FIN_DATA.radarData.labels,
      datasets: radarEntities.map((name, i) => ({
        label: name.split(' ')[0],
        data: FIN_DATA.radarData.companies[name] || [30, 20, 15, 20, 25],
        borderColor: palette[i % palette.length].b,
        backgroundColor: palette[i % palette.length].bg,
        borderWidth: 2,
        pointBackgroundColor: palette[i % palette.length].b,
        pointRadius: 4
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8', font: { size: 10, family: 'Inter', weight: '600' }, boxWidth: 10 } }
      },
      scales: {
        r: {
          angleLines: { color: 'rgba(255,255,255,0.08)' },
          grid: { color: 'rgba(255,255,255,0.06)' },
          pointLabels: { color: '#94a3b8', font: { size: 9, family: 'Inter', weight: '600' } },
          ticks: { display: false }
        }
      }
    }
  });
}

function setTab(tab, el) {
  activeMetricsTab = tab;
  document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  renderBarChart();
}

// ========== DUPONT ANALYSIS & FINANCIAL HEALTH STRESS TESTER ==========
let baseNetMargin = 24.6;
let baseAssetTurn = 1.12;
let baseLeverage = 5.67;
let baseRoe = 156.0;

function initDuPontView() {
  const select = document.getElementById('dupontCompanySelect');
  if (!select) return;

  const comps = FIN_DATA.metricsTable.map(m => m.company);
  select.innerHTML = comps.map(c => `
    <option value="${escapeHTML(c)}" ${c === currentDuPontComp ? 'selected' : ''}>${escapeHTML(c)}</option>
  `).join('');

  updateDuPontView(currentDuPontComp);
}

function updateDuPontView(compName) {
  currentDuPontComp = compName;
  const select = document.getElementById('dupontCompanySelect');
  if (select) select.value = compName;

  const badge = document.getElementById('dupontCompBadge');
  if (badge) badge.textContent = compName;

  const metric = FIN_DATA.metricsTable.find(m => m.company.toLowerCase() === compName.toLowerCase()) || FIN_DATA.metricsTable[0];

  // Extract base numerical values
  const nm = parseFloat((metric.netMargin || '18').replace('%', '')) || 18.0;
  const de = parseFloat(metric.de) || 1.2;
  const leverage = Number((1.0 + de).toFixed(2));
  let roe = parseFloat((metric.roe || '25').replace('%', '')) || 25.0;
  if (roe <= 0) roe = 15.0;

  // Asset Turnover = ROE / (NetMargin * Leverage)
  let assetTurn = (roe / (nm * leverage));
  if (isNaN(assetTurn) || assetTurn <= 0 || assetTurn > 5) assetTurn = 1.05;
  assetTurn = Number(assetTurn.toFixed(2));

  baseNetMargin = nm;
  baseAssetTurn = assetTurn;
  baseLeverage = leverage;
  baseRoe = Number((nm * assetTurn * leverage).toFixed(1));

  document.getElementById('dpNetMargin').textContent = `${baseNetMargin.toFixed(1)}%`;
  document.getElementById('dpAssetTurn').textContent = `${baseAssetTurn.toFixed(2)}x`;
  document.getElementById('dpLeverage').textContent = `${baseLeverage.toFixed(2)}x`;
  document.getElementById('dpRoe').textContent = `${baseRoe.toFixed(1)}%`;

  const qualityEl = document.getElementById('dpRoeQuality');
  if (qualityEl) {
    if (baseRoe > 40) qualityEl.textContent = 'Superior Capital Efficiency';
    else if (baseRoe > 18) qualityEl.textContent = 'Strong Investment Grade';
    else qualityEl.textContent = 'Moderate Capital Returns';
  }

  // Reset sliders
  const revSlider = document.getElementById('revShockSlider');
  const marginSlider = document.getElementById('marginShockSlider');
  if (revSlider) revSlider.value = 0;
  if (marginSlider) marginSlider.value = 0;

  runStressSimulation();
}

function runStressSimulation() {
  const revShock = parseFloat(document.getElementById('revShockSlider')?.value || 0);
  const marginShockBps = parseFloat(document.getElementById('marginShockSlider')?.value || 0);

  document.getElementById('revShockVal').textContent = (revShock >= 0 ? `+${revShock}%` : `${revShock}%`);
  document.getElementById('marginShockVal').textContent = (marginShockBps >= 0 ? `+${marginShockBps} bps` : `${marginShockBps} bps`);

  // Calculate simulated figures
  const marginShiftPercent = marginShockBps / 100;
  let simMargin = baseNetMargin + marginShiftPercent;
  if (simMargin < 0.5) simMargin = 0.5;

  let simTurn = baseAssetTurn * (1 + revShock / 100);
  if (simTurn < 0.2) simTurn = 0.2;

  const simRoeVal = simMargin * simTurn * baseLeverage;

  document.getElementById('simNetMargin').textContent = `${simMargin.toFixed(1)}% (${marginShiftPercent >= 0 ? '+' : ''}${marginShiftPercent.toFixed(1)}%)`;
  document.getElementById('simRoe').textContent = `${simRoeVal.toFixed(1)}%`;

  const statusEl = document.getElementById('simSolvencyStatus');
  if (statusEl) {
    if (simMargin >= 15 && simRoeVal >= 20) {
      statusEl.textContent = 'Tier-1 Balance Sheet Resilience';
      statusEl.style.color = 'var(--positive)';
    } else if (simMargin >= 8 && simRoeVal >= 10) {
      statusEl.textContent = 'Moderate Margin Compression (Stable)';
      statusEl.style.color = 'var(--gold)';
    } else {
      statusEl.textContent = 'High Capital & Liquidity Stress Flagged';
      statusEl.style.color = 'var(--negative)';
    }
  }
}

// ========== RISKS ==========
function renderRisks() {
  const el = document.getElementById('risksList');
  if (!el) return;

  const sev = document.getElementById('riskSevFilter')?.value || 'all';
  const type = document.getElementById('riskTypeFilter')?.value || 'all';

  const filtered = FIN_DATA.risks.filter(r => {
    const ms = sev === 'all' || r.severity === sev;
    const mt = type === 'all' || r.type.toLowerCase().includes(type.toLowerCase());
    return ms && mt;
  });

  const chip = document.getElementById('riskCountChip');
  if (chip) chip.textContent = `${filtered.length} risks shown`;

  el.innerHTML = filtered.map(renderRiskCard).join('');

  document.getElementById('riskSevFilter')?.addEventListener('change', renderRisks);
  document.getElementById('riskTypeFilter')?.addEventListener('change', renderRisks);
}

function renderRiskCard(r) {
  const sevClass = { critical: 'sev-critical', high: 'sev-high', medium: 'sev-medium' }[r.severity] || 'sev-medium';
  const emojis = { critical: '🔴', high: '🟠', medium: '🟡', low: '🟢' };

  return `
    <div class="risk-card">
      <div class="risk-card-toprow">
        <span class="${sevClass}">${emojis[r.severity] || ''} ${r.severity}</span>
        <span class="risk-type-chip">${r.type}</span>
        <span class="risk-company-chip">${r.company}</span>
      </div>
      <div class="risk-card-title">${r.title}</div>
      <div class="risk-card-desc">${r.description}</div>
      <div class="evidence-block">
        <strong>Source Evidence</strong>
        "${r.evidence}"
      </div>
      <div class="rec-block">
        <strong>Analyst Recommendation</strong>
        ${r.recommendation}
      </div>
    </div>
  `;
}

function setRiskFilter(sev) {
  const el = document.getElementById('riskSevFilter');
  if (el) { el.value = sev; renderRisks(); }
}

// ========== BENCHMARK ==========
function renderBenchChips() {
  const el = document.getElementById('benchChips');
  if (!el) return;

  const comps = ['Amazon', 'Amazon.com, Inc.', 'Apple Inc.', 'Microsoft', 'Microsoft Corporation', 'TCS', 'Tesla', 'Tesla, Inc.', 'Infosys', 'reliance'];

  el.innerHTML = comps.map(c => `
    <div class="bench-chip ${benchSelected.includes(c) ? 'on' : ''}" onclick="toggleBench('${c}')">
      ${c}
    </div>
  `).join('');
}

function toggleBench(c) {
  if (benchSelected.includes(c)) {
    if (benchSelected.length > 2) benchSelected = benchSelected.filter(x => x !== c);
  } else {
    benchSelected.push(c);
  }
  renderBenchChips();
}

function renderBenchMatrix() {
  renderBenchChips();

  const thead = document.getElementById('benchThead');
  const tbody = document.getElementById('benchTbody');
  if (!thead || !tbody) return;

  const data = benchSelected.map(name => {
    return FIN_DATA.metricsTable.find(m => m.company.toLowerCase() === name.toLowerCase()) ||
           FIN_DATA.metricsTable.find(m => m.company.toLowerCase().includes(name.split(' ')[0].toLowerCase())) ||
           { company: name, ticker: '', revenue: 'N/A', growth: 'N/A', grossMargin: 'N/A', opMargin: 'N/A', netMargin: 'N/A', currentRatio: 'N/A', de: 'N/A', roe: 'N/A', eps: 'N/A' };
  });

  thead.innerHTML = `<tr>
    <th>Metric</th>
    ${data.map(d => `<th>${d.company.split(' ')[0]}<br><span style="font-weight:400;color:var(--text-muted)">${d.ticker || ''}</span></th>`).join('')}
  </tr>`;

  const metrics = [
    { label: 'Revenue', key: 'revenue' },
    { label: 'YoY Growth', key: 'growth' },
    { label: 'Gross Margin', key: 'grossMargin' },
    { label: 'Operating Margin', key: 'opMargin' },
    { label: 'Net Profit Margin', key: 'netMargin' },
    { label: 'Current Ratio', key: 'currentRatio' },
    { label: 'Debt / Equity', key: 'de' },
    { label: 'ROE', key: 'roe' },
    { label: 'Diluted EPS', key: 'eps' }
  ];

  tbody.innerHTML = metrics.map(m => `
    <tr>
      <td>${m.label}</td>
      ${data.map(d => `<td>${d[m.key] || 'N/A'}</td>`).join('')}
    </tr>
  `).join('');
}

// ========== REPORTS ==========
function renderReports() {
  const el = document.getElementById('reportsList');
  if (!el) return;

  const recClass = { Buy: 'rec-buy', 'Hold / Neutral': 'rec-hold', 'Neutral': 'rec-hold', 'Caution / Watch': 'rec-watch', Watch: 'rec-watch' };

  el.innerHTML = FIN_DATA.reports.map(r => `
    <div class="report-card" onclick="openViewReport('${r.id}')">
      <div class="report-card-header">
        <div class="report-company-badge">
          <span class="company-badge-sm" style="width:24px;height:24px;font-size:0.58rem;">${r.company.substring(0,2).toUpperCase()}</span>
          <span class="report-co-name">${r.company}</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
          <span class="status-pill status-completed">${r.status}</span>
          <span class="rec-badge ${recClass[r.recommendation] || 'rec-hold'}">${r.recommendation}</span>
        </div>
      </div>
      <div class="report-title">${r.title}</div>
      <div class="report-excerpt">${r.summary.slice(0, 300)}...</div>
      <div class="report-footer" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
        <span style="font-size:0.7rem;color:var(--text-muted);">${r.date} · ${r.source}</span>
        <div style="display:flex;align-items:center;gap:6px;" onclick="event.stopPropagation();">
          <button class="btn-gold" style="padding:4px 10px;font-size:0.68rem;display:inline-flex;align-items:center;gap:4px;" onclick="downloadReport('${r.id}', 'pdf')">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
            PDF Report
          </button>
          <button class="btn-outline" style="padding:4px 8px;font-size:0.68rem;" onclick="downloadReport('${r.id}', 'json')">
            JSON
          </button>
          <span style="color:var(--gold);font-size:0.72rem;font-weight:600;cursor:pointer;margin-left:4px;" onclick="openViewReport('${r.id}')">View →</span>
        </div>
      </div>
    </div>
  `).join('');
}

function openViewReport(id) {
  const rep = FIN_DATA.reports.find(r => r.id === id);
  if (!rep) return;

  document.getElementById('viewRepTitle').textContent = rep.title;
  document.getElementById('viewRepBody').innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid var(--border-default);flex-wrap:wrap;gap:10px;">
      <span style="font-size:0.75rem;color:var(--text-muted);">Generated: ${rep.date} · Company: <strong style="color:var(--gold)">${rep.company}</strong></span>
      <div style="display:flex;gap:8px;align-items:center;">
        <span class="rec-badge rec-buy">${rep.recommendation}</span>
        <button class="btn-gold" style="padding:5px 12px;font-size:0.74rem;display:inline-flex;align-items:center;gap:4px;" onclick="downloadReport('${rep.id}', 'pdf')">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
          Download PDF Report
        </button>
        <button class="btn-outline" style="padding:5px 10px;font-size:0.74rem;" onclick="downloadReport('${rep.id}', 'json')">
          JSON
        </button>
        <button class="btn-outline" style="padding:5px 10px;font-size:0.74rem;" onclick="downloadReport('${rep.id}', 'md')">
          Markdown
        </button>
      </div>
    </div>
    <div style="font-size:0.86rem;line-height:1.75;color:var(--text-secondary);">${rep.summary}</div>
    <div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border-subtle);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
      <span style="font-size:0.72rem;color:var(--teal);font-family:var(--font-mono);">Source Filing: ${rep.source}</span>
      <button class="btn-gold" style="padding:6px 14px;font-size:0.74rem;display:inline-flex;align-items:center;gap:4px;" onclick="downloadReport('${rep.id}', 'pdf')">
        📥 Save PDF Report to Disk
      </button>
    </div>
  `;
  openModal('modalViewReport');
}

function downloadReport(id, fmt = 'pdf') {
  window.open(`/api/reports/download/${id}?format=${fmt}`, '_blank');
}

function downloadReportForDoc(filename, company, year, fmt = 'pdf') {
  const cleanComp = (company || '').split(' ')[0];
  const cleanYr = (year || '').replace(/[^0-9]/g, '') || '2024';
  window.open(`/api/reports/download?company=${encodeURIComponent(cleanComp)}&year=${encodeURIComponent(cleanYr)}&format=${fmt}`, '_blank');
}

// ========== RESEARCH AGENT DUAL-MODE CONTROLLER ==========
function setResearchMode(mode) {
  currentResearchMode = mode;
  document.getElementById('modeBtnDefault')?.classList.toggle('active', mode === 'default');
  document.getElementById('modeBtnAdvanced')?.classList.toggle('active', mode === 'advanced');

  const statusEl = document.getElementById('rmbStatusText');
  if (statusEl) {
    if (mode === 'advanced') {
      statusEl.textContent = 'Role: Senior Investment Banking & Fundamental Research Analyst (Gemini 3.8 Flash Active)';
    } else {
      statusEl.textContent = 'Role: Grounded RAG Document Retrieval (Direct Index Search)';
    }
  }
}

// ========== CHAT ENGINE ==========
function initChat() {
  const container = document.getElementById('chatMessages');
  if (!container) return;

  const initial = FIN_DATA.qaKnowledgeBase[0];

  container.innerHTML = `
    <div class="chat-bubble user">
      <div class="chat-ava user">UK</div>
      <div class="bubble user">${initial.question}</div>
    </div>

    <div class="chat-bubble agent">
      <div class="chat-ava agent">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/></svg>
      </div>
      <div class="bubble agent">
        <div class="agent-header-line">
          <strong>Research Agent</strong>
          <span class="ai-mode-pill">⚡ Gemini 3.8 Flash AI</span>
          <span>·</span>
          <span>Oct 15, 2026</span>
          <span>·</span>
          <span style="color:var(--gold);font-family:var(--font-mono);">${initial.latency}</span>
        </div>
        <div class="agent-answer-body">${formatAnswer(initial.answer)}</div>
        <div class="sources-section">
          <span class="sources-toggle" onclick="toggleSources(this)">
            ▾ ${initial.sources.length} cited sources
          </span>
          <div class="sources-list" style="display:none">
            ${initial.sources.map(s => `
              <div class="source-row">
                <div class="source-row-doc">[${s.id}] ${s.doc} — Page ${s.page}</div>
                <div class="source-row-quote">"${s.quote}"</div>
              </div>
            `).join('')}
          </div>
        </div>
        <div class="retrieval-note">${initial.retrievalPlan}</div>
      </div>
    </div>
  `;

  document.getElementById('chatInput')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  });
}

function sendSuggestion(q) {
  const el = document.getElementById('chatInput');
  if (el) { el.value = q; handleSend(); }
}

async function handleSend() {
  const input = document.getElementById('chatInput');
  const q = input.value.trim();
  if (!q) return;
  input.value = '';

  const container = document.getElementById('chatMessages');

  // User message
  const userBubble = document.createElement('div');
  userBubble.className = 'chat-bubble user';
  userBubble.innerHTML = `
    <div class="chat-ava user">UK</div>
    <div class="bubble user">${escapeHTML(q)}</div>
  `;
  container.appendChild(userBubble);

  const isAdv = currentResearchMode === 'advanced';

  // Thinking state
  const thinkBubble = document.createElement('div');
  thinkBubble.className = 'chat-bubble agent';
  thinkBubble.innerHTML = `
    <div class="chat-ava agent">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/></svg>
    </div>
    <div class="bubble agent">
      <div class="agent-header-line">
        <strong>Research Agent</strong>
        <span class="ai-mode-pill">${isAdv ? '⚡ Gemini 3.8 Flash Interpreting...' : '📄 Grounded RAG Searching...'}</span>
      </div>
      <div style="display:flex;align-items:center;gap:8px;color:var(--text-muted);font-size:0.78rem;">
        <span class="pulse-ring" style="width:6px;height:6px;background:${isAdv ? 'var(--teal)' : 'var(--blue)'};"></span>
        ${isAdv ? 'Synthesizing disclosures through Gemini 3.8 Flash reasoning layer...' : 'Querying ChromaDB vector index and extracting citations...'}
      </div>
    </div>
  `;
  container.appendChild(thinkBubble);
  container.scrollTop = container.scrollHeight;

  try {
    const res = await fetch('/api/research/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q, mode: currentResearchMode })
    });
    const data = await res.json();

    const modelBadge = data.aiEnhanced
      ? `<span class="ai-mode-pill">⚡ Gemini 3.8 Flash AI</span>`
      : `<span class="ai-mode-pill default">📄 Standard RAG</span>`;

    thinkBubble.innerHTML = `
      <div class="chat-ava agent">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/></svg>
      </div>
      <div class="bubble agent">
        <div class="agent-header-line">
          <strong>Research Agent</strong>
          ${modelBadge}
          <span>·</span>
          <span>${data.timestamp}</span>
          <span>·</span>
          <span style="color:var(--gold);font-family:var(--font-mono);">${data.latency}</span>
        </div>
        <div class="agent-answer-body">${formatAnswer(data.answer)}</div>
        <div class="sources-section">
          <span class="sources-toggle" onclick="toggleSources(this)">▾ ${data.sources.length} cited sources</span>
          <div class="sources-list" style="display:none">
            ${data.sources.map(s => `
              <div class="source-row">
                <div class="source-row-doc">[${s.id}] ${s.doc} — Page ${s.page}</div>
                <div class="source-row-quote">"${s.quote}"</div>
              </div>
            `).join('')}
          </div>
        </div>
        <div class="retrieval-note">${data.retrievalPlan}</div>
      </div>
    `;

    renderActivityLog();
  } catch (err) {
    thinkBubble.querySelector('.bubble').innerHTML += `<p style="color:var(--negative);font-size:0.76rem;margin-top:8px;">Error querying research agent pipeline.</p>`;
  }

  container.scrollTop = container.scrollHeight;
}

function toggleSources(el) {
  const list = el.nextElementSibling;
  if (list) {
    const hidden = list.style.display === 'none';
    list.style.display = hidden ? 'flex' : 'none';
    el.textContent = (hidden ? '▴' : '▾') + el.textContent.slice(1);
  }
}

// ========== MODALS ==========
function openModal(id) { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }

// ========== TOAST NOTIFICATION SYSTEM ==========
function showToast(title, msg, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const icons = {
    success: '✅',
    info: 'ℹ️',
    error: '⚠️'
  };

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || '🔔'}</span>
    <div class="toast-content">
      <div class="toast-title">${escapeHTML(title)}</div>
      <div class="toast-msg">${escapeHTML(msg)}</div>
    </div>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4500);
}

// ========== DROP ZONE & AUTO-FILL ==========
function initDropZone() {
  const zone = document.querySelector('.drop-zone');
  if (!zone) return;

  ['dragenter', 'dragover'].forEach(name => {
    zone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
      zone.style.borderColor = '#3b82f6';
      zone.style.background = '#eff6ff';
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    zone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
      zone.style.borderColor = '#cbd5e1';
      zone.style.background = '#f8fafc';
    });
  });

  zone.addEventListener('drop', (e) => {
    if (e.dataTransfer && e.dataTransfer.files.length > 0) {
      processSelectedFile(e.dataTransfer.files[0]);
    }
  });
}

function onFileSelect(e) {
  if (e.target.files && e.target.files[0]) {
    processSelectedFile(e.target.files[0]);
  }
}

function processSelectedFile(file) {
  selectedUploadFile = file;
  const dropText = document.getElementById('dropText');
  if (dropText) dropText.textContent = file.name;

  // Smart auto-detect company & year from filename
  const fname = file.name.toUpperCase();
  const compInput = document.getElementById('uploadCompany');
  const yearSelect = document.getElementById('uploadYear');

  if (compInput) {
    if (fname.includes('INTEGRATED') || fname.includes('WIPRO')) compInput.value = 'Wipro Limited';
    else if (fname.includes('REALIANCE') || fname.includes('RELIANCE')) compInput.value = 'Reliance Industries';
    else if (fname.includes('INFOSYS') || fname.includes('INFOYS')) compInput.value = 'Infosys Ltd.';
    else if (fname.includes('APPLE')) compInput.value = 'Apple Inc.';
    else if (fname.includes('MICROSOFT')) compInput.value = 'Microsoft Corporation';
    else if (fname.includes('AMAZON')) compInput.value = 'Amazon.com, Inc.';
    else if (fname.includes('TESLA')) compInput.value = 'Tesla, Inc.';
    else if (fname.includes('TCS')) compInput.value = 'TCS';
    else if (fname.includes('META')) compInput.value = 'Meta Platforms';
    else {
      const guessed = file.name.split(/[_\-.\s]/)[0];
      if (guessed) compInput.value = guessed.charAt(0).toUpperCase() + guessed.slice(1).toLowerCase();
    }
  }

  if (yearSelect) {
    const yrMatch = fname.match(/(202[3-7]|2[3-7])/);
    if (yrMatch) {
      const yr = yrMatch[0].length === 2 ? `FY20${yrMatch[0]}` : `FY${yrMatch[0]}`;
      yearSelect.value = yr;
    }
  }
}

async function handleUpload(e) {
  e.preventDefault();
  const btn = document.getElementById('btnUpload');
  btn.innerHTML = `<span class="pulse-ring" style="width:6px;height:6px;background:#ffffff;margin-right:6px;"></span> Parsing &amp; Indexing...`;
  btn.disabled = true;

  const fd = new FormData();
  if (selectedUploadFile) {
    fd.append('file', selectedUploadFile);
  } else {
    const companyVal = document.getElementById('uploadCompany').value || 'Company';
    const blob = new Blob(['Financial document sample content for indexing'], { type: 'application/pdf' });
    const name = companyVal.replace(/\s+/g, '_') + '_Annual_FY2026.pdf';
    fd.append('file', blob, name);
  }

  const companyName = document.getElementById('uploadCompany').value || 'Company';
  const yearVal = document.getElementById('uploadYear').value || 'FY2026';
  const docTypeVal = document.getElementById('uploadType').value || 'Annual Report (10-K)';

  fd.append('company', companyName);
  fd.append('year', yearVal);
  fd.append('docType', docTypeVal);

  try {
    const res = await fetch('/api/documents/upload', { method: 'POST', body: fd });
    const data = await res.json();

    if (data.success && data.document) {
      const newDoc = { ...data.document, _isNew: true };
      
      // 1. Prepend to in-memory FIN_DATA documents
      FIN_DATA.documents.unshift(newDoc);
      FIN_DATA.stats.documentsCount = FIN_DATA.documents.length;

      // 2. Prepend to agent activity log
      if (data.activity) {
        FIN_DATA.agentActivity.unshift(data.activity);
      } else {
        FIN_DATA.agentActivity.unshift({
          id: Date.now(),
          agent: 'Document Agent',
          action: `Parsed and indexed ${newDoc.name} (${newDoc.chunks} chunks)`,
          latency: '1.8s',
          time: 'Just now',
          status: 'success'
        });
      }

      // 3. Update UI counters
      const kd = document.getElementById('kpiDocs');
      if (kd) kd.textContent = FIN_DATA.documents.length;
      const bd = document.getElementById('navBadgeDocs');
      if (bd) bd.textContent = FIN_DATA.documents.length;

      // 4. Close modal and reset form
      closeModal('modalUploadDoc');
      document.getElementById('uploadForm').reset();
      document.getElementById('dropText').textContent = 'Click to browse file';
      selectedUploadFile = null;

      // 5. Sync company if created/updated
      if (data.company) {
        const existIdx = FIN_DATA.companies.findIndex(c => c.name.toLowerCase() === data.company.name.toLowerCase());
        if (existIdx >= 0) {
          FIN_DATA.companies[existIdx] = data.company;
        } else {
          FIN_DATA.companies.unshift(data.company);
        }
        renderCompanies();
        const kc = document.getElementById('kpiCompanies');
        if (kc) kc.textContent = FIN_DATA.companies.length;
      }

      // 6. Navigate directly to Documents view and re-render
      switchRoute('documents');
      renderDocsTable();
      renderActivityLog();

      // Sync report if returned
      if (data.report) {
        FIN_DATA.reports.unshift(data.report);
        FIN_DATA.stats.reportsCount = FIN_DATA.reports.length;
        const kr = document.getElementById('kpiReports');
        if (kr) kr.textContent = FIN_DATA.reports.length;
        renderReports();
      }

      // 7. Show vibrant toast confirmation with download link
      showToast(
        'Document Analyzed & Report Ready',
        `"${newDoc.name}" indexed and analyzed. Executive PDF report is compiled and ready for download in the Reports view!`,
        'success'
      );
    } else {
      showToast('Upload Failed', data.error || 'Server could not process file', 'error');
    }
  } catch (err) {
    showToast('Upload Error', 'Could not connect to server. Please try again.', 'error');
  } finally {
    btn.textContent = 'Index Document';
    btn.disabled = false;
  }
}

async function handleNewSession(e) {
  e.preventDefault();
  const name = document.getElementById('sessName').value;
  const desc = document.getElementById('sessDesc').value;
  const tags = document.getElementById('sessTags').value.split(',').map(t => t.trim()).filter(Boolean);

  await fetch('/api/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, description: desc, tags })
  });

  closeModal('modalNewSession');
  document.getElementById('sessionForm').reset();
  renderSessionsGrid();
  renderDashSessions();

  const ks = document.getElementById('kpiSessions');
  if (ks) ks.textContent = FIN_DATA.sessions.length;
}

async function handleGenReport(e) {
  e.preventDefault();
  const btn = document.getElementById('btnGenReport');
  btn.textContent = 'Synthesizing...';
  btn.disabled = true;

  const company = document.getElementById('repCompany').value;
  const recommendation = document.getElementById('repRec').value;

  try {
    await fetch('/api/reports/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company, recommendation })
    });
    closeModal('modalGenerateReport');
    renderReports();
    renderDashReports();
    renderActivityLog();
    const kr = document.getElementById('kpiReports');
    if (kr) kr.textContent = FIN_DATA.reports.length;
  } catch (err) {
    alert('Report generation failed.');
  } finally {
    btn.textContent = 'Execute Pipeline →';
    btn.disabled = false;
  }
}

// ========== UTILS ==========
function formatAnswer(text) {
  if (!text) return '';
  return text
    .replace(/^### (.*?)$/gm, '<h4 class="chat-sec-title">$1</h4>')
    .replace(/^## (.*?)$/gm, '<h3 class="chat-sec-main">$1</h3>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[(S\d+)\]/g, '<span class="cite-tag">[$1]</span>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n- /g, '<br><span class="bullet-dot">&bull;</span> ')
    .replace(/\n\d+\. /g, '<br><span class="bullet-dot">&bull;</span> ');
}

function escapeHTML(str) {
  return str.replace(/[&<>'"]/g, t => ({ '&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;' }[t] || t));
}
