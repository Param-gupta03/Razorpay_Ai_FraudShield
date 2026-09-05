# Phase 2 — Validation Strategy & Data Preparation Report

This report summarizes the results of Phase 2, covering chronological data splitting, data preparation, feature engineering, and data leakage verification.

## 1. Chronological Split Boundaries and Sizes

The data split is performed chronologically based on `TransactionDT` to simulate a realistic production scenario and prevent temporal leakage. 

*   **Training Set (Earliest 70%):** `TransactionDT` <= `10,437,998.10`
*   **Validation Set (Next 15%):** `10,437,998.10` < `TransactionDT` <= `13,151,846.00`
*   **Untouched Test Set (Latest 15%):** `TransactionDT` > `13,151,846.00`

### Split Statistics

| Split | Row Count | Percentage | Fraud Count | Fraud Rate | Time Span (DT Range) |
| --- | --- | --- | --- | --- | --- |
| **Train** | 413,378 | 70.00% | 14,538 | 3.5169% | `86,400` - `10,437,998` |
| **Validation** | 88,581 | 15.00% | 3,042 | 3.4341% | `10,438,007` - `13,151,846` |
| **Test (Untouched)** | 88,581 | 15.00% | 3,083 | 3.4804% | `13,151,878` - `15,811,131` |
| **Total** | 590,540 | 100.00% | 20,663 | 3.4990% | `86,400` - `15,811,131` |

> [!NOTE]
> The target fraud rate is highly stable across all three chronological splits (fluctuating only between 3.43% and 3.52%). This ensures that the validation and test sets are representative of the training set while remaining completely separated in time.

## 2. Dataset Merging & Column Policy

### Left Join Unification
The identity dataset `train_identity.csv` is merged onto `train_transaction.csv` using a `left join` on `TransactionID`. 
*   All **590,540** transaction rows are kept.
*   About **24.42%** of transaction rows have matching identity rows, resulting in some empty identity columns for the remaining transactions.

### Excluded Columns
*   `TransactionID`: Excluded from X (features) because it is a sequential identifier and acting as a proxy for time would leak ordering.
*   `isFraud`: Extracted as the target variable `y` and strictly removed from the model feature matrix `X`.

No other columns were dropped, to allow LightGBM/XGBoost to capture as many signals as possible.

## 3. Missing Value Handling

*   **Numerical Columns:** Left as-is. Tree-based models (LightGBM/XGBoost) will handle missing values natively, determining the optimal split direction for missing values during training.
*   **Categorical Columns:** NaNs and null values are explicitly filled with the category `'MISSING'` before converting to category type.
*   **Engineered Missingness Flags:**
    *   `nulls_count`: Total count of missing values in each row.
    *   `identity_nulls_count`: Total count of missing values in the identity-related fields for each row.

## 4. Feature Engineering Details

A total of **457 features** were prepared (33 Categorical, 424 Numerical). The pipeline engineered 25 new features:

1.  **Datetime extraction (from TransactionDT):**
    *   `hour`: Hour of the day (0–23)
    *   `day_of_week`: Day of the week (0–6)
2.  **Transaction Amount transformations:**
    *   `TransactionAmt_log`: Natural log `log(1 + TransactionAmt)` to compress extreme transaction values.
    *   `TransactionAmt_decimal`: Decimal part of `TransactionAmt` (often represents fractional amounts, card types, or currency conversions).
3.  **Missingness statistics:**
    *   `nulls_count`: Number of missing columns per transaction.
    *   `identity_nulls_count`: Number of missing identity fields (acts as a proxy for whether identity/device info was captured).
4.  **Email Domain group & match:**
    *   `email_match`: Direct match check between P-email and R-email (`1` if they match, `0` if they differ, `-1` if either is missing).
    *   `P_emaildomain_bin` / `R_emaildomain_bin`: Top-level email providers (e.g. `gmail`, `yahoo`, `hotmail`, etc.).
