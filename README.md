# 📊 FinTrend Analytics Command Center (Django + Python + SQL + AI/ML + RAG)

A comprehensive, enterprise-grade **FinTech Mutual Fund Analytics & AI Command Center** built using **Django 6.1**, **Python 3.14**, **SQL (PostgreSQL / SQLite)**, **Scikit-Learn Random Forest Classifier**, and a **Vector Retrieval-Augmented Generation (RAG) Engine**, coupled with a dark-mode **React.js (Vite + Chart.js)** frontend.

---

## 🚀 Key Modules & Capabilities

### 1. 🤖 Data Science & AI/ML
* **Random Forest Investor Churn Predictor**: Behavioral feature extraction (Recency, Redemption Ratio, SIP Status), risk cohort segmentation (LOW, MEDIUM, HIGH), and 1-click retention outreach with fee waiver codes (`RELATIONSHIP15`).
* **Vector RAG Engine**: Semantic vector search over authoritative financial knowledge bases:
  - SEBI Mutual Fund Categorization & Investment Directives (`SEBI-CAT-2026`)
  - Scheme Information Documents & Fund Factsheets (`FACT-FV-BC-001`, `FACT-APX-MC-002`, `FACT-PRM-HY-003`)
  - AML / CFT Compliance & Suspicious Transaction Reporting SOPs (`AML-SOP-2026`)
  - Portfolio Risk Management & Liquidity Coverage Directives (`RISK-POLICY-2026`)
* **FiNAI Allocation Advisor**: Conversational intelligence combining real-time SQL platform aggregations with retrieved regulatory RAG citations, downside stress testing simulation, and Sharpe/Beta optimization.
* **AML Anomaly Surveillance**: Real-time transaction surveillance flagging high-value transfers (> ₹30 Cr threshold) and risk scoring.

### 2. 🏛️ Django REST Backend (`backend_django/`)
* **Relational SQL Database Models**: 13 tables (`users`, `funds`, `investments`, `transactions`, `sip_schedules`, `compliance_checks`, `compliance_alerts`, `audit_logs`, `kyc_records`, `kyc_documents`, `cfa_approvals`, `notifications`, `system_users`).
* **WORM Compliance Security**: Write-Once-Read-Many immutable audit ledger.
* **WebSocket Live Link**: Real-time order broadcasting over `/ws`.

### 3. 📈 Interactive Analytics Dashboards (`frontend/`)
* **Executive Dashboard**: Live market index ticker, glowing metrics, 30-day sparklines, and active folio counts.
* **AUM Analytics**: Time-series AUM growth, fund category distribution, and state-wise concentration.
* **SIP Trend Analysis**: Mandate status controls, cancellation tracking, and SIP Stoppage Ratio monitor.
* **2D Transaction Heatmap**: Calendar intensity matrix by hour of day and day of week.
* **AML & Compliance Alerts**: Real-time surveillance feed, case review workflows, and STR filing.
* **Performance Benchmarking**: Relative returns vs NIFTY 50 TRI, portfolio Alpha, Information Ratio, and Sharpe Ratio.
* **Report Generator & Fund Manager Diary**: PDF/CSV exports and persistent notes editor.

---

## 📂 Project Structure

```text
FinTrend-Analysis/
├── backend_django/                      # Django REST Backend & ML/RAG Engines
│   ├── fintrend/                       # ASGI, WSGI, Settings, Root URLs
│   ├── analytics_api/                  # Models, Views, Serializers, Tests
│   │   ├── ml/                         # Random Forest Churn, RAG Engine, FiNAI Advisor, AML
│   │   └── services/                   # WORM Audit Logger, Simulator
│   ├── requirements.txt                # Python Dependencies
│   └── manage.py                       # Django CLI
├── frontend/                           # React 19 + Vite + Chart.js Dashboard
├── run_platform.py                     # Unified Boot Script
├── package.json
└── README.md
```

---

## ⚙️ Installation & Running

### 1. Install Python & Node Dependencies
```bash
# Python dependencies
pip install -r backend_django/requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Launch the Entire Platform
```bash
python run_platform.py
```

### 3. Run Automated Tests
```bash
cd backend_django
python manage.py test
```

Open your browser at:
```
http://localhost:5173
```