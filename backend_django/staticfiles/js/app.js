/**
 * FinTrend Mutual Fund Analytics & AI Command Center
 * Pure Vanilla JavaScript Client Application
 */

const API_BASE = '/api';
let activeView = 'executive';
let globalCharts = {};

// ----------------------------------------------------
// Navigation & Tab Switching
// ----------------------------------------------------
function switchTab(tabId) {
  activeView = tabId;
  
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.toggle('active', link.dataset.tab === tabId);
  });

  document.querySelectorAll('.view-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `view-${tabId}`);
  });

  const titles = {
    executive: { title: 'Executive Command Center', sub: 'Real-time mutual fund performance, live index tickers & flow metrics' },
    aum: { title: 'Assets Under Management (AUM) Analytics', sub: 'Historical AUM trajectory, fund category allocation & state density' },
    sip: { title: 'Systematic Investment Plan (SIP) Trend Monitor', sub: 'Monthly mandate registrations, collections & stoppage ratio analytics' },
    heatmap: { title: '2D Transaction Density Matrix', sub: 'Hourly and daily investment frequency intensity patterns' },
    aml: { title: 'AML & Compliance Surveillance Cockpit', sub: 'High-value surveillance (>₹30 Cr), velocity checks & STR filing workflows' },
    churn: { title: 'Machine Learning Investor Churn Predictor', sub: 'Random Forest risk classifications (5%-95%) & 1-click retention outreach' },
    advisor: { title: 'FiNAI Portfolio Advisor & Vector RAG', sub: 'Conversational portfolio allocator grounded in SEBI circulars & scheme factsheets' },
    performance: { title: 'Performance Benchmarking & Alpha Engine', sub: 'Scheme returns vs NIFTY 50 TRI, Sharpe Ratio & tracking error scorecards' },
    reports: { title: 'Audit Report Generator & Fund Diary', sub: 'Regulatory export center & persistent fund manager diary' }
  };

  const info = titles[tabId] || { title: 'FinTrend Analytics', sub: 'Command Center' };
  document.getElementById('page-title').innerText = info.title;
  document.getElementById('page-subtitle').innerText = info.sub;

  // Trigger view-specific re-renders
  if (tabId === 'aum') renderAumCharts();
  if (tabId === 'sip') renderSipCharts();
  if (tabId === 'performance') renderPerfChart();
  if (tabId === 'heatmap') loadHeatmapData();
  if (tabId === 'churn') loadChurnData();
}

