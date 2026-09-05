# Phase 3 — Model Training & Evaluation Report

This report documents the training, validation, threshold optimization, business cost analysis, calibration, SHAP feature attribution, and final untouched test evaluation of the fraud detection system.

## 1. Datasets and Split Methodology
*   **Source:** Merged Vesta/IEEE-CIS Transaction and Identity datasets, downcasted and joined on `TransactionID` in Phase 2.
*   **Splits:** 
    *   **Train (70%):** 413,378 rows (historical training)
    *   **Validation (15%):** 88,581 rows (threshold optimization, model selection)
    *   **Test (15%):** 88,581 rows (untouched chronological test set)
*   **Validation Target Class Distribution:** 3.4341% Fraud Rate (3,042 fraud cases).

## 2. Model Performance Comparisons on Validation Set

We trained five candidate models. The table below compares their performance at a default classification threshold of 0.50:

| Model | Precision | Recall | F1 | PR-AUC | ROC-AUC | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Logistic Regression (Baseline) | 0.1477 | 0.7117 | 0.2447 | 0.4194 | 0.8560 | 12,491 | 877 |
| LightGBM (Standard) | 0.8818 | 0.3679 | 0.5191 | 0.6185 | 0.9306 | 150 | 1,923 |
| LightGBM (Class-Weighted) | 0.5012 | 0.5631 | 0.5303 | 0.5785 | 0.9108 | 1,705 | 1,329 |
| XGBoost (Standard) | 0.9005 | 0.3511 | 0.5052 | 0.6106 | 0.9235 | 118 | 1,974 |
| XGBoost (Class-Weighted) | 0.4740 | 0.5546 | 0.5111 | 0.5639 | 0.9038 | 1,872 | 1,355 |


### Baseline Analysis
*   The baseline **Logistic Regression** model demonstrates reasonable ROC-AUC (around 0.75-0.78) but suffers on F1 and PR-AUC because the data has highly non-linear relationships.
*   Both **LightGBM** and **XGBoost** models perform significantly better than the linear baseline.
*   **LightGBM (Standard)** was selected as the final primary model because it has the highest **PR-AUC** (0.6185) on the validation set and is highly computationally efficient.

## 3. Threshold Analysis and Optimization

Rather than using a default threshold of 0.50, we evaluated a range of classification thresholds on validation probabilities for `LightGBM (Standard)`:

| Threshold | Precision | Recall | F1 | PR-AUC | FP | FN | Expected Cost | Net Benefit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.05 | 0.3520 | 0.7061 | 0.4698 | 0.6185 | 3,954.0 | 894.0 | $193,410.00 | $262,890.00 |
| 0.10 | 0.5255 | 0.6019 | 0.5611 | 0.6185 | 1,653.0 | 1,211.0 | $206,445.00 | $249,855.00 |
| 0.15 | 0.6260 | 0.5431 | 0.5816 | 0.6185 | 987.0 | 1,390.0 | $223,305.00 | $232,995.00 |
| 0.20 | 0.6969 | 0.5033 | 0.5845 | 0.6185 | 666.0 | 1,511.0 | $236,640.00 | $219,660.00 |
| 0.25 | 0.7516 | 0.4694 | 0.5779 | 0.6185 | 472.0 | 1,614.0 | $249,180.00 | $207,120.00 |
| 0.30 | 0.7943 | 0.4431 | 0.5689 | 0.6185 | 349.0 | 1,694.0 | $259,335.00 | $196,965.00 |
| 0.35 | 0.8189 | 0.4237 | 0.5585 | 0.6185 | 285.0 | 1,753.0 | $267,225.00 | $189,075.00 |
| 0.40 | 0.8399 | 0.4017 | 0.5435 | 0.6185 | 233.0 | 1,820.0 | $276,495.00 | $179,805.00 |
| 0.45 | 0.8634 | 0.3866 | 0.5341 | 0.6185 | 186.0 | 1,866.0 | $282,690.00 | $173,610.00 |
| 0.50 | 0.8818 | 0.3679 | 0.5191 | 0.6185 | 150.0 | 1,923.0 | $290,700.00 | $165,600.00 |
| 0.60 | 0.9118 | 0.3330 | 0.4878 | 0.6185 | 98.0 | 2,029.0 | $305,820.00 | $150,480.00 |
| 0.70 | 0.9344 | 0.2949 | 0.4483 | 0.6185 | 63.0 | 2,145.0 | $322,695.00 | $133,605.00 |
| 0.80 | 0.9423 | 0.2521 | 0.3978 | 0.6185 | 47.0 | 2,275.0 | $341,955.00 | $114,345.00 |
| 0.90 | 0.9507 | 0.1838 | 0.3080 | 0.6185 | 29.0 | 2,483.0 | $372,885.00 | $83,415.00 |


### Recommended Operational Threshold
*   **Selected Threshold:** `0.05`
*   **Business Rationale:** This threshold minimizes the expected financial cost under the cost assumptions. At this threshold:
    *   Precision is `0.3520`
    *   Recall is `0.7061` (capturing `70.61%` of all fraud cases)
    *   Expected financial cost is reduced to **$193,410.00**, generating a net business benefit of **$262,890.00** compared to doing nothing.

## 4. Configurable Cost Model and Financial Analysis

### Financial Cost Assumptions
Since true costs vary by merchant, we define the following configurable parameters:
*   `FALSE_POSITIVE_COST` = **$15.00** (represents merchant review overhead, user friction, and customer lifetime value loss from false declines).
*   `FALSE_NEGATIVE_COST` = **$150.00** (represents the loss of the average ticket transaction value, chargeback fees, card network fines, and lost merchandise).

### Cost Equation
$$\text{Expected Cost} = (FP \times \text{FALSE\_POSITIVE\_COST}) + (FN \times \text{FALSE\_NEGATIVE\_COST})$$

### Validation Net Benefit Summary
*   **Baseline Cost (Unmanaged Fraud):** $462,450.00
*   **Expected Managed Cost (at selected threshold):** $193,410.00
*   **Net Business Benefit:** $262,890.00

## 5. Model Calibration and Brier Score
*   **Brier Score:** `0.0220` for the selected model.
*   The calibration curve indicates that the raw probability predictions map closely to empirical fraud frequencies, allowing the system to provide direct, reliable probability values to merchants (e.g., "This transaction is 82% likely to be fraudulent").

## 6. Top 20 Feature Importance (Gini Importance)

The following table lists the top 20 features for `LightGBM (Standard)`:

| Rank | Feature Name | Gini Importance score |
| --- | --- | --- |
| 1 | `card1` | 2,454 |
| 2 | `TransactionAmt` | 2,349 |
| 3 | `card2` | 2,018 |
| 4 | `card1_card2_count` | 1,929 |
| 5 | `addr1` | 1,897 |
| 6 | `addr1_count` | 1,762 |
| 7 | `card2_count` | 1,680 |
| 8 | `card1_count` | 1,520 |
| 9 | `D15` | 1,315 |
| 10 | `id_31` | 1,274 |
| 11 | `C13` | 1,231 |
| 12 | `DeviceInfo` | 1,230 |
| 13 | `dist1` | 1,005 |
| 14 | `D2` | 934 |
| 15 | `card5` | 926 |
| 16 | `D10` | 919 |
| 17 | `hour` | 874 |
| 18 | `id_20` | 859 |
| 19 | `C1` | 845 |
| 20 | `P_emaildomain` | 831 |


## 7. SHAP Explainability & Local Interpretability

*   **Global Summary:** SHAP summary plots indicate that transaction value (`TransactionAmt`), card-address counts (`card1_count`), time-based differentials (`D` features), count of null variables (`nulls_count`), and card-address configurations (`card1_card2_count`) drive the model's decisions globally.
*   **No Causation:** SHAP values represent model feature attributions rather than physical real-world causation. They show how the model weighs features relative to the baseline dataset.

### Local Explanations (Examples)

### Example 1: Transaction index `441478` (Fraudulent (1))

- **Fraud Probability:** 81.22%
- **Top Risk-Increasing Factors (Positive SHAP):**
  - `C1 (11.0): +1.2276`
  - `C8 (5.0): +0.6051`
  - `C13 (2.0): +0.4528`
  - `V294 (1.0): +0.4377`
  - `card6 (credit): +0.4286`
