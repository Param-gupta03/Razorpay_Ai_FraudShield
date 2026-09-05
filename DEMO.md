# FraudShield AI — Presentation & Pitch Video Guide

This guide describes how to deliver a compelling, 5-minute pitch video presentation of **FraudShield AI** for merchants and risk leadership.

## 1. Prerequisites
Ensure both servers are running locally:
*   **FastAPI Backend URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000) (Interactive Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs))
*   **Next.js Frontend URL:** [http://localhost:3000](http://localhost:3000)

---

## 2. The 5-Minute Pitch Video Script & Flow (300 Seconds)

### STEP 1: The Problem & Why-Now (Duration: ~45 seconds)
1.  Open the web dashboard at `http://localhost:3000`.
2.  **Script Cue:** 
    > *"Welcome to FraudShield AI. E-commerce merchants today face a multi-million-dollar dilemma: direct fraud losses average $150 per chargeback incident, but overly aggressive rule-based fraud filters create false decline friction that turns away loyal customers. Why now? Card-not-present transaction volumes are peaking, fraudsters adapt faster than static rule engines, and opaque AI models create compliance and chargeback audit nightmares. FraudShield AI bridges this gap with an explainable, defense-only advisory system that scores transactions along a strict chronological timeline."*
3.  Point to the **KPI Cards** and **Business Cost Management Chart** on the dashboard. Highlight the **$232,770** estimated net savings benefit on the test set ($229,680 managed cost vs. $462,450 unmanaged baseline fraud cost).

### STEP 2: Live Single Transaction Scoring (Duration: ~60 seconds)
1.  Click the **Transactions** link in the navigation header.
2.  Explain that these are real, audited demo transactions from the IEEE-CIS / Vesta dataset.
3.  Find transaction **`#443491`** (a high-velocity credit transaction) in the table and click **`Analyze`** on the right.
4.  You are now on the **Risk Analysis** tab with populated form inputs and raw payload.
5.  Click **`Analyze Transaction`** (instant scoring in < 0.1s prediction latency).
6.  Point to the real-time scoring results:
    *   **Fraud Probability:** **96.87%** (Risk Level: **HIGH**).
    *   **Recommended Action:** **`REVIEW TRANSACTION`** (Exceeds the frozen cost-minimizing operating threshold of 0.05).
    *   **Decision Cost:** Estimated at **$0.47** (Manual review overhead $(1 - 0.9687) \times \$15.00$).
7.  **Script Cue:** 
    > *"In under 100 milliseconds, FraudShield AI outputs a calibrated 96.87% fraud probability. Crucially, our frozen operational threshold is 0.05. Any transaction scoring below 0.05 is auto-approved with zero customer friction. Scores between 0.05 and 0.30 fall into the MEDIUM risk band, while scores at or above 0.30 are marked HIGH risk. Both MEDIUM and HIGH trigger a human-assisted review queue rather than an automated decline, safeguarding legitimate checkout revenues."*

### STEP 3: False-Positive-Cost Economics & Threshold Optimization (Duration: ~60 seconds)
1.  Scroll or switch to the **Risk Policy & Methodology** tab (About tab) or refer to the Cost Breakdown chart on the dashboard.
2.  **Script Cue:** 
    > *"Why did we freeze our operational threshold at 0.05 rather than the standard 0.50? Because real-world fraud exhibits severe cost asymmetry. A false positive costs an estimated $15 in manual review labor and customer friction, but a false negative—a missed fraud chargeback—costs $150 in lost inventory and bank penalties. That is a 10-to-1 asymmetry. By formulating our objective function around Expected Cost = P(Fraud) * $150 for Approvals and (1 - P(Fraud)) * $15 for Reviews, our validation optimization proved that a 0.05 operating cutoff minimizes total financial loss. Note that while 0.05 is the operational gate triggering reviews, 0.10 marks our internal boundary where review queue prioritization escalates."*
3.  Highlight the operational review rate: **8.31%**, ensuring the manual review queue remains operationally lean and sustainable for merchant operations teams.

### STEP 4: SHAP Explainability & Non-Causal Language (Duration: ~45 seconds)
1.  On the Risk Analysis tab, scroll down to **"Why was this transaction flagged?"**.
2.  Show the side-by-side SHAP positive and negative attribution cards:
    *   **Risk-Increasing Factors:** `C14`, `TransactionAmt`, `V54`
    *   **Risk-Reducing Factors:** `D1`, `card3_count`, `V314`
3.  **Script Cue:** 
    > *"FraudShield AI never operates as a black box. For every scored checkout, our TreeExplainer calculates exact local SHAP attributions. Notice our strict non-causal language: the system reports that high transaction velocity counts in C14 and elevated checkout amounts 'contributed to higher predicted risk', while card history age in D1 'mitigated risk'. We explicitly describe mathematical feature contributions rather than claiming real-world causality, providing actionable, audit-ready context for human analysts."*

### STEP 5: Honest Metrics, Temporal Drift & Defense-Only Guardrails (Duration: ~60 seconds)
1.  Click **Model Performance** in the header navigation.
2.  Show the comparison between **Validation** and the **Untouched Temporal Test** performance metrics.
3.  Point to the untouched test confusion matrix:
    *   **TP:** `2,080` | **TN:** `80,216` | **FP:** `5,282` | **FN:** `1,003` | **FNR:** `32.53%`
    *   **Test Recall:** `67.47%` | **Precision:** `28.25%` | **PR-AUC:** `0.5459` | **ROC-AUC:** `0.9057` | **Brier Score:** `0.0220`
4.  **Script Cue:** 
    > *"Finally, FraudShield AI is built upon rigorous, honest machine learning standards. We never use random k-fold splits, which leak future transaction patterns into past training data. We enforce strict out-of-time chronological splitting. On our final untouched test split, the model achieved a 67.47% fraud recall and delivered $232,770 in net financial savings. We openly disclose that PR-AUC dropped from 0.6185 on validation to 0.5459 on untouched test data—a real-world demonstration of temporal concept drift that highlights the necessity of continuous monitoring. Most importantly, FraudShield AI is engineered strictly as defense-only, nothing offense-capable: it advises human teams, optimizes review queues, and protects honest merchants without punitive automated declines. Thank you."*

---

## 3. Recommended Demo Transactions
Use these pre-audited cases in the `Transactions` tab for immediate testing:

1.  **Transaction #443491 (High Risk / Fraudulent):**
    *   *Inputs:* TransactionAmt = $150.00, Card = Visa Credit, high velocity counters.
    *   *Result:* Fraud Probability = `96.87%` | Recommended Action = `REVIEW` | Risk Level = `HIGH`.
2.  **Transaction #441478 (High Risk / Fraudulent):**
    *   *Inputs:* TransactionAmt = $13.28, Card = Visa Credit, low elapsed time.
    *   *Result:* Fraud Probability = `81.22%` | Recommended Action = `REVIEW` | Risk Level = `HIGH`.
3.  **Transaction #437512 (Low Risk / Legitimate):**
    *   *Inputs:* TransactionAmt = $34.00, Card = Mastercard Debit.
    *   *Result:* Fraud Probability = `0.62%` | Recommended Action = `APPROVE` | Risk Level = `LOW`.
4.  **Transaction #450846 (Low Risk / Legitimate):**
    *   *Inputs:* TransactionAmt = $85.00, Card = Visa Credit, Safari browser.
    *   *Result:* Fraud Probability = `1.50%` | Recommended Action = `APPROVE` | Risk Level = `LOW`.

---

## 4. Key Metrics to Highlight
*   **Frozen Operating Threshold:** `0.05` (Loss-minimizing cutoff selected on validation).
*   **Test Set Recall:** `67.47%` (FNR: `32.53%`).
*   **Test Set Precision:** `28.25%`.
*   **Test Confusion Matrix:** TP: `2,080` | TN: `80,216` | FP: `5,282` | FN: `1,003`.
*   **Test PR-AUC:** `0.5459` (Validation PR-AUC: `0.6185`).
*   **Test ROC-AUC:** `0.9057`.
*   **Brier Calibration Score:** `0.0220` (Calibrated probabilities).
*   **Test Set Net Benefit:** `$232,770.00` savings ($229,680.00 expected cost vs. $462,450.00 baseline).
*   **Review Rate:** `8.31%` (Operationally manageable merchant overhead).
