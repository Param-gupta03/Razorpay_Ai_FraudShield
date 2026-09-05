# Phase 6 — Final QA & Build Verification Report

This report documents the testing checklist, compilation verification, security audits, data privacy reviews, and latency observations for FraudShield AI.

## 1. Unit & Integration Testing
*   **Module:** `backend/tests/test_api.py`
*   **Result:** **6 passed, 0 failed, 4 warnings in 3.29 seconds.**
*   **Coverage:**
    1.  `test_health`: Verified 200 health status and correct operational threshold.
    2.  `test_model_info`: Verified metadata structure and metrics.
    3.  `test_predict_valid`: Evaluated a standard payload, confirming correct risk mapping.
    4.  `test_predict_missing_required`: Confirmed Pydantic blocks payloads missing required fields.
    5.  `test_predict_bad_types`: Confirmed Pydantic blocks payloads with incorrect value types.
    6.  `test_batch_prediction`: Verified multipart file processing and CSV streams.

## 2. Frontend Production Build
*   **Command:** `npm run build` in `frontend/`
*   **Result:** **Compiled successfully in 2.2 seconds; TypeScript checks completed in 4.0s (exit code 0).**
*   **Fixes Implemented:**
    *   *JSX Math Parsing:* Math formula brackets (e.g. `{}`) were incorrectly interpreted by the Next.js compiler as Javascript code blocks, crashing the build. Fixed by wrapping equations in string literals `{"..."}` and double-escaping backslashes.

## 3. End-to-End System Testing & Sample Predictions
We tested the backend and frontend together by scoring our pre-audited demo transactions:

| Transaction ID | Input Profile | Probability | Risk Level | recommended action | Expected Cost | SHAP Key Factors |
| --- | --- | --- | --- | --- | --- | --- |
| **#443491** | High-value, iOS browser, high transaction counts | **96.87%** | **HIGH** | **REVIEW** | **$0.47** | +C1, +C13, +V258 |
| **#441478** | Low-value, Windows, credit card, low elapsed time | **81.22%** | **HIGH** | **REVIEW** | **$2.82** | +C1, +C8, +C13 |
| **#437512** | Mid-value, debit card, standard velocity | **0.62%** | **LOW** | **APPROVE** | **$0.93** | -card5, -TransactionAmt |
| **#450846** | Mid-value, credit card, mobile safari browser | **1.50%** | **LOW** | **APPROVE** | **$2.25** | -P_emaildomain, -D13 |

*   **Extreme Missingness Test:** Passed a payload containing ONLY the required fields `{"TransactionDT": 86400, "TransactionAmt": 150.0}`. The system mapped the remaining 432 columns to `np.nan` and returned a probability of `12.49%` (MEDIUM Risk / REVIEW) in **53ms** without crashing.

## 4. Latency Observations
*   **Single Prediction Latency:** **~50–65ms** (Average API roundtrip under TestClient).
*   **SHAP Overhead:** **~12ms** (TreeExplainer runs locally in memory on a single row, showing near-instantaneous execution).
*   **Batch Prediction Latency:** **~120ms** for small batches (CSV uploaded, transformed, and streamed back in a vectorized pipeline).

## 5. Security & Privacy Audits
*   **Data Types:** Cleaned up dict mapping to check `if value is not None` before overwriting. This preserves `np.nan` for numerical inputs, preventing them from being typed as `object` (which crashes LightGBM).
*   **CORS Configuration:** Standard FastAPI CORS middleware handles localhost domains safely for Next.js.
*   **Traceback Shielding:** Backend exceptions in predictions are caught and returned as structured HTTP 400 Bad Request messages. Raw stack trace paths are hidden from API responses.
*   **Data Masking:** Transaction data contains no personally identifiable information (PII) like customer names, emails, billing addresses, or card numbers. High-cardinality fields are simplified to numeric indices or provider domains.

## 6. Final Project Structure
The project matches the required layout:
```text
razopayjon/
├── backend/
│   └── app/
│       ├── main.py
│       ├── schemas.py
│       ├── model_service.py
│       ├── risk_engine.py
│       ├── explanation_service.py
│       └── config.py
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── types/
│   └── public/
├── src/
│   ├── data_preparation.py
│   ├── features.py
│   ├── train_models.py
│   └── evaluate_models.py
├── models/
│   ├── lightgbm_final.pkl
│   └── feature_pipeline.pkl
├── reports/
│   ├── risk_policy.md
│   ├── phase3_report.md
│   ├── phase4_report.md
│   └── final_qa_report.md
├── README.md
├── ARCHITECTURE.md
└── DEMO.md
```

## 7. Remaining Limitations
1.  **Temporal Drift:** Performance on the untouched test set (PR-AUC: `0.5459`) is lower than validation performance (`0.6185`). The model must be periodically monitored and retrained to handle new fraud shapes.
2.  **Identity Capture:** ~75% of browser/OS identifiers are missing in Vesta checkout streams, forcing risk scores to rely heavily on transaction velocity (`C` columns) and transaction amounts.
3.  **Benchmark Costs:** Expected cost calculations use configurable demonstration assumptions ($15 review cost vs $150 chargeback loss) and should not be presented as guaranteed merchant savings.
