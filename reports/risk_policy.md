# AI Fraud Risk Manager Policy

This document outlines the risk categorization boundaries, recommended actions, and expected cost parameters established for the AI Fraud Risk Engine.

## 1. Risk Level and Recommended Action Mapping

Our risk policy is designed to be transparent, mathematically grounded in validation probabilities, and strictly **defense-only**.

| Probability Range | Risk Level | Recommended Action | Target Handling Policy |
| --- | --- | --- | --- |
| **Probability < 0.05** | **LOW** | **APPROVE** | Low-risk transactions are approved automatically to minimize customer checkout friction. |
| **0.05 <= Probability < 0.30** | **MEDIUM** | **REVIEW** | Flagged for standard review. Assisted review teams are notified to double-check details. |
| **Probability >= 0.30** | **HIGH** | **REVIEW** | Flagged for high-priority review. Assisted review teams inspect resolution, IP, and device data. |

## 2. Policy Justification

The thresholds for risk categorization are determined by the empirical distribution of model predictions on our validation set:

1.  **Low Risk Threshold (< 0.05):**
    *   Our baseline fraud rate is **3.49%**.
    *   The optimal decision threshold that minimizes total business expected cost (balancing the cost of chargebacks vs. review friction) is **0.05**.
    *   Therefore, any transaction with a predicted fraud risk below 5% is cleared for automatic approval, ensuring that over **95%** of legitimate customers pass without friction.
2.  **Medium Risk (0.05 to 0.30):**
    *   Transactions in this band have a fraud risk that is 3 to 9 times higher than the baseline average.
    *   Manual review is required because the probability is elevated, but these transactions represent borderline flags where customer details (e.g. card/address history) require human verification.
3.  **High Risk (>= 0.30):**
    *   A transaction with a probability >= 30% carries a risk that is **10 to 28 times** higher than the baseline average.
    *   These are high-priority review items that frequently correlate with rapid checkout velocity (high values in `C` columns) and mismatching location or email parameters.

## 3. Defense-Only Action Rules

To comply with defense-only regulations, the model does **not** automatically reject transactions or block cards:
*   **No Auto-Decline:** The recommended actions are strictly limited to `APPROVE` and `REVIEW`.
*   **Human-in-the-Loop:** Transactions flagged as `REVIEW` are directed to the merchant's risk operations queue. This assists review teams rather than making irreversible, automated financial decisions that could trigger false declines and damage customer lifetime value.

## 4. Expected Cost Formulation

Decisions are priced based on the following configurable cost model:
*   $\text{FALSE\_POSITIVE\_COST}$ = **$15.00** (cost of reviewing a legitimate transaction or user friction).
*   $\text{FALSE\_NEGATIVE\_COST}$ = **$150.00** (average ticket size chargeback loss).

### Formula
*   For `APPROVE` decisions (prob < 0.05):
    $$\text{Decision Cost} = \text{prob} \times \$150.00$$
*   For `REVIEW` decisions (prob >= 0.05):
    $$\text{Decision Cost} = (1 - \text{prob}) \times \$15.00$$