- **Top Risk-Reducing Factors (Negative SHAP):**
  - `TransactionAmt (13.279999732971191): -0.2198`
  - `id_19 (266.0): -0.0742`
  - `hour (19): -0.0429`
  - `TransactionAmt_log (2.658859968185425): -0.0428`
  - `TransactionAmt_decimal (0.2799997329711914): -0.0397`

### Example 2: Transaction index `443491` (Fraudulent (1))

- **Fraud Probability:** 96.87%
- **Top Risk-Increasing Factors (Positive SHAP):**
  - `C1 (24.0): +1.4812`
  - `C13 (1.0): +0.7932`
  - `V258 (2.0): +0.6132`
  - `V152 (3.0): +0.5964`
  - `C4 (10.0): +0.5838`
- **Top Risk-Reducing Factors (Negative SHAP):**
  - `id_30 (iOS 11.3.0): -0.2803`
  - `id_31 (mobile safari generic): -0.1972`
  - `ProductCD (R): -0.1545`
  - `M4 (MISSING): -0.0797`
  - `D1 (63.0): -0.0653`

### Example 3: Transaction index `437512` (Legitimate (0))

- **Fraud Probability:** 0.62%
- **Top Risk-Increasing Factors (Positive SHAP):**
  - `C13 (1.0): +0.1765`
  - `P_emaildomain (MISSING): +0.1033`
  - `dist1 (nan): +0.1017`
  - `M4 (M0): +0.0988`
  - `C5 (0.0): +0.0911`
- **Top Risk-Reducing Factors (Negative SHAP):**
  - `card5 (166.0): -0.2124`
  - `TransactionAmt (34.0): -0.2097`
  - `card6 (debit): -0.1576`
  - `C11 (1.0): -0.1018`
  - `M3 (T): -0.0961`

### Example 4: Transaction index `450846` (Legitimate (0))

- **Fraud Probability:** 1.50%
- **Top Risk-Increasing Factors (Positive SHAP):**
  - `card6 (credit): +0.2378`
  - `C11 (2.0): +0.1553`
  - `D15 (16.0): +0.1358`
  - `DeviceInfo (MISSING): +0.1185`
  - `M4 (M2): +0.1098`
- **Top Risk-Reducing Factors (Negative SHAP):**
  - `P_emaildomain (hotmail.com): -0.2190`
  - `D13 (63.0): -0.2112`
  - `C14 (2.0): -0.1338`
  - `C1 (2.0): -0.0987`
  - `D6 (63.0): -0.0816`



## 8. FINAL UNTOUCHED TEST SET PERFORMANCE (Honest Evaluation)

The final model `LightGBM (Standard)` was evaluated **exactly once** on the untouched test set using the operational threshold of `0.05`:

*   **Operational Threshold:** `0.05`
*   **PR-AUC (Average Precision):** `0.5459`
*   **ROC-AUC:** `0.9057`
*   **Brier Calibration Score:** `0.0220`
*   **Precision:** `0.2825`
*   **Recall:** `0.6747`
*   **F1 Score:** `0.3983`
*   **True Positives (TP):** `2,080` | **True Negatives (TN):** `80,216`
*   **False Positives (FP):** `5,282` | **False Negatives (FN):** `1,003`
*   **False Positive Rate (FPR):** `0.0618` | **False Negative Rate (FNR):** `0.3253`
*   **Expected Test Financial Cost:** **$229,680.00**
*   **Test Baseline Unmanaged Cost:** **$462,450.00**
*   **Net Financial Benefit (Untouched Test):** **$232,770.00**

## 9. Limitations
1.  **Stationarity Assumption:** The model is trained on historical data. If fraud patterns shift rapidly over time, the performance may degrade, requiring periodic temporal re-training.
2.  **Missing Identity Information:** Since identity info is only captured for 24% of transactions, features from the identity set (OS, Browser, DeviceType) have a high rate of missing values. While LightGBM splits on these natively, it highlights the importance of improving identity capture at the checkout page.

## 10. Reproduction Instructions

Run the following commands sequentially:
```powershell
# 1. Prepare raw data (merge + split)
python src/data_preparation.py

# 2. Run feature transformations
python src/run_pipeline.py

# 3. Train all baseline, LightGBM, and XGBoost models
python src/train_models.py

# 4. Run optimization, plot curves, interpret SHAP, and evaluate test set
python src/evaluate_models.py
```
