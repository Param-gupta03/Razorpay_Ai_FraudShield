# FraudShield AI — System Architecture

This document describes the end-to-end design, data pipelines, scoring pathways, and decision systems of FraudShield AI.

## 1. System Topology & Pipeline Flow

The diagram below maps out the request lifecycle of a transaction through FraudShield AI:

```text
                     Incoming Transaction Payload
                                   ↓
                       Pydantic Schema Validation
                                   ↓
                       Raw Column Template Mapping
                                   ↓
                       Fitted Feature Transformations
                                   ↓
                        Aligned Feature Matrix
                                   ↓
                         LightGBM Classifier
                                   ↓
                          Fraud Probability
                                   ↓
                     Tuned Expected Cost Threshold (0.05)
                                ↙          ↘
                  Prob < 0.05                  Prob >= 0.05
                     ↙                              ↘
            APPROVE ACTION                     REVIEW ACTION
                     ↘                              ↙
                       SHAP TreeExplainer Local Values
                                   ↓
                       Non-Causal Text Formatting
                                   ↓
                           API Response JSON
                                   ↓
                       React Merchant Dashboard
```

---

## 2. Component Explanations

### 1. Pydantic Schema Validation
*   **Module:** `backend/app/schemas.py`
*   The API validates incoming JSON payloads using Pydantic. Required fields (`TransactionDT`, `TransactionAmt`) are typed and bounds-checked.
*   By setting `extra = "allow"`, the schema accepts arbitrary Vesta dataset columns (such as `C`, `D`, `V` columns, and browser/device specs) dynamically.

### 2. Template Mapping & Preprocessing
*   **Module:** `backend/app/model_service.py` and `src/features.py`
*   To prevent shape errors in LightGBM, `ModelService` constructs an empty 434-column dictionary template mapped from raw headers at startup.
*   The payload overrides this template, skipping `None` inputs to preserve `np.nan` floats.
*   The template is passed to `feature_pipeline.pkl` (fitted on the training split) which transforms frequencies, parses screen resolutions, groups browsers/OS systems, and converts categorical columns to pandas `category` types.

### 3. Feature Matrix Alignment
*   **Module:** `backend/app/model_service.py`
*   The transformed row is filtered and ordered to match the 456 columns specified in `reports/feature_metadata.json`.
*   To preserve pandas category metadata, the transaction is sliced as a 1-row DataFrame (`X.iloc[[0]]`) rather than a Series.

### 4. LightGBM Risk Classifier
*   **Module:** `models/lightgbm_final.pkl`
*   Evaluates the feature matrix to output a calibrated probability $P(\text{isFraud} = 1)$.
*   LightGBM is chosen because it natively handles missing values (which are common in identity features) and is highly efficient.

### 5. Risk Policy & Expected Cost Gate
*   **Module:** `backend/app/risk_engine.py`
*   The probability is compared against the frozen, cost-optimized threshold of `0.05`:
*   $P(\text{Fraud}) < 0.05 \rightarrow$ **LOW Risk / `APPROVE`**
*   $0.05 \le P(\text{Fraud}) < 0.30 \rightarrow$ **MEDIUM Risk / `REVIEW`**
*   $P(\text{Fraud}) \ge 0.30 \rightarrow$ **HIGH Risk / `REVIEW`**
*   **Decision Cost:** Expected financial cost is calculated as:
    *   If Approved: Expected Cost = $\text{prob} \times \$150.00$ (chargeback risk).
    *   If Reviewed: Expected Cost = $(1 - \text{prob}) \times \$15.00$ (manual review overhead).

### 6. SHAP Attribution
*   **Module:** `backend/app/explanation_service.py`
*   For each scored transaction, the SHAP `TreeExplainer` calculates local feature attributions.
*   The service filters out micro-impacts ($|val| \le 0.005$) and returns the top 3 risk-increasing and top 3 risk-reducing factors.
*   The descriptions use non-causal language (e.g. *"contributed to higher predicted risk"* instead of *"caused fraud"*).

### 7. Merchant React Dashboard
*   **Module:** `frontend/`
*   Built in Next.js and TypeScript, styled with Tailwind CSS, and graphed with Recharts.
*   Consumes the FastAPI endpoints in a responsive tab-based dashboard that supports live transaction simulation, batch CSV prediction download, and model audits.
