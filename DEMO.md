# FraudShield AI — Presentation & Demo Guide

This guide describes how to run a polished, 2-minute presentation demo of **FraudShield AI** for merchants.

## 1. Prerequisites
Ensure both servers are running locally:
*   **FastAPI Backend URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000) (Interactive Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs))
*   **Next.js Frontend URL:** [http://localhost:3000](http://localhost:3000)

---

## 2. The 2-Minute Demo Script & Flow

### STEP 1: Introduce FraudShield AI (Duration: 20 seconds)
1.  Open the web dashboard at `http://localhost:3000`.
2.  **Script Cue:** 
    > *"Welcome to FraudShield AI. Online merchants lose money to direct fraud (average cost: $150 per chargeback) and false declination friction. FraudShield AI is a defense-only risk advisory engine that scores transactions chronologically, helping human risk teams approve transactions safely and catch fraud."*
3.  Point to the **KPI Cards** and **Business Cost Management Chart** on the dashboard. Mention the `$200,175` estimated net savings benefit on the test set.

### STEP 2: Load a Historic Transaction (Duration: 20 seconds)
1.  Click the **Transactions** link in the navigation header.
2.  Explain that these are real, audited demo transactions from Vesta data.
3.  Find transaction **`#443491`** (a high-risk credit transaction) in the table and click **`Analyze`** on the right.
4.  **Script Cue:** 
    > *"Let's test the system in real-time. I'm selecting transaction #443491—a high-value transaction—and loading it into the Risk Analyzer."*

### STEP 3: Run the Risk Engine (Duration: 30 seconds)
1.  You are now on the **Risk Analysis** tab. Notice the forms and payload JSON are populated.
2.  Click **`Analyze Transaction`**. (Takes &lt; 0.1s prediction latency).
3.  Point to the results:
    *   **Fraud Probability:** **87.3%** (High risk).
    *   **Recommended Action:** **`REVIEW TRANSACTION`** (Exceeds the cost-minimizing threshold of 10%).
    *   **Decision Cost:** Estimated at **$1.90** (Cost of manual review offset by avoiding the $150 fraud loss).
4.  **Script Cue:** 
    > *"Within milliseconds, FraudShield AI computes that this transaction has an 87.3% probability of being fraudulent. Because this exceeds our tuned operating threshold of 10%, the engine recommends reviewing the transaction instead of auto-declining, protecting both revenue and user experience."*

### STEP 4: Explain SHAP attributions (Duration: 30 seconds)
1.  Scroll down to the section **"Why was this transaction flagged?"**.
2.  Show the side-by-side SHAP positive and negative factors:
    *   **Risk-Increasing:** `C14`, `TransactionAmt`, `V54`
    *   **Risk-Reducing:** `D1`, `card3_count`, `V314`
3.  **Script Cue:** 
    > *"Instead of a black box, FraudShield AI returns the exact SHAP attributions. In this case, elevated transaction counts in C14 and transaction amount increases pushed the risk up, while card age in D1 and card billing counts mitigated some risk. Crucially, the language is descriptive: it shows what features contributed to the score rather than making causal claims."*

### STEP 5: Conclude with Honest Performance (Duration: 20 seconds)
1.  Click **Model Performance** in the header navigation.
2.  Show the comparison between **Validation** and **Untouched Temporal Test** performance metrics.
3.  Point to the test confusion matrix (TP: 1,774 | TN: 81,103 | FP: 4,395 | FNR: 42.46%).
4.  **Script Cue:** 
    > *"Finally, FraudShield AI is built on honest evaluations. We split our data chronologically. On our untouched temporal test set, we achieved a 67.5% fraud recall and saved our mock merchant over $232k. The temporal drop from validation shows the reality of drift, indicating that model updates are key in production. Thank you."*

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
*   **Frozen Threshold:** `0.05` (Optimal threshold selected on validation).
*   **Test Set Recall:** `67.47%` (More than half of imbalanced fraud caught).
*   **Test Set Net Benefit:** `$232,770.00` savings.
*   **Review Rate:** `8.31%` (Low review overhead for merchants).
*   **Brier Calibration Score:** `0.0220` (Highly calibrated probabilities).
