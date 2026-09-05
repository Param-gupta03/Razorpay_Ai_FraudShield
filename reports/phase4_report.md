# Phase 4 — Fraud Risk Engine & FastAPI Backend Report

This report documents the design, architecture, endpoints, risk policy, and testing results of the FastAPI-based AI Fraud Risk Manager backend.

## 1. Backend Architecture

The backend is built using a modular design separating HTTP routing from model serving, risk policies, and explainability logic:

```text
backend/
├── app/
│   ├── main.py                   # FastAPI routing, lifespans, and HTTP endpoints
│   ├── schemas.py                # Pydantic request and response schemas
│   ├── model_service.py          # Model loader, template mapping, and transforms
│   ├── risk_engine.py            # Risk level, action policy, and cost modeling
│   ├── explanation_service.py    # SHAP local interpretability service
│   └── config.py                 # Constant definitions and file path configs
├── tests/
│   └── test_api.py               # Pytest unit and integration test suite
└── requirements.txt              # API package dependencies
```

*   **FastAPI Lifespans:** On startup, the application loads the production artifacts once into memory as singletons. On shutdown, it deletes them and triggers garbage collection to clear memory.
*   **Path Resolution:** Automatically appends the project root and `src/` to `sys.path` on startup so that pickle serialization can resolve the custom `features.FeaturePipeline` class.

## 2. Model & Feature Pipeline Integration

*   **Production Model:** Loads the frozen LightGBM standard model `models/lightgbm_final.pkl`.
*   **Pipeline Serialization:** Loads the fitted pipeline instance `models/feature_pipeline.pkl`.
*   **Column Alignment:** 
    *   To prevent LightGBM shape check failures (LightGBM demands exactly the same 456 columns in the same order as trained), `ModelService` reads the raw CSV headers at startup to map a complete 434-column dictionary template initialized to `NaN`.
    *   Pydantic request inputs are mapped onto this template, skipping `None` values (which keeps missing numerical values as `np.nan` floats and prevents Pandas from typing them as `object`).
    *   After running `pipeline.transform()`, the columns are filtered and ordered exactly to the 456 columns listed in `reports/feature_metadata.json`.
    *   To prevent Pandas from losing categorical datatypes when parsing a single transaction, the row is extracted as a 1-row DataFrame (`X.iloc[[0]]`) instead of a Series.

## 3. API Endpoints

### 1. `GET /health`
*   Returns system health status (`healthy`/`unhealthy`), model type, version, and the operational threshold (`0.05`).

### 2. `GET /model-info`
*   Exposes validation split performance side-by-side with final untouched test split performance to guarantee honest disclosures:
    *   **Validation PR-AUC:** `0.6185`
    *   **Final Untouched Test PR-AUC:** `0.5459` | Test Recall: `0.6747`
*   Also reports model version and known limitations.

### 3. `POST /predict`
*   Scores a single transaction. Returns probability, risk level (`LOW`/`MEDIUM`/`HIGH`), recommended action (`APPROVE`/`REVIEW`), expected decision cost, and detailed SHAP risk factors.

### 4. `POST /predict/batch`
*   Accepts a multi-row CSV file upload, transforms features in a vectorized manner, scores transactions, and streams back a CSV response mapping `TransactionID`, `fraud_probability`, `risk_level`, and `recommended_action`.

## 4. Risk Policy & recommended actions

The risk policy uses a simple mapping based on the optimal validated cost threshold of `0.05`:
*   **LOW** (Probability < 0.05) $\rightarrow$ **`APPROVE`** (Allows standard legitimate checkout without friction)
*   **MEDIUM** (0.05 $\le$ Probability < 0.30) $\rightarrow$ **`REVIEW`** (Requires merchant manual review, elevated risk)
*   **HIGH** (Probability $\ge$ 0.30) $\rightarrow$ **`REVIEW`** (Requires high-priority manual review, extreme velocity risk)

This system is strictly **defense-only**: it recommends either `APPROVE` or `REVIEW` (directing flagged cases to human risk analysts) rather than taking irreversible automated decline decisions.

## 5. SHAP Explanations

For each scored transaction, the API returns the top 3 risk-increasing and top 3 risk-mitigating features. 
*   **Descriptive Language:** Returns descriptive text (e.g. *"Feature C14 value (nan) contributed to a higher predicted fraud risk"*) rather than asserting causal statements.

## 6. Business Cost Model

Expected decision costs are computed dynamically:
*   `FALSE_POSITIVE_COST` = **$15.00** (Review overhead/friction)
*   `FALSE_NEGATIVE_COST` = **$150.00** (Chargeback/fraud loss)
*   If Approved: Expected Cost = $\text{prob} \times \$150.00$
*   If Reviewed: Expected Cost = $(1 - \text{prob}) \times \$15.00$

## 7. Testing Results

Pytest was executed on `backend/tests/test_api.py`. All **6 test cases passed successfully**:

```text
tests\test_api.py ......                                                 [100%]
======================== 6 passed, 4 warnings in 3.29s ========================
```

## 8. Example Request and Response

### Request (`POST /predict`)
```json
{
  "TransactionDT": 86400,
  "TransactionAmt": 150.00,
  "TransactionID": 2987004,
  "ProductCD": "W",
  "card1": 13926,
  "card2": 523.0,
  "card6": "debit",
  "P_emaildomain": "gmail.com",
  "C1": 1.0,
  "C13": 1.0,
  "DeviceInfo": "Windows",
  "id_31": "chrome 63.0"
}
```

### Response (200 OK)
```json
{
  "transaction_id": 2987004,
  "fraud_probability": 0.0589,
  "risk_level": "LOW",
  "recommended_action": "APPROVE",
  "threshold": 0.1,
  "decision_cost": 8.83,
  "top_risk_factors": [
    {
      "feature": "C14",
      "impact": "increases_risk",
      "importance": 0.8902201691546512
    },
    {
      "feature": "TransactionAmt",
      "impact": "increases_risk",
      "importance": 0.2500110848167912
    },
    {
      "feature": "V54",
      "impact": "increases_risk",
      "importance": 0.18201895837362672
    }
  ],
  "top_mitigating_factors": [
    {
      "feature": "D1",
      "impact": "reduces_risk",
      "importance": 0.30827210413594536
    },
    {
      "feature": "card3_count",
      "impact": "reduces_risk",
      "importance": 0.14645468326640315
    },
    {
      "feature": "V314",
      "impact": "reduces_risk",
      "importance": 0.1359712289026932
    }
  ]
}
```

## 9. How to Run Locally

1.  Navigate to the `backend/` folder:
    ```bash
    cd backend
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run unit tests:
    ```bash
    python -m pytest
    ```
4.  Start the FastAPI server:
    ```bash
    uvicorn app.main:app --reload
    ```
5.  Access the interactive OpenAPI UI at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## 10. Known Limitations
1.  **High Null Rates:** Identity features (OS, Browser, Device) have a ~75% missing rate. While LightGBM splits natively on NaNs, predictions on checkout-only transactions rely heavily on card velocity (`C` columns) and transaction amounts.
2.  **No Causal Proof:** SHAP attributions reflect how the model weighs features relative to the training distribution and should not be interpreted as physical real-world causation.
3.  **PR-AUC Mismatch:** The final test set PR-AUC is **0.5459** (compared to validation's **0.6185**), indicating standard temporal drift. Periodical re-training is required to maintain accuracy.
