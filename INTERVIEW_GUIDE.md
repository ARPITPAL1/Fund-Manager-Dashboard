# 📊 FinTrend Analytics & AI Command Center: Interview Master Guide

This document is your complete interview preparation manual for the **FinTrend Mutual Fund Analytics & AI Command Center**.

---

## 🎯 Quick Elevator Pitch (Memorize for Introductions)
> *"FinTrend is an enterprise-grade Mutual Fund Analytics Command Center built for Asset Management Companies (AMCs). It combines a **Python 3.14 + Django REST** backend with a resilient **SQL database** (PostgreSQL/SQLite), an automated **Random Forest Classifier** for client churn prediction, and a **Vector RAG (Retrieval-Augmented Generation)** engine that grounds conversational AI advice in official SEBI circulars and scheme factsheets. On the frontend, it features a **React 19 + Chart.js** dark-mode analytics cockpit with real-time WebSocket transaction streaming."*

---

## 🗄️ Database Architecture (SQL & Django ORM)
- **13 Relational Tables**: `users`, `funds`, `investments`, `transactions`, `sip_schedules`, `compliance_checks`, `compliance_alerts`, `audit_logs`, `kyc_records`, `kyc_documents`, `cfa_approvals`, `notifications`, `system_users`.
- **WORM Immutability**: Write-Once-Read-Many policy enforced on `audit_logs` where deletes/edits are blocked at the application level to comply with SEBI/SEC regulatory audit requirements.
- **Double-Entry Financial Ledger**: Tracks purchase, redemption, SIP auto-debits, and NAV unit allocations.

---

## 🧠 Data Science, AI/ML & RAG Architecture
1. **Supervised ML: Investor Churn Classifier**:
   - Model: Scikit-Learn **Random Forest** (100 decision trees).
   - Features: Activity Recency ($X_1$), Redemption Ratio ($X_2$), SIP Mandate Status ($X_3$).
   - Output: Churn probability score ($5\% - 95\%$), cohort segmentation (LOW, MEDIUM, HIGH), and 1-click fee waiver retention campaign dispatch.
2. **Vector RAG Engine**:
   - Ingests SEBI circulars (`SEBI-CAT-2026`), Scheme Information Documents (`FACT-FV-BC-001`), and AML SOPs (`AML-SOP-2026`).
   - Vector indexing with cosine similarity search.
   - Injects top-$k$ retrieved facts into FiNAI AI responses with verifiable source citations.
3. **Quantitative Portfolio Optimizer (FiNAI Advisor)**:
   - Evaluates portfolio Beta ($\beta = 0.92$), Sharpe Ratio ($S = 1.85$), and Liquidity Coverage Ratio ($LCR = 95\%$).
   - Downside Stress Testing: Simulates market drops ($-5\%, -10\%, -15\%, -20\%$) and calculates downside protection Alpha ($+1.60\%$).
4. **Real-Time AML Surveillance**:
   - Flagging single transactions $> \text{₹30 Cr}$ or velocity spikes with automated case resolution workflows.

---

## 💡 Top 5 Technical Interview Q&As:
1. **Why Django over Node.js?** — Strong ACID compliance, relational integrity, and native Python ecosystem integration for ML models (Scikit-Learn, Pandas) and Vector RAG in a unified runtime.
2. **How does RAG prevent hallucinations?** — It performs semantic search over pre-indexed regulatory documents and scheme factsheets, passing exact excerpts into the LLM prompt with strict citation constraints.
3. **What is WORM?** — Write-Once-Read-Many. Ensures audit logs cannot be modified or deleted, preserving regulatory evidentiary integrity.
4. **How does the Churn model work?** — Extracts a 3D feature vector from SQL transactions and predicts probability via 100 decision trees.
5. **How is real-time streaming achieved?** — Native WebSockets via Django Channels / Daphne ASGI broadcasting JSON events directly to connected clients.
