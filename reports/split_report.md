# Data Split Report

This report documents the temporal chronological split strategy applied to the merged dataset.

## 1. Split Thresholds

- **Methodology:** Split chronologically using percentiles of the `TransactionDT` column.
- **Train/Validation Split Boundary (`TransactionDT`):** 10,437,998.10
- **Validation/Test Split Boundary (`TransactionDT`):** 13,151,846.00

## 2. Split Size and Target Statistics

| Split | Row Count | Percentage | Fraud Count | Fraud Rate | Time Span (DT Range) |
| --- | --- | --- | --- | --- | --- |
| **Train** | 413,378 | 70.00% | 14,538 | 3.5169% | `86,400` - `10,437,996` |
| **Validation** | 88,581 | 15.00% | 3,042 | 3.4341% | `10,438,003` - `13,151,840` |
| **Test (Untouched)** | 88,581 | 15.00% | 3,083 | 3.4804% | `13,151,880` - `15,811,131` |
| **Total** | 590,540 | 100.00% | 20,663 | 3.4990% | `86,400` - `15,811,131` |

## 3. Data Integrity & Leakage Assertions

- **Zero TransactionID Overlap:** Checked. (Verified that train, validation, and test datasets share exactly zero transaction identifiers).
- **Strict Chronological Ordering:** Checked. (Verified that train timestamps occur entirely before validation, and validation timestamps occur entirely before test timestamps).
- **Target Availability:** Checked. (Verified that `isFraud` target exists across all sets and maintains consistent class proportions of ~3.4% - 3.5%).