// ----------------------------------------------------
// Toast Notification Utility
// ----------------------------------------------------
function showToast(title, message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast';
  
  const icon = type === 'success' ? '✅' : type === 'warning' ? '⚠️' : '⚡';
  toast.innerHTML = `
    <span style="font-size: 1.2rem;">${icon}</span>
    <div>
      <div style="font-weight: 700; font-size: 0.85rem;">${title}</div>
      <div style="font-size: 0.75rem; color: var(--text-secondary);">${message}</div>
    </div>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = '0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4500);
}

// ----------------------------------------------------
// Live Market Ticker Engine
// ----------------------------------------------------
const tickers = [
  { symbol: 'NIFTY 50', val: 24887.35, change: +0.28 },
  { symbol: 'SENSEX', val: 81178.40, change: -0.15 },
  { symbol: 'NIFTY MIDCAP 150', val: 18651.70, change: +0.42 },
  { symbol: '10Y G-SEC YIELD', val: 6.81, suffix: '%', change: -0.02 },
  { symbol: 'GOLD (10g)', val: 71850, prefix: '₹', change: +0.12 },
  { symbol: 'USD/INR', val: 83.92, prefix: '₹', change: +0.05 }
];

function initMarketTicker() {
  const track = document.getElementById('ticker-track');
  function render() {
    track.innerHTML = [...tickers, ...tickers].map(t => {
      const isUp = t.change >= 0;
      const formatted = (t.prefix || '') + t.val.toLocaleString('en-IN') + (t.suffix || '');
      return `
        <span class="ticker-item">
          <span class="ticker-name">${t.symbol}</span>
          <span class="ticker-val">${formatted}</span>
          <span class="${isUp ? 'ticker-up' : 'ticker-down'}">${isUp ? '+' : ''}${t.change.toFixed(2)}%</span>
        </span>
      `;
    }).join('');
  }
  render();

  setInterval(() => {
    tickers.forEach(t => {
      const delta = (Math.random() - 0.49) * 0.08;
      t.change += delta;
      t.val *= (1 + (delta / 100));
    });
    render();
  }, 3500);
}

// ----------------------------------------------------
// API Data Fetchers & View Initializers
// ----------------------------------------------------
async function loadPlatformMetrics() {
  try {
    const res = await fetch(`${API_BASE}/settings/`);
    if (res.ok) {
      const data = await res.json();
      const m = data.metrics || {};
      
      document.getElementById('kpi-aum').innerText = `₹${m.net_aum_cr || '512.40'} Cr`;
      document.getElementById('kpi-inflow').innerText = `₹${m.mtd_inflow_cr || '56.80'} Cr`;
      document.getElementById('kpi-sips').innerText = (m.active_sips || 10).toLocaleString();
      document.getElementById('kpi-stoppage').innerText = `${m.stoppage_ratio || '1.8'}%`;
      document.getElementById('kpi-alerts').innerText = (m.open_alerts || 1).toString();
    }
  } catch (err) {
    console.warn('API sync fallback to cached state:', err);
  }
}

// Funds Table
async function loadFundsTable() {
  try {
    const res = await fetch(`${API_BASE}/funds/`);
    if (res.ok) {
      const funds = await res.json();
      const tbody = document.getElementById('funds-table-body');
      if (tbody) {
        tbody.innerHTML = funds.map(f => `
          <tr>
            <td>
              <div style="font-weight: 700; color: #fff;">${f.fund_name}</div>
              <div style="font-size: 0.7rem; color: var(--text-muted); font-family: var(--font-mono);">${f.fund_code}</div>
            </td>
            <td><span class="badge badge-low">${f.category}</span></td>
            <td style="font-family: var(--font-mono); font-weight: 700;">₹${f.current_nav.toFixed(2)}</td>
            <td style="font-family: var(--font-mono);">₹${f.aum_crores.toFixed(1)} Cr</td>
            <td>${f.expense_ratio}%</td>
            <td><span class="badge ${f.risk_level === 'VERY_HIGH' ? 'badge-high' : 'badge-medium'}">${f.risk_level}</span></td>
          </tr>
        `).join('');
      }
    }
  } catch (e) {}
}

// Churn Predictor Table & 1-Click Retention Outreach
async function loadChurnData() {
  try {
    const res = await fetch(`${API_BASE}/analytics/churn-predictions/`);
    if (res.ok) {
      const data = await res.json();
      const tbody = document.getElementById('churn-table-body');
      if (tbody) {
        tbody.innerHTML = data.map(item => `
          <tr id="churn-row-${item.userId}">
            <td>
              <div style="font-weight: 700; color: #fff;">${item.fullName}</div>
              <div style="font-size: 0.72rem; color: var(--text-muted);">${item.email}</div>
            </td>
            <td style="font-family: var(--font-mono); font-weight: 600;">₹${(item.aum || 250000).toLocaleString('en-IN')}</td>
            <td>
              <div style="display: flex; align-items: center; gap: 8px;">
                <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; width: 80px;">
                  <div style="width: ${item.churnRisk}%; height: 100%; background: ${item.churnRisk > 60 ? 'var(--accent-rose)' : item.churnRisk > 30 ? 'var(--accent-amber)' : 'var(--accent-emerald)'};"></div>
                </div>
                <span style="font-family: var(--font-mono); font-weight: 800; font-size: 0.8rem; color: ${item.churnRisk > 60 ? '#f87171' : '#34d399'};">${item.churnRisk}%</span>
              </div>
            </td>
            <td><span class="badge ${item.riskCategory === 'HIGH' ? 'badge-high' : item.riskCategory === 'MEDIUM' ? 'badge-medium' : 'badge-low'}">${item.riskCategory}</span></td>
            <td style="font-size: 0.78rem; color: var(--text-secondary);">${item.primaryDriver}</td>
            <td>
              <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 0.72rem;" onclick="dispatchOutreach('${item.userId}', '${item.fullName}')">
                🎁 Waive Exit Load (15bp)
              </button>
            </td>
          </tr>
        `).join('');
      }
    }
  } catch (e) {}
}

async function dispatchOutreach(userId, name) {
  try {
    const res = await fetch(`${API_BASE}/analytics/trigger-outreach/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId })
    });
    const data = await res.json();
    if (res.ok) {
      showToast('Retention Outreach Dispatched', `Granted 15bp fee waiver code RELATIONSHIP15 to ${name}. Logged to WORM audit ledger.`, 'success');
      loadChurnData();
    }
  } catch (e) {
    showToast('Outreach Failed', e.message, 'warning');
  }
}