5.  **Device, OS & Resolution parsing (from Identity):**
    *   `screen_width` / `screen_height` / `screen_area` / `screen_aspect_ratio`: Parsed from `id_33` (e.g., `"1920x1080"`).
    *   `os_name`: Grouped OS names (Windows, iOS, Android, Mac, Linux, other, MISSING) parsed from `id_30`.
    *   `browser_name`: Grouped browsers (Chrome, Safari, Firefox, Edge, Samsung, Opera, IE, other, MISSING) parsed from `id_31`.
6.  **Card and Address Frequencies (Leakage-Safe Count Encoding):**
    *   Frequencies are computed **only** on the training set and mapped onto validation and test. Unseen values are set to `0`.
    *   Features include: `card1_count`, `card2_count`, `card3_count`, `card5_count`, `addr1_count`, `addr2_count`, `P_emaildomain_count`, `R_emaildomain_count`, `DeviceInfo_count`, and `card1_card2_count` (compound card frequency).

## 5. Explicit Data Leakage Assertions Passed

The following pipeline checks are ran as assertions during feature preparation:

*   **Zero Key Overlap:** Asserted that `Train_TransactionID` $\cap$ `Val_TransactionID` = $\emptyset$, `Train_TransactionID` $\cap$ `Test_TransactionID` = $\emptyset$, and `Val_TransactionID` $\cap$ `Test_TransactionID` = $\emptyset$.
*   **Strict Chronological Ordering:** Asserted that $\max(\text{Train DT}) \leq \min(\text{Val DT})$ and $\max(\text{Val DT}) \leq \min(\text{Test DT})$.
*   **Feature Isolation:** Asserted that `isFraud` and `TransactionID` are absent from X.
*   **Fit-Transform Isolation:** Verified that categorical frequencies and category sets are fit *only* on the training split, completely protecting validation and test sets from lookup leakage.

## 6. Memory & Performance Optimizations

1.  **Dtype Downcasting:** Downcasted floats to `float32` and integers to the smallest possible integer type (`int32`, `int16`, `int8`).
    *   `train_transaction.csv` memory reduced from **2,062.07 MB** to **861.11 MB** (**58.2% reduction**).
    *   `train_identity.csv` memory reduced from **143.14 MB** to **37.64 MB** (**73.7% reduction**).
2.  **Pickle Serialization:** Saved splits as `.pkl` files inside `data/processed/`. Pickling preserves pandas Categorical types natively and loads in less than 5 seconds.

## 7. How to Reproduce Phase 2

Run the following commands in the project directory:

```powershell
# 1. Runs the load, downcast, merge, split, and asserts splits integrity
python src/data_preparation.py

# 2. Runs the end-to-end feature pipeline, asserts feature integrity, saves pickles and feature metadata
python src/run_pipeline.py
```

### Generated Files
*   [`src/data_preparation.py`](file:///C:/Users/param/OneDrive/Desktop/razopayjon/src/data_preparation.py) — Merging, downcasting, splitting, and split assertions.
*   [`src/features.py`](file:///C:/Users/param/OneDrive/Desktop/razopayjon/src/features.py) — Fit-transform feature engineering pipeline.
*   [`src/run_pipeline.py`](file:///C:/Users/param/OneDrive/Desktop/razopayjon/src/run_pipeline.py) — Executable orchestration script for dataset transformations.
*   [`notebooks/01_data_preparation.ipynb`](file:///C:/Users/param/OneDrive/Desktop/razopayjon/notebooks/01_data_preparation.ipynb) — Visual Jupyter notebook showcasing step-by-step preparation.
*   [`reports/split_report.md`](file:///C:/Users/param/OneDrive/Desktop/razopayjon/reports/split_report.md) — Documentation of temporal split thresholds and sizes.
*   [`reports/feature_metadata.json`](file:///C:/Users/param/OneDrive/Desktop/razopayjon/reports/feature_metadata.json) — Serialization of all categorical/numerical features.
