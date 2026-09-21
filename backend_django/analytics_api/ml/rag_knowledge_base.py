"""
Financial Knowledge Base Corpus for RAG (Retrieval-Augmented Generation) Engine.
Contains authoritative documents covering:
1. SEBI Mutual Fund Categorization & Investment Directives
2. Scheme Information Documents (SID) & Scheme Factsheets
3. AML / CFT Compliance Guidelines & PMLA Directives
4. Portfolio Risk Management & Liquidity Coverage Directives
"""

FINANCIAL_KNOWLEDGE_CORPUS = [
    {
        "doc_id": "SEBI-CAT-2026",
        "title": "SEBI Mutual Fund Categorization & Portfolio Allocation Norms (Circular SEBI/HO/IMD/DF3/CIR/P/2026/42)",
        "category": "REGULATORY_COMPLIANCE",
        "content": """
SEBI Categorization and Rationalization of Mutual Fund Schemes:
1. Large Cap Funds: An open-ended equity scheme predominantly investing in large cap stocks. Minimum investment in equity & equity-related instruments of large cap companies (1st - 100th company in terms of full market capitalization) shall be 80% of total assets.
2. Mid Cap Funds: Minimum investment in equity & equity-related instruments of mid cap companies (101st - 250th company in terms of full market capitalization) shall be 65% of total assets.
3. Hybrid Aggressive Funds: Equity & equity-related instruments allocation must be between 65% and 80% of total assets; Debt instruments allocation between 20% and 35%.
4. ELSS (Equity Linked Savings Scheme): Equity Linked Savings Scheme with a statutory 3-year lock-in period qualifying under Section 80C of the Income Tax Act. Minimum 80% in equity instruments. No premature redemption permitted before 36 months from the date of allotment.
5. Liquid Funds: Schemes investing in debt and money market instruments with maturity up to 91 days only. Graduated exit load applicable for redemptions within 7 days.
6. Total Expense Ratio (TER) Limits: For open-ended equity schemes, maximum allowable base TER is capped at 2.25% on the first ₹500 Cr AUM, reducing progressively down to 1.05% for AUM exceeding ₹50,000 Cr.
        """
    },
    {
        "doc_id": "FACT-FV-BC-001",
        "title": "FinVista Bluechip Large Cap Fund - Scheme Factsheet & Investment Mandate",
        "category": "SCHEME_FACTSHEET",
        "content": """
FinVista Bluechip Large Cap Fund (Code: FV-BC-001):
- Fund Objective: Long-term capital appreciation by investing in top-tier bluechip market leaders.
- Benchmark: NIFTY 50 Total Returns Index (TRI).
- Inception Date: March 10, 2015 | Current NAV: ₹78.45 | AUM: ₹2,450.80 Crores.
- Portfolio Asset Allocation: Large Cap Equity: 88.5%, Mid Cap Equity: 6.2%, Cash & Money Market: 5.3%.
- Top 5 Holdings: HDFC Bank (9.4%), Reliance Industries (8.8%), ICICI Bank (7.6%), Infosys (6.2%), Tata Consultancy Services (5.8%).
- Risk Metrics: Portfolio Beta: 0.92, Sharpe Ratio: 1.85, Standard Deviation: 12.4%, Alpha vs NIFTY 50: +2.76%.
- Expense Ratio: 0.72% (Direct Plan) | Exit Load: 1.00% if redeemed within 365 days; 0% thereafter.
- Minimum Investment: ₹5,000 for lumpsum, ₹1,000 for monthly SIP.
        """
    },
    {
        "doc_id": "FACT-APX-MC-002",
        "title": "Apex Midcap Opportunities Fund - Scheme Factsheet & Strategy",
        "category": "SCHEME_FACTSHEET",
        "content": """
Apex Midcap Opportunities Fund (Code: APX-MC-002):
- Fund Objective: High capital growth by identifying fast-growing mid-sized Indian enterprises.
- Benchmark: NIFTY Midcap 150 TRI | Current NAV: ₹112.30 | AUM: ₹1,890.40 Crores.
- Portfolio Allocation: Mid Cap Equities: 72.4%, Small Cap: 18.1%, Cash & Arbitrage: 9.5%.
- Top Holdings: Trent Ltd (5.4%), Persistent Systems (4.9%), Dixon Technologies (4.3%), Polycab India (4.1%), Federal Bank (3.8%).
- Expense Ratio: 0.85% | Exit Load: 1.00% for redemption within 12 months.
- Risk Classification: Very High Risk. Suitable for investment horizons of 5+ years.
        """
    },
    {
        "doc_id": "FACT-PRM-HY-003",
        "title": "Premier Dynamic Balanced Hybrid Fund - Factsheet & Allocation Strategy",
        "category": "SCHEME_FACTSHEET",
        "content": """
Premier Dynamic Balanced Hybrid Fund (Code: PRM-HY-003):
- Fund Objective: Balanced growth with downside volatility containment through asset allocation.
- Benchmark: CRISIL Hybrid 35+65 Aggressive Index | Current NAV: ₹45.60 | AUM: ₹1,240.20 Crores.
- Asset Breakdown: Equity: 68.5%, AAA Corporate Debt: 22.5%, Sovereign G-Secs: 6.0%, Cash: 3.0%.
- Expense Ratio: 0.65% | Exit Load: 1.00% if redeemed within 180 days.
- Downside Protection: Dynamic hedging shields portfolio during market drawdowns, restricting benchmark decline pass-through to under 50%.
        """
    },
    {
        "doc_id": "AML-SOP-2026",
        "title": "Anti-Money Laundering (AML) & Suspicious Transaction Reporting (STR) SOP",
        "category": "COMPLIANCE_POLICY",
        "content": """
AML and CFT Standard Operating Procedures (SEBI / FIU-IND Guidelines):
1. High-Value Surveillance Threshold: Any single transaction exceeding ₹30 Crores (or equivalent in foreign currency) triggers an immediate mandatory Level-1 Compliance Review.
2. Velocity Alerts: Multiple cumulative transactions exceeding ₹10 Crores within a rolling 72-hour window by the same beneficial owner or PAN must be inspected for structuring/smurfing patterns.
3. Suspicious Transaction Report (STR): If source of funds cannot be verified or transactions demonstrate non-economic behavior, an STR must be submitted to the Financial Intelligence Unit (FIU-IND) within 7 working days.
4. Politically Exposed Persons (PEP) & High-Risk Folios: Enhanced Due Diligence (EDD) required before allotment. Annual re-KYC mandatory.
        """
    },
    {
        "doc_id": "RISK-POLICY-2026",
        "title": "AMC Portfolio Risk Management & Liquidity Coverage Policy",
        "category": "RISK_MANAGEMENT",
        "content": """
Asset Management Company Risk & Stress Testing Guidelines:
1. Liquidity Coverage Ratio (LCR): Open-ended schemes must maintain a minimum of 90% liquidity coverage against potential peak 30-day redemption runs. Liquid and Debt schemes must hold at least 10% in sovereign G-Secs/T-Bills.
2. Stress Testing Framework: Mandatory monthly stress tests simulating 5%, 10%, and 20% systemic market corrections. Fund managers must evaluate drawdowns across asset classes: Large Cap (downside capture: 0.85), Hybrid (downside capture: 0.45), Debt (downside capture: -0.05), Small Cap (downside capture: 1.35).
3. Portfolio Beta & Sharpe Target: Target optimized portfolio Beta is 0.90 - 0.95 with a target Sharpe Ratio above 1.75 to ensure superior risk-adjusted alpha generation.
        """
    }
]