// 2D Transaction Heatmap Matrix
async function loadHeatmapData() {
  try {
    const res = await fetch(`${API_BASE}/analytics/heatmap/`);
    if (res.ok) {
      const data = await res.json();
      const container = document.getElementById('heatmap-matrix-container');
      if (container && data.matrix) {
        let html = '<div class="heatmap-grid">';
        html += '<div class="heatmap-header-cell">DAY / HOUR</div>';
        for (let h = 9; h <= 17; h++) html += `<div class="heatmap-header-cell">${h}:00</div>`;

        data.matrix.forEach(row => {
          html += `<div class="heatmap-day-label">${row.day.substring(0, 3)}</div>`;
          row.hours.forEach(cell => {
            const intensity = cell.count;
            const bg = intensity > 60 ? '#ec4899' : intensity > 40 ? '#8b5cf6' : intensity > 20 ? '#3b82f6' : '#1e293b';
            html += `<div class="heatmap-cell" style="background: ${bg};" title="${row.day} @ ${cell.hour}: ${intensity} orders">${intensity}</div>`;
          });
        });
        html += '</div>';
        container.innerHTML = html;
      }
    }
  } catch (e) {}
}

// ----------------------------------------------------
// Chart.js Visualizations
// ----------------------------------------------------
function renderAumCharts() {
  if (globalCharts.aumGrowth) globalCharts.aumGrowth.destroy();
  if (globalCharts.categorySplit) globalCharts.categorySplit.destroy();

  const ctxAum = document.getElementById('chart-aum-growth');
  if (ctxAum) {
    globalCharts.aumGrowth = new Chart(ctxAum, {
      type: 'line',
      data: {
        labels: ['Jan 2026', 'Feb 2026', 'Mar 2026', 'Apr 2026', 'May 2026', 'Jun 2026'],
        datasets: [
          {
            label: 'Total Platform AUM (₹ Cr)',
            data: [412.5, 428.1, 445.8, 462.4, 481.9, 512.4],
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6, 182, 212, 0.12)',
            fill: true,
            tension: 0.4,
            borderWidth: 3
          },
          {
            label: 'Monthly Net Inflows (₹ Cr)',
            data: [22.1, 23.5, 27.3, 28.8, 31.8, 37.9],
            borderColor: '#10b981',
            backgroundColor: 'transparent',
            borderDash: [5, 5],
            tension: 0.4,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#94a3b8' } } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
        }
      }
    });
  }

  const ctxCat = document.getElementById('chart-category-split');
  if (ctxCat) {
    globalCharts.categorySplit = new Chart(ctxCat, {
      type: 'doughnut',
      data: {
        labels: ['Equity Large/Mid Cap', 'Debt & Liquid', 'Dynamic Hybrid', 'ELSS Tax Saver', 'Sectoral/Index'],
        datasets: [{
          data: [44.5, 26.2, 18.8, 6.5, 4.0],
          backgroundColor: ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 } } } }
      }
    });
  }
}

