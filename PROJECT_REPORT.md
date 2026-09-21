# 📊 Aegis Zero-Admin Mutual Fund Platform
## Enterprise Project Report & Trend Analysis Command Center

This comprehensive technical report provides an exhaustive, production-grade overview of the **Aegis Zero-Admin Mutual Fund Platform** (also known as the **FinTrend Analytics Dashboard**). It highlights the core business challenges faced by Asset Management Companies (AMCs), details the architecture, code-level implementation services, database resiliency strategies, cloud deployments, and native Windows automation scripts.

---

## 📌 Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Market Pain Points](#2-problem-statement--market-pain-points)
3. [Decoupled System Architecture](#3-decoupled-system-architecture)
4. [Resilient Dual-Engine Database Gateway](#4-resilient-dual-engine-database-gateway)
5. [Core Features & Business Workflows](#5-core-features--business-workflows)
6. [Core Service Logic Deep Dives](#6-core-service-logic-deep-dives)
7. [WORM Audit Trail Security & Database Triggers](#7-worm-audit-trail-security--database-triggers)
8. [AWS Cloud Infrastructure Deployment (IaC)](#8-aws-cloud-infrastructure-deployment-iac)
9. [PowerPoint COM Automation (VBScript Generator)](#9-powerpoint-com-automation-vbscript-generator)
10. [Local Installation & Verification](#10-local-installation--verification)

---

## 1. Executive Summary

The **Aegis Zero-Admin Mutual Fund Platform** is an advanced analytics command center designed for Asset Management Companies (AMCs) and portfolio managers. The platform consolidates critical operational capabilities—real-time transaction tracking, Assets Under Management (AUM) distribution, Systematic Investment Plan (SIP) trend analysis, compliance monitoring, machine-learning-driven investor churn prediction, returns benchmarking, and an AI-powered conversational advisor (FiNAI)—into a unified, resilient system.

Featuring a **decoupled three-tier architecture**, the platform implements a resilient **Dual-Engine Database Gateway** that guarantees operational availability by dynamically falling back from an AWS Supabase PostgreSQL instance to a local zero-admin SQLite instance during network interruptions. Furthermore, the platform incorporates write-once-read-many (WORM) audit security, complete AWS CloudFormation infrastructure templates (VPC, RDS, ECS Fargate, S3, CloudFront), and a native Windows VBScript COM automation generator that builds slide decks on demand.

---

## 2. Problem Statement & Market Pain Points

Asset Management Companies process billions of rupees in Systematic Investment Plans (SIPs) and lump-sum investments daily. However, legacy AMC software suffers from critical bottlenecks that increase risk and reduce profitability:

* **Latency in Analytics**: Portfolio managers lack real-time visibility into active AUM fluctuations and net flows (inflows vs. outflows), hindering rapid capital allocation and risk management during market hours.
* **Delayed Risk Mitigation**: Anti-Money Laundering (AML) and compliance checks are frequently executed post-settlement. This delay exposes AMCs to severe regulatory fines and security risks.
* **Unpredicted Client Churn**: AMCs struggle to detect early-stage churn signals (such as cancelled SIPs, heavy redemptions, or account inactivity). Without proactive customer outreach, they lose high-net-worth folios.
* **Tool Fragmentation**: Fund managers operate across multiple disjointed systems for portfolio logging, index benchmarking, stress testing, and scenario simulations.

---

## 3. Decoupled System Architecture

Aegis is architected as a decoupled, multi-tier web application to maximize performance, scalability, and fault tolerance.

```mermaid
graph TD
    %% Client Layer (React.js & Vite)
    subgraph Client_Layer [Frontend: React.js & Vite]
        A[Executive Dashboard] <--> |WS Live Link| WSClient[WebSocket Client]
        B[AUM / SIP Dashboards]
        C[AML / Churn / Benchmarking]
        D[AI Allocation Advisor - FiNAI]
    end

    %% Backend Server Layer (Express.js & WS)
    subgraph Server_Layer [Backend: Express.js Server]
        API[Express Router /api]
        WSS[WebSocket Server ws]
        SIM[Real-time Transaction Generator]
        SIM -->|Broadcasting| WSS
        WSS <-->|Live Updates| WSClient
    end

    %% Core Services & Rules Engines
    subgraph Business_Logic [Services & Heuristics]
        AML[Compliance/AML Rules Engine]
        ML[Churn Heuristics Engine]
    end

    %% Resilient Database Gateway Adapter
    subgraph Database_Layer [Database Gateway Adapter]
        DBA[Boot Coordinator db.js]
        PG[AWS Supabase PostgreSQL 16 Pool]
        SQLITE[Zero-Admin Local SQLite 3 Fallback]
    end

    %% Network & Database Mappings
    A & B & C & D -->|HTTP REST Requests| API
    API --> AML & ML
    AML & ML --> DBA
    DBA -->|Verify Connection & Connect| PG
    DBA -->|Graceful Fallback If Offline| SQLITE
```

### Technical Stack Details
* **Frontend**:
  * **Framework**: React.js (v18) built with Vite for rapid bundling.
  * **Visualizations**: Chart.js via `react-chartjs-2`, configured with custom dark-mode themes, canvas glow effects, and sparklines.
  * **Icons**: `lucide-react` for consistent dashboard iconography.
  * **Styling**: Vanilla CSS3 using design variables, CSS grids, flexbox layouts, glassmorphism containers, and smooth state transitions.
* **Backend**:
  * **Environment**: Node.js with Express.js REST APIs.
  * **Real-time Server**: Native WebSocket server (`ws` package) for client-server pushing.
  * **Simulation**: Event-driven transaction simulator generating mock investor transactions and compliance exceptions.
* **Database & Persistence**:
  * **Production Engine**: Remote PostgreSQL 16 database hosted on Supabase, featuring performance indices and PL/pgSQL database triggers.
  * **Resilient Fallback**: Zero-configuration local SQLite 3 instance using a unified gateway wrapper (`db.js`).

---

## 4. Resilient Dual-Engine Database Gateway

One of Aegis's standout innovations is its resilient **Dual-Engine Database Gateway** (`backend/database/db.js`), which handles schema setup, connection pooling, and connection failures. 

### Boot Coordinator Connection Fallback
During backend startup, the boot coordinator tests connection to the remote PostgreSQL database. If PostgreSQL fails to respond within a 10-second timeout window, the coordinator catches the error and initializes the local SQLite database.

This unified gateway adapter abstracts query execution from the underlying driver:

```javascript
// db.js (Gateway Interaction Routines)
const dbPg = require('./db_pg.js');
const { sqliteQuery, initializeSQLiteDatabase } = require('./sqlite');

let activeEngine = 'sqlite'; // Default to SQLite fallback

const dbQuery = {
  async run(sql, params = []) {
    return activeEngine === 'postgres' ? dbPg.dbQuery.run(sql, params) : sqliteQuery.run(sql, params);
  },
  async get(sql, params = []) {
    return activeEngine === 'postgres' ? dbPg.dbQuery.get(sql, params) : sqliteQuery.get(sql, params);
  },
  async all(sql, params = []) {
    return activeEngine === 'postgres' ? dbPg.dbQuery.all(sql, params) : sqliteQuery.all(sql, params);
  },
  async exec(sql) {
    return activeEngine === 'postgres' ? dbPg.dbQuery.exec(sql) : sqliteQuery.exec(sql);
  }
};
```

---

## 5. Core Features & Business Workflows

The dashboard compiles nine essential mutual fund operations into a unified dark-theme user experience.

### 5.1 Executive Dashboard & Live Broadcast
* **WebSocket Integration**: Connects to the backend server to receive live transaction streams. Metrics cards (Total AUM, Active Investors, Active SIPs, Redemptions, Net Inflows) update dynamically.
* **Glow Metrics Cards**: Displays values accompanied by 30-day canvas sparklines to visualize trends.
* **Market Indices Ticker**: Displays a live, rolling horizontal ticker of indices (`NIFTY 50`, `SENSEX`, `NIFTY 500`, `VIX`, `10Y G-SEC`, `GOLD`) with real-time price fluctuations.
* **Live Notifications Drawer**: A slide-out panel that displays operational notifications, compliance alerts, and system statuses.

### 5.2 AUM Analytics
* **AUM Growth Over Time**: Charts growth parameters (Daily, Monthly, Yearly) using custom line graphs.
* **Asset Allocation Distribution**: Doughnut charts display the distribution across categories (Equity, Hybrid, Debt, ELSS, Sectoral).
* **Geographical Investor Concentration**: Shows AUM density across Indian states (Maharashtra, Delhi NCR, Karnataka, Gujarat, Tamil Nadu, etc.).

### 5.3 SIP Trend Analysis & Stoppage Monitor
* **Active Mandates**: Tracks monthly SIP registrations, active mandates, average ticket sizes, and cancellation volumes.
* **SIP Stoppage Ratio**: Calculates the ratio of cancelled/paused SIPs against new registrations. If this ratio crosses a predefined threshold, the interface flags a warning status.

### 5.4 Interactive Transaction Heatmap
* **2D Calendar Matrix**: Renders transaction density by hour of the day (9:00 AM - 5:00 PM) and day of the week (Monday - Sunday) using dynamic color-intensity scales.
* **Peak Utilization Analysis**: Enables operations teams to identify peak load times and schedule maintenance windows during low-traffic periods.

### 5.5 AML & Compliance
* **Real-time Checks**: Algorithms flag high-value transfers (e.g., single transactions exceeding ₹30 Cr) or rapid transaction velocity.
* **Case Management**: Provides Compliance Officers with tools to assign alerts, add resolution logs, and resolve or escalate cases (e.g., filing a Suspicious Transaction Report).

### 5.6 Churn Prediction Dashboard
* **Risk Vector Analysis**: Calculates investor churn probabilities based on key parameters: transaction recency, redemption volumes, and active/cancelled SIP schedules.
* **Targeted Outreach Campaign**: Enables portfolio managers to launch retention campaigns with a single click. The backend registers a 15 basis point fee waiver (`RELATIONSHIP15`) and logs the outreach.

### 5.7 AI Allocation Advisor (FiNAI)
* **Natural Language Queries**: Integrates an AI chat panel that processes natural language queries about fund NAVs, stoppage ratios, and asset weights.
* **Stress Testing Simulation**: Simulates hypothetical market corrections (e.g., a 10% market correction) and calculates projected asset drawdowns.
* **Beta/Sharpe Ratio Optimization**: Compares current portfolio allocations with optimized allocations to reduce portfolio beta and increase Sharpe ratios.

### 5.8 Performance Benchmarking
* **Relative Returns**: Charts mutual fund performances against indices like the NIFTY 50 Total Returns Index (TRI).
* **Fund Health Cards**: Compares portfolio Alpha, Tracking Error, Information Ratio, Sharpe Ratio, and Category Rank against industry averages.

### 5.9 Report Generator & Notes Pad
* **PDF / CSV Export Engine**: Compiles transactions, fund performances, and compliance histories into export-ready documents.
* **Fund Manager Diary**: A persistent notepad that auto-saves notes to local storage. It includes an export feature to download notes as a `.txt` file.

---

## 6. Core Service Logic Deep Dives

### 6.1 Random Forest Machine Learning Classifier (`analytics.service.js`)
The platform calculates an investor's churn risk using an ensemble **Random Forest Classifier** model trained dynamically in Node.js. 

For each investor, the service extracts a 3-dimensional feature vector:
1. **Activity Recency**: Days elapsed since the investor's last transaction (defaulting to 365 if no trades exist).
2. **Redemption Ratio**: Cumulative withdrawals/redemptions relative to total capital inflows (range $0.0$ to $1.0$).
3. **SIP Mandate Status**: Categorical mapping of Systematic Investment Plan active states:
   * `0` = Active mandates only
   * `1` = No active or historical mandates
   * `2` = Paused mandates
   * `3` = Cancelled mandates

#### Ensemble Prediction Mechanics
The Random Forest model consists of 50 bootstrap-trained `DecisionTree` structures built using Shannon Entropy and Information Gain metrics:
$$\text{Entropy}(y) = -\sum p_i \log_2(p_i)$$
$$\text{Information Gain} = \text{Entropy}_{\text{parent}} - \sum \frac{N_{\text{child}}}{N_{\text{parent}}} \text{Entropy}_{\text{child}}$$

Each tree votes (predicting `0` for retention or `1` for churn). The final churn risk probability is computed as:
$$\text{Churn Risk Score} = \text{CappedBetween}(5\%, 95\%, \frac{\text{Trees predicting 1}}{\text{Total Trees}} \times 100)$$

Scores above $60\%$ are categorized as **HIGH RISK** and flagged for retention outreach campaigns.

---

## 7. WORM Audit Trail Security & Database Triggers

To meet strict regulatory compliance standards (such as SEBI and SEC guidelines), the database enforces a **Write-Once-Read-Many (WORM)** policy on the `audit_logs` table.

This policy is enforced at the database level using PL/pgSQL triggers that block updates or deletes, ensuring that the audit history remains immutable:

```sql
-- triggers.js
CREATE OR REPLACE FUNCTION lock_audit_log_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Immutability Violation: Audit log entries cannot be modified or deleted.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER lock_audit_log_updates
BEFORE UPDATE ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION lock_audit_log_modification();

CREATE TRIGGER lock_audit_log_deletes
BEFORE DELETE ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION lock_audit_log_modification();
```

---

## 8. AWS Cloud Infrastructure Deployment (IaC)

Aegis includes full infrastructure-as-code configuration templates (`aws/template.yaml`) designed for AWS Serverless Application Model (SAM) or CloudFormation.

```
aws/
├── template.yaml            # Parent template establishing parameters & resource links
└── components/
    ├── networking.yaml      # VPC, Isolated Subnets (2 AZs), Route Tables, NAT Gateways
    ├── database.yaml        # RDS PostgreSQL inside private subnets
    ├── backend.yaml         # ECS Fargate Cluster, Task Definitions, Application Load Balancer
    └── frontend.yaml        # S3 Static Web Hosting synchronized with CloudFront CDN
```

### Infrastructure Stack Components
1. **`networking.yaml`**: Configures a highly available VPC layout. It provisions public subnets for the load balancers, and private subnets with NAT Gateways for the container tasks and databases.
2. **`database.yaml`**: provisions an Amazon RDS PostgreSQL 16 instance. It is deployed within isolated private subnets and configured with security groups that only accept traffic from ECS containers.
3. **`backend.yaml`**: Runs the Express.js server inside ECS Fargate container instances. The containers are managed by an Application Load Balancer (ALB) that handles SSL termination.
4. **`frontend.yaml`**: Deploys the built React.js single-page application to Amazon S3. An Amazon CloudFront CDN distribution caches assets globally for low-latency delivery.

---

## 9. PowerPoint COM Automation (VBScript Generator)

Aegis includes a native Windows VBScript file (`generate_presentation.vbs`) that automates slide generation. This script uses Windows Component Object Model (COM) interfaces to launch Microsoft PowerPoint and build a 16:9 widescreen presentation deck on demand.

### PowerPoint COM Architecture
The script establishes the dark-slate theme and constructs slides programmatically:

* **Slide 1**: Title slide featuring the platform's color palette (Slate 900 background, Slate 800 cards, and Sapphire Blue borders).
* **Slide 2**: Problem Statement slide detailing legacy AMC issues.
* **Slide 3**: Proposed Solution slide outlining the real-time engine and the dual-engine database.
* **Slide 4**: System Architecture slide mapping the decoupled React frontend, Express.js server, and database layer.
* **Slide 5**: System Architecture & Tech Stack diagram.
* **Slide 6**: Operational Workflow lifecycle.
* **Slide 7**: Core features quadrant.
* **Slide 8**: Summary and roadmap slide.

This script executes locally on Windows systems containing Microsoft PowerPoint.

---

## 10. Local Installation & Verification

To test the application locally, verify that you have Node.js (v18+) and npm installed.

### 10.1 Environment Configuration
Create a `.env` file in the project root:

```env
PORT=5000
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mutual_fund_platform
SEED_DATABASE=true
```

### 10.2 Installation and Run Command
Aegis contains configured root scripts that manage dependencies and servers:

```bash
# 1. Clone the repository
git clone https://github.com/lalathegreat/SIP-Trend-Analysis.git
cd SIP-Trend-Analysis

# 2. Install dependencies for the root, frontend, and backend packages
npm run install-all

# 3. Spin up the Express.js backend and React client concurrently
npm run dev
```

The system will boot up:
* The Express.js API server will start on [http://localhost:5000](http://localhost:5000).
* The Vite client will launch on [http://localhost:5173](http://localhost:5173).
* If PostgreSQL is unreachable, the server will fall back to SQLite, creating `backend/database/database.sqlite` automatically.

---
*Report compiled by the Aegis Architecture Group.*
