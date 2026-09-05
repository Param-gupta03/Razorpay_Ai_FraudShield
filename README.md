# FraudShield AI - Transaction Risk Dashboard

FraudShield AI is an ML-powered, defense-only transaction risk management engine designed to help online merchants identify fraud while minimizing transaction review friction for legitimate checkouts.

## 1. Problem
Merchants face two distinct payment challenges:
1.  **Direct Fraud Losses:** Stolen merchandise and chargeback fees (which average $150 per transaction).
2.  **False Declines:** Declining legitimate customers due to overly rigid rules, leading to customer lifetime value losses.

## 2. Solution
An explainable, human-assisted ML risk scoring engine that:
*   Scores transactions to predict a **fraud probability**.
*   Classifies risk into **LOW**, **MEDIUM**, and **HIGH** bands.
*   Recommends action rules: **APPROVE** (LOW risk) or **REVIEW** (MEDIUM/HIGH risk).
*   Explains risk factors locally using game-theoretic **SHAP** values.
*   Estimates decision costs under configurable merchant assumptions.

## 3. Dataset Profile
*   **Total Transactions:** 590,540
*   **Fraud Transactions:** 20,663
*   **Imbalance Rate:** 3.499% Fraud Rate (highly imbalanced class setting)

## 4. Machine Learning & Preprocessing
*   **Model:** Standard LightGBM Classifier.
*   **Features:** 456 columns (incorporating raw amounts, billing zip codes, transaction frequency counts, address mappings, and OS/browser identity features).
*   **Preprocessing:** Chronological frequency maps for high-cardinality values, categorical mapping, and memory-downcasted data merges.

## 5. Temporal Splitting & Evaluation Metrics
To prevent future-information leakage, the datasets are split chronologically by `TransactionDT` (no random splitting):
*   **Training Split (70% earliest):** 413,378 rows
*   **Validation Split (15% next):** 88,581 rows (used for threshold tuning and model selection)
*   **Untouched Test Split (15% latest):** 88,581 rows (evaluated exactly once)

### Metrics Summary

| Split | PR-AUC | ROC-AUC | Precision | Recall | F1 Score |
| --- | --- | --- | --- | --- | --- |
| **Validation** | `0.6185` | `0.9306` | `0.3520` | `70.61%` | `0.4698` |
| **Untouched Test** | `0.5459` | `0.9057` | `0.2825` | `67.47%` | `0.3983` |

*   **Selected Operating Threshold:** `0.05` (optimal threshold that minimizes expected financial cost).
*   **Test Confusion Matrix:**
    *   True Negatives (TN): `80,216` | True Positives (TP): `2,080`
    *   False Positives (FP): `5,282` | False Negatives (FN): `1,003`
*   **Simulated Business Impact (Test Split):**
    *   Baseline Unmanaged Fraud Cost: **$462,450.00**
    *   FraudShield Managed Expected Cost: **$229,680.00**
    *   Net Savings Benefit: **$232,770.00**

---

## 6. Directory Layout
```text
razopayjon/
├── data/                       # IEEE-CIS transaction and identity CSV datasets
├── src/
│   ├── data_preparation.py     # Join, downcasting, and chronological split boundaries
│   ├── features.py             # Frequency encoders and custom feature transformers
│   ├── train_models.py         # Training routines for LR, XGBoost, and LightGBM
│   └── evaluate_models.py      # Threshold tuning, SHAP values, and test set evaluations
├── models/
│   ├── lightgbm_final.pkl      # Production LightGBM model
│   └── feature_pipeline.pkl    # Fitted preprocessing pipeline instance
├── reports/
│   ├── risk_policy.md          # Policy definitions and threshold guidelines
│   ├── phase3_report.md        # Model selection and evaluation metrics
│   ├── phase4_report.md        # FastAPI backend endpoint documentation
│   └── final_qa_report.md      # Final QA checklist and test results
├── backend/                    # FastAPI python app
└── frontend/                   # Next.js typescript client
```

---

## 7. Setup & Launch Guide

### 1. Backend Setup & Startup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
*   API runs locally at: [http://127.0.0.1:8000](http://127.0.0.1:8000)
*   Interactive OpenAPI Swagger documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
*   ReDoc documentation: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

#### Backend Testing
Run pytest from the repository root:
```bash
python -m pytest backend/tests/test_api.py
```

#### API Endpoints Overview
*   `GET /health` — Verifies API health and confirms loaded model type and decision threshold.
*   `GET /model-info` — Returns model metadata, validation metrics, test metrics, and limitations.
*   `POST /predict` — Real-time transaction scoring with fraud probability, risk level (`LOW`/`MEDIUM`/`HIGH`), recommended action (`APPROVE`/`REVIEW`), expected decision cost, and SHAP feature attributions.
*   `POST /predict/batch` — Multipart CSV file upload for vectorized batch transaction risk scoring.

### 2. Frontend Setup & Startup
```bash
cd frontend
npm install
npm run dev
```
Open the interactive dashboard UI at [http://localhost:3000](http://localhost:3000).

#### Frontend Commands
*   `npm run dev` — Launch development server
*   `npm run build` — Compile production build and run TypeScript checks
*   `npm run lint` — Run ESLint rules check

---

## 8. Important Limitations
1.  **Temporal Shift:** The test set PR-AUC dropped from `0.5372` to `0.4505`. This confirms temporal drift and requires periodic re-training and model updates.
2.  **No Causal Proof:** SHAP attributions represent statistical weight relative to training baselines, not real-world physical causation.
3.  **Missing Identity Information:** Device OS and Browser configurations are missing for ~75% of raw transactions, forcing high reliance on check-out velocity.
4.  **No Production Readiness Without Qualification:** Stated financial cost figures use demonstration assumptions and must be validated with merchant-specific parameters before production launch.