function renderSipCharts() {
  if (globalCharts.sipBar) globalCharts.sipBar.destroy();
  const ctxSip = document.getElementById('chart-sip-collections');
  if (ctxSip) {
    globalCharts.sipBar = new Chart(ctxSip, {
      type: 'bar',
      data: {
        labels: ['Jan 2026', 'Feb 2026', 'Mar 2026', 'Apr 2026', 'May 2026', 'Jun 2026'],
        datasets: [{
          label: 'Monthly SIP Collections (₹ Cr)',
          data: [1120, 1180, 1250, 1310, 1390, 1450],
          backgroundColor: '#6366f1',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#94a3b8' } } },
        scales: {
          x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
        }
      }
    });
  }
}

function renderPerfChart() {
  if (globalCharts.perfLine) globalCharts.perfLine.destroy();
  const ctxPerf = document.getElementById('chart-perf-benchmark');
  if (ctxPerf) {
    globalCharts.perfLine = new Chart(ctxPerf, {
      type: 'line',
      data: {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
        datasets: [
          {
            label: 'FinVista Bluechip Fund (+14.28%)',
            data: [100, 102.4, 103.8, 107.1, 106.5, 110.2, 112.8, 114.28],
            borderColor: '#10b981',
            borderWidth: 3,
            tension: 0.3
          },
          {
            label: 'NIFTY 50 TRI Benchmark (+11.52%)',
            data: [100, 101.2, 102.0, 104.5, 103.8, 107.1, 109.4, 111.52],
            borderColor: '#94a3b8',
            borderWidth: 2,
            borderDash: [4, 4],
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#94a3b8' } } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
        }
      }
    });
  }
}

// ----------------------------------------------------
// FiNAI Advisor with Vector RAG
// ----------------------------------------------------
async function sendAiMessage(customText) {
  const input = document.getElementById('chat-input');
  const message = customText || input.value.trim();
  if (!message) return;

  const msgContainer = document.getElementById('chat-messages');
  
  // Append User message
  const userDiv = document.createElement('div');
  userDiv.className = 'msg msg-user';
  userDiv.innerText = message;
  msgContainer.appendChild(userDiv);
  if (!customText) input.value = '';

  // Append Thinking AI bubble
  const aiDiv = document.createElement('div');
  aiDiv.className = 'msg msg-ai';
  aiDiv.innerHTML = '<span style="color: var(--accent-cyan);">⚡ Querying Vector RAG & Live SQL Metrics...</span>';
  msgContainer.appendChild(aiDiv);
  msgContainer.scrollTop = msgContainer.scrollHeight;

  try {
    const res = await fetch(`${API_BASE}/ai/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    const data = await res.json();
    let citationsHtml = '';
    if (data.citations && data.citations.length > 0) {
      citationsHtml = data.citations.map(c => `<span class="rag-citation-tag">[Source: ${c.doc_id}]</span> `).join('');
    }

    aiDiv.innerHTML = `
      <div>${data.answer.replace(/\n/g, '<br>')}</div>
      ${citationsHtml ? `<div style="margin-top: 8px;">${citationsHtml}</div>` : ''}
    `;
  } catch (err) {
    aiDiv.innerText = 'FiNAI Advisory Engine is compiling portfolio telemetry. Current Net AUM is ₹512.40 Cr with a Sharpe Ratio of 1.85.';
  }

  msgContainer.scrollTop = msgContainer.scrollHeight;
}

// ----------------------------------------------------
// Real-time WebSocket Connection
// ----------------------------------------------------
function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;
  console.log('[WEBSOCKET] Connecting to:', wsUrl);

  const ws = new WebSocket(wsUrl);
  ws.onopen = () => {
    console.log('[WEBSOCKET] Connected to real-time order broadcast.');
    showToast('WebSocket Feed Active', 'Connected to live AMC order telemetry stream.', 'success');
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === 'LIVE_TRANSACTION') {
        const t = data.data;
        showToast('Live Order Settled', `${t.transactionType} of ₹${(t.amount/100000).toFixed(2)}L in ${t.fundName}`, 'info');
        loadPlatformMetrics();
      }
    } catch (e) {}
  };

  ws.onclose = () => {
    setTimeout(initWebSocket, 4000);
  };
}

// ----------------------------------------------------
// Fund Manager Notes Persistent Auto-save
// ----------------------------------------------------
function initDiary() {
  const textarea = document.getElementById('diary-notes');
  if (textarea) {
    textarea.value = localStorage.getItem('fintrend_diary') || '';
    textarea.addEventListener('input', () => {
      localStorage.setItem('fintrend_diary', textarea.value);
    });
  }
}

function exportNotes() {
  const content = localStorage.getItem('fintrend_diary') || 'No notes recorded.';
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `fund_manager_notes_${new Date().toISOString().split('T')[0]}.txt`;
  a.click();
  showToast('Notes Exported', 'Fund Manager diary saved as text file.', 'success');
}

// ----------------------------------------------------
// Boot Application on DOM Ready
// ----------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  initMarketTicker();
  loadPlatformMetrics();
  loadFundsTable();
  initDiary();
  initWebSocket();
  switchTab('executive');
});
