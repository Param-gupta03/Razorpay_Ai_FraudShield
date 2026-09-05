# Data Audit Report

This report provides a detailed data audit of the datasets located in the `data/` directory. This audit is designed to be memory-efficient and run without loading full copies of large files into memory.

## 1. File Overview

| Filename | File Size (MB) | Number of Rows | Number of Columns | Estimated Memory Usage (MB) |
| --- | --- | --- | --- | --- |
| `train_transaction.csv` | 651.69 | 590,540 | 394 | 2048.27 |
| `train_identity.csv` | 25.30 | 144,233 | 41 | 143.89 |

## 2. Target Column & Class Distribution

The target column `isFraud` **is present** in the transaction dataset.

| Class (isFraud) | Count | Percentage |
| --- | --- | --- |
| 0 | 569,877 | 96.5010% |
| 1 | 20,663 | 3.4990% |

**Class Imbalance Ratio (Majority:Minority):** 27.58:1

## 3. Duplicate and Unique Key Analysis

| Dataset | Unique `TransactionID` | Duplicate `TransactionID` | Unique Row Count (Hash-based) | Total Row Count | Duplicate Rows |
| --- | --- | --- | --- | --- | --- |
| `train_transaction.csv` | 590,540 | 0 | 590,540 | 590,540 | 0 |
| `train_identity.csv` | 144,233 | 0 | 144,233 | 144,233 | 0 |

- **`TransactionID` Uniqueness:** `TransactionID` is unique in both tables (there are 0 duplicate IDs).
- **Duplicate Rows:** There are 0 duplicate rows in both files (each row has a unique combination of values).

## 4. Relationship between Transaction and Identity

- **Transaction Rows:** 590,540
- **Identity Rows:** 144,233
- **Overlapping Transactions (in both):** 144,233
- **Percentage of Transactions with Identity Info:** 24.42%
- **Percentage of Identity Records with Transaction Info:** 100.00%

> [!NOTE]
> The identity dataset contains additional details (IP, device, browser, etc.) for a subset of transactions (about 24.4% of them). When merging, we should perform a **left join** from Transaction to Identity to keep all transaction records.

## 5. Column Breakdown (Data Types and Missing Values)

### `train_transaction.csv` Column Statistics

| Column Name | Data Type | Missing Count | Missing Percentage | Unique Values (Categorical/Low Card) |
| --- | --- | --- | --- | --- |
| `TransactionID` | `int64` | 0 | 0.00% | N/A (Continuous) |
| `isFraud` | `int64` | 0 | 0.00% | 2 |
| `TransactionDT` | `int64` | 0 | 0.00% | N/A (Continuous) |
| `TransactionAmt` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `ProductCD` | `str` | 0 | 0.00% | 5 |
| `card1` | `int64` | 0 | 0.00% | N/A (Continuous) |
| `card2` | `float64` | 8,933 | 1.51% | N/A (Continuous) |
| `card3` | `float64` | 1,565 | 0.27% | N/A (Continuous) |
| `card4` | `str` | 1,577 | 0.27% | 4 |
| `card5` | `float64` | 4,259 | 0.72% | N/A (Continuous) |
| `card6` | `str` | 1,571 | 0.27% | 4 |
| `addr1` | `float64` | 65,706 | 11.13% | N/A (Continuous) |
| `addr2` | `float64` | 65,706 | 11.13% | N/A (Continuous) |
| `dist1` | `float64` | 352,271 | 59.65% | N/A (Continuous) |
| `dist2` | `float64` | 552,913 | 93.63% | N/A (Continuous) |
| `P_emaildomain` | `str` | 94,456 | 15.99% | N/A (Continuous) |
| `R_emaildomain` | `str` | 453,249 | 76.75% | N/A (Continuous) |
| `C1` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `C2` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `C3` | `float64` | 0 | 0.00% | 27 |
| `C4` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `C5` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `C6` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `C7` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `C8` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `C9` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `C10` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `C11` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `C12` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `C13` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `C14` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `D1` | `float64` | 1,269 | 0.21% | N/A (Continuous) |
| `D2` | `float64` | 280,797 | 47.55% | N/A (Continuous) |
| `D3` | `float64` | 262,878 | 44.51% | N/A (Continuous) |
| `D4` | `float64` | 168,922 | 28.60% | N/A (Continuous) |
| `D5` | `float64` | 309,841 | 52.47% | N/A (Continuous) |
| `D6` | `float64` | 517,353 | 87.61% | N/A (Continuous) |
| `D7` | `float64` | 551,623 | 93.41% | N/A (Continuous) |
| `D8` | `float64` | 515,614 | 87.31% | N/A (Continuous) |
| `D9` | `float64` | 515,614 | 87.31% | 24 |
| `D10` | `float64` | 76,022 | 12.87% | N/A (Continuous) |
| `D11` | `float64` | 279,287 | 47.29% | N/A (Continuous) |
| `D12` | `float64` | 525,823 | 89.04% | N/A (Continuous) |
| `D13` | `float64` | 528,588 | 89.51% | N/A (Continuous) |
| `D14` | `float64` | 528,353 | 89.47% | N/A (Continuous) |
| `D15` | `float64` | 89,113 | 15.09% | N/A (Continuous) |
| `M1` | `str` | 271,100 | 45.91% | 2 |
| `M2` | `str` | 271,100 | 45.91% | 2 |
| `M3` | `str` | 271,100 | 45.91% | 2 |
| `M4` | `str` | 281,444 | 47.66% | 3 |
| `M5` | `str` | 350,482 | 59.35% | 2 |
| `M6` | `str` | 169,360 | 28.68% | 2 |
| `M7` | `str` | 346,265 | 58.64% | 2 |
| `M8` | `str` | 346,252 | 58.63% | 2 |
| `M9` | `str` | 346,252 | 58.63% | 2 |
| `V1` | `float64` | 279,287 | 47.29% | 2 |
| `V2` | `float64` | 279,287 | 47.29% | 9 |
| `V3` | `float64` | 279,287 | 47.29% | 10 |
| `V4` | `float64` | 279,287 | 47.29% | 7 |
| `V5` | `float64` | 279,287 | 47.29% | 7 |
| `V6` | `float64` | 279,287 | 47.29% | 10 |
| `V7` | `float64` | 279,287 | 47.29% | 10 |
| `V8` | `float64` | 279,287 | 47.29% | 9 |
| `V9` | `float64` | 279,287 | 47.29% | 9 |
| `V10` | `float64` | 279,287 | 47.29% | 5 |
| `V11` | `float64` | 279,287 | 47.29% | 6 |
| `V12` | `float64` | 76,073 | 12.88% | 4 |
| `V13` | `float64` | 76,073 | 12.88% | 7 |
| `V14` | `float64` | 76,073 | 12.88% | 2 |
| `V15` | `float64` | 76,073 | 12.88% | 8 |
| `V16` | `float64` | 76,073 | 12.88% | 15 |
| `V17` | `float64` | 76,073 | 12.88% | 16 |
| `V18` | `float64` | 76,073 | 12.88% | 16 |
| `V19` | `float64` | 76,073 | 12.88% | 8 |
| `V20` | `float64` | 76,073 | 12.88% | 15 |
| `V21` | `float64` | 76,073 | 12.88% | 6 |
| `V22` | `float64` | 76,073 | 12.88% | 9 |
| `V23` | `float64` | 76,073 | 12.88% | 14 |
| `V24` | `float64` | 76,073 | 12.88% | 14 |
| `V25` | `float64` | 76,073 | 12.88% | 7 |
| `V26` | `float64` | 76,073 | 12.88% | 13 |
| `V27` | `float64` | 76,073 | 12.88% | 4 |
| `V28` | `float64` | 76,073 | 12.88% | 4 |
| `V29` | `float64` | 76,073 | 12.88% | 6 |
| `V30` | `float64` | 76,073 | 12.88% | 8 |
| `V31` | `float64` | 76,073 | 12.88% | 8 |
| `V32` | `float64` | 76,073 | 12.88% | 15 |
| `V33` | `float64` | 76,073 | 12.88% | 7 |
| `V34` | `float64` | 76,073 | 12.88% | 13 |
| `V35` | `float64` | 168,969 | 28.61% | 4 |
| `V36` | `float64` | 168,969 | 28.61% | 6 |
| `V37` | `float64` | 168,969 | 28.61% | N/A (Continuous) |
| `V38` | `float64` | 168,969 | 28.61% | N/A (Continuous) |
| `V39` | `float64` | 168,969 | 28.61% | 16 |
| `V40` | `float64` | 168,969 | 28.61% | 18 |
| `V41` | `float64` | 168,969 | 28.61% | 2 |
| `V42` | `float64` | 168,969 | 28.61% | 9 |
| `V43` | `float64` | 168,969 | 28.61% | 9 |
| `V44` | `float64` | 168,969 | 28.61% | 49 |
| `V45` | `float64` | 168,969 | 28.61% | 49 |
| `V46` | `float64` | 168,969 | 28.61% | 7 |
| `V47` | `float64` | 168,969 | 28.61% | 9 |
| `V48` | `float64` | 168,969 | 28.61% | 6 |
| `V49` | `float64` | 168,969 | 28.61% | 6 |
| `V50` | `float64` | 168,969 | 28.61% | 6 |
| `V51` | `float64` | 168,969 | 28.61% | 7 |
| `V52` | `float64` | 168,969 | 28.61% | 9 |
| `V53` | `float64` | 77,096 | 13.06% | 6 |
| `V54` | `float64` | 77,096 | 13.06% | 7 |
| `V55` | `float64` | 77,096 | 13.06% | 18 |
| `V56` | `float64` | 77,096 | 13.06% | N/A (Continuous) |
| `V57` | `float64` | 77,096 | 13.06% | 7 |
| `V58` | `float64` | 77,096 | 13.06% | 11 |
| `V59` | `float64` | 77,096 | 13.06% | 17 |
| `V60` | `float64` | 77,096 | 13.06% | 17 |
| `V61` | `float64` | 77,096 | 13.06% | 7 |
| `V62` | `float64` | 77,096 | 13.06% | 11 |
| `V63` | `float64` | 77,096 | 13.06% | 8 |
| `V64` | `float64` | 77,096 | 13.06% | 8 |
| `V65` | `float64` | 77,096 | 13.06% | 2 |
| `V66` | `float64` | 77,096 | 13.06% | 8 |
| `V67` | `float64` | 77,096 | 13.06% | 9 |
| `V68` | `float64` | 77,096 | 13.06% | 3 |
| `V69` | `float64` | 77,096 | 13.06% | 6 |
| `V70` | `float64` | 77,096 | 13.06% | 7 |
| `V71` | `float64` | 77,096 | 13.06% | 7 |
| `V72` | `float64` | 77,096 | 13.06% | 11 |
| `V73` | `float64` | 77,096 | 13.06% | 8 |
| `V74` | `float64` | 77,096 | 13.06% | 9 |
| `V75` | `float64` | 89,164 | 15.10% | 5 |
| `V76` | `float64` | 89,164 | 15.10% | 7 |
| `V77` | `float64` | 89,164 | 15.10% | 31 |
| `V78` | `float64` | 89,164 | 15.10% | 32 |
| `V79` | `float64` | 89,164 | 15.10% | 8 |
| `V80` | `float64` | 89,164 | 15.10% | 20 |
| `V81` | `float64` | 89,164 | 15.10% | 20 |
| `V82` | `float64` | 89,164 | 15.10% | 8 |
| `V83` | `float64` | 89,164 | 15.10% | 8 |
| `V84` | `float64` | 89,164 | 15.10% | 8 |
| `V85` | `float64` | 89,164 | 15.10% | 8 |
| `V86` | `float64` | 89,164 | 15.10% | 31 |
| `V87` | `float64` | 89,164 | 15.10% | 31 |
| `V88` | `float64` | 89,164 | 15.10% | 2 |
| `V89` | `float64` | 89,164 | 15.10% | 3 |
| `V90` | `float64` | 89,164 | 15.10% | 6 |
| `V91` | `float64` | 89,164 | 15.10% | 7 |
| `V92` | `float64` | 89,164 | 15.10% | 8 |
| `V93` | `float64` | 89,164 | 15.10% | 8 |
| `V94` | `float64` | 89,164 | 15.10% | 3 |
| `V95` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V96` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V97` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V98` | `float64` | 314 | 0.05% | 13 |
| `V99` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V100` | `float64` | 314 | 0.05% | 29 |
| `V101` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V102` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V103` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V104` | `float64` | 314 | 0.05% | 16 |
| `V105` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V106` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V107` | `float64` | 314 | 0.05% | 2 |
| `V108` | `float64` | 314 | 0.05% | 8 |
| `V109` | `float64` | 314 | 0.05% | 8 |
| `V110` | `float64` | 314 | 0.05% | 8 |
| `V111` | `float64` | 314 | 0.05% | 10 |
| `V112` | `float64` | 314 | 0.05% | 10 |
| `V113` | `float64` | 314 | 0.05% | 10 |
| `V114` | `float64` | 314 | 0.05% | 7 |
| `V115` | `float64` | 314 | 0.05% | 7 |
| `V116` | `float64` | 314 | 0.05% | 7 |
| `V117` | `float64` | 314 | 0.05% | 4 |
| `V118` | `float64` | 314 | 0.05% | 4 |
| `V119` | `float64` | 314 | 0.05% | 4 |
| `V120` | `float64` | 314 | 0.05% | 4 |
| `V121` | `float64` | 314 | 0.05% | 4 |
| `V122` | `float64` | 314 | 0.05% | 4 |
| `V123` | `float64` | 314 | 0.05% | 14 |
| `V124` | `float64` | 314 | 0.05% | 14 |
| `V125` | `float64` | 314 | 0.05% | 14 |
| `V126` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V127` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V128` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V129` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V130` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V131` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V132` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V133` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V134` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V135` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V136` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V137` | `float64` | 314 | 0.05% | N/A (Continuous) |
| `V138` | `float64` | 508,595 | 86.12% | 23 |
| `V139` | `float64` | 508,595 | 86.12% | 34 |
| `V140` | `float64` | 508,595 | 86.12% | 34 |
| `V141` | `float64` | 508,595 | 86.12% | 6 |
| `V142` | `float64` | 508,595 | 86.12% | 10 |
| `V143` | `float64` | 508,589 | 86.12% | N/A (Continuous) |
| `V144` | `float64` | 508,589 | 86.12% | N/A (Continuous) |
| `V145` | `float64` | 508,589 | 86.12% | N/A (Continuous) |
| `V146` | `float64` | 508,595 | 86.12% | 25 |
| `V147` | `float64` | 508,595 | 86.12% | 27 |
| `V148` | `float64` | 508,595 | 86.12% | 21 |
| `V149` | `float64` | 508,595 | 86.12% | 21 |
| `V150` | `float64` | 508,589 | 86.12% | N/A (Continuous) |
| `V151` | `float64` | 508,589 | 86.12% | N/A (Continuous) |
| `V152` | `float64` | 508,589 | 86.12% | 39 |
| `V153` | `float64` | 508,595 | 86.12% | 19 |
| `V154` | `float64` | 508,595 | 86.12% | 19 |
| `V155` | `float64` | 508,595 | 86.12% | 25 |
| `V156` | `float64` | 508,595 | 86.12% | 25 |
| `V157` | `float64` | 508,595 | 86.12% | 25 |
| `V158` | `float64` | 508,595 | 86.12% | 25 |
| `V159` | `float64` | 508,589 | 86.12% | N/A (Continuous) |
| `V160` | `float64` | 508,589 | 86.12% | N/A (Continuous) |
| `V161` | `float64` | 508,595 | 86.12% | N/A (Continuous) |
| `V162` | `float64` | 508,595 | 86.12% | N/A (Continuous) |
| `V163` | `float64` | 508,595 | 86.12% | N/A (Continuous) |
| `V164` | `float64` | 508,589 | 86.12% | N/A (Continuous) |
| `V165` | `float64` | 508,589 | 86.12% | N/A (Continuous) |
| `V166` | `float64` | 508,589 | 86.12% | N/A (Continuous) |
| `V167` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V168` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V169` | `float64` | 450,721 | 76.32% | 20 |
| `V170` | `float64` | 450,721 | 76.32% | 49 |
| `V171` | `float64` | 450,721 | 76.32% | N/A (Continuous) |
| `V172` | `float64` | 450,909 | 76.36% | 32 |
| `V173` | `float64` | 450,909 | 76.36% | 8 |
| `V174` | `float64` | 450,721 | 76.32% | 9 |
| `V175` | `float64` | 450,721 | 76.32% | 15 |
| `V176` | `float64` | 450,909 | 76.36% | 49 |
| `V177` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V178` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V179` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V180` | `float64` | 450,721 | 76.32% | N/A (Continuous) |
| `V181` | `float64` | 450,909 | 76.36% | 25 |
| `V182` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V183` | `float64` | 450,909 | 76.36% | 42 |
| `V184` | `float64` | 450,721 | 76.32% | 17 |
| `V185` | `float64` | 450,721 | 76.32% | 32 |
| `V186` | `float64` | 450,909 | 76.36% | 39 |
| `V187` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V188` | `float64` | 450,721 | 76.32% | 31 |
| `V189` | `float64` | 450,721 | 76.32% | 31 |
| `V190` | `float64` | 450,909 | 76.36% | 43 |
| `V191` | `float64` | 450,909 | 76.36% | 22 |
| `V192` | `float64` | 450,909 | 76.36% | 45 |
| `V193` | `float64` | 450,909 | 76.36% | 38 |
| `V194` | `float64` | 450,721 | 76.32% | 8 |
| `V195` | `float64` | 450,721 | 76.32% | 17 |
| `V196` | `float64` | 450,909 | 76.36% | 39 |
| `V197` | `float64` | 450,721 | 76.32% | 15 |
| `V198` | `float64` | 450,721 | 76.32% | 22 |
| `V199` | `float64` | 450,909 | 76.36% | 46 |
| `V200` | `float64` | 450,721 | 76.32% | 46 |
| `V201` | `float64` | 450,721 | 76.32% | N/A (Continuous) |
| `V202` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V203` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V204` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V205` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V206` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V207` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V208` | `float64` | 450,721 | 76.32% | N/A (Continuous) |
| `V209` | `float64` | 450,721 | 76.32% | N/A (Continuous) |
| `V210` | `float64` | 450,721 | 76.32% | N/A (Continuous) |
| `V211` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V212` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V213` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V214` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V215` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V216` | `float64` | 450,909 | 76.36% | N/A (Continuous) |
| `V217` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V218` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V219` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V220` | `float64` | 449,124 | 76.05% | 26 |
| `V221` | `float64` | 449,124 | 76.05% | N/A (Continuous) |
| `V222` | `float64` | 449,124 | 76.05% | N/A (Continuous) |
| `V223` | `float64` | 460,110 | 77.91% | 17 |
| `V224` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V225` | `float64` | 460,110 | 77.91% | 35 |
| `V226` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V227` | `float64` | 449,124 | 76.05% | N/A (Continuous) |
| `V228` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V229` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V230` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V231` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V232` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V233` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V234` | `float64` | 449,124 | 76.05% | N/A (Continuous) |
| `V235` | `float64` | 460,110 | 77.91% | 24 |
| `V236` | `float64` | 460,110 | 77.91% | 46 |
| `V237` | `float64` | 460,110 | 77.91% | 40 |
| `V238` | `float64` | 449,124 | 76.05% | 24 |
| `V239` | `float64` | 449,124 | 76.05% | 24 |
| `V240` | `float64` | 460,110 | 77.91% | 6 |
| `V241` | `float64` | 460,110 | 77.91% | 5 |
| `V242` | `float64` | 460,110 | 77.91% | 21 |
| `V243` | `float64` | 460,110 | 77.91% | 43 |
| `V244` | `float64` | 460,110 | 77.91% | 23 |
| `V245` | `float64` | 449,124 | 76.05% | N/A (Continuous) |
| `V246` | `float64` | 460,110 | 77.91% | 46 |
| `V247` | `float64` | 460,110 | 77.91% | 19 |
| `V248` | `float64` | 460,110 | 77.91% | 23 |
| `V249` | `float64` | 460,110 | 77.91% | 23 |
| `V250` | `float64` | 449,124 | 76.05% | 19 |
| `V251` | `float64` | 449,124 | 76.05% | 19 |
| `V252` | `float64` | 460,110 | 77.91% | 25 |
| `V253` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V254` | `float64` | 460,110 | 77.91% | 45 |
| `V255` | `float64` | 449,124 | 76.05% | 46 |
| `V256` | `float64` | 449,124 | 76.05% | 48 |
| `V257` | `float64` | 460,110 | 77.91% | 49 |
| `V258` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V259` | `float64` | 449,124 | 76.05% | N/A (Continuous) |
| `V260` | `float64` | 460,110 | 77.91% | 9 |
| `V261` | `float64` | 460,110 | 77.91% | 41 |
| `V262` | `float64` | 460,110 | 77.91% | 21 |
| `V263` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V264` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V265` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V266` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V267` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V268` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V269` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V270` | `float64` | 449,124 | 76.05% | N/A (Continuous) |
| `V271` | `float64` | 449,124 | 76.05% | N/A (Continuous) |
| `V272` | `float64` | 449,124 | 76.05% | N/A (Continuous) |
| `V273` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V274` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V275` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V276` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V277` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V278` | `float64` | 460,110 | 77.91% | N/A (Continuous) |
| `V279` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V280` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V281` | `float64` | 1,269 | 0.21% | 23 |
| `V282` | `float64` | 1,269 | 0.21% | 33 |
| `V283` | `float64` | 1,269 | 0.21% | N/A (Continuous) |
| `V284` | `float64` | 12 | 0.00% | 13 |
| `V285` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V286` | `float64` | 12 | 0.00% | 9 |
| `V287` | `float64` | 12 | 0.00% | 32 |
| `V288` | `float64` | 1,269 | 0.21% | 11 |
| `V289` | `float64` | 1,269 | 0.21% | 13 |
| `V290` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V291` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V292` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V293` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V294` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V295` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V296` | `float64` | 1,269 | 0.21% | N/A (Continuous) |
| `V297` | `float64` | 12 | 0.00% | 13 |
| `V298` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V299` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V300` | `float64` | 1,269 | 0.21% | 12 |
| `V301` | `float64` | 1,269 | 0.21% | 14 |
| `V302` | `float64` | 12 | 0.00% | 17 |
| `V303` | `float64` | 12 | 0.00% | 21 |
| `V304` | `float64` | 12 | 0.00% | 17 |
| `V305` | `float64` | 12 | 0.00% | 2 |
| `V306` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V307` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V308` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V309` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V310` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V311` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V312` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V313` | `float64` | 1,269 | 0.21% | N/A (Continuous) |
| `V314` | `float64` | 1,269 | 0.21% | N/A (Continuous) |
| `V315` | `float64` | 1,269 | 0.21% | N/A (Continuous) |
| `V316` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V317` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V318` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V319` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V320` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V321` | `float64` | 12 | 0.00% | N/A (Continuous) |
| `V322` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V323` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V324` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V325` | `float64` | 508,189 | 86.05% | 13 |
| `V326` | `float64` | 508,189 | 86.05% | 45 |
| `V327` | `float64` | 508,189 | 86.05% | 19 |
| `V328` | `float64` | 508,189 | 86.05% | 16 |
| `V329` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V330` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V331` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V332` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V333` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V334` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V335` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V336` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V337` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V338` | `float64` | 508,189 | 86.05% | N/A (Continuous) |
| `V339` | `float64` | 508,189 | 86.05% | N/A (Continuous) |

### `train_identity.csv` Column Statistics

| Column Name | Data Type | Missing Count | Missing Percentage | Unique Values (Categorical/Low Card) |
| --- | --- | --- | --- | --- |
| `TransactionID` | `int64` | 0 | 0.00% | N/A (Continuous) |
| `id_01` | `float64` | 0 | 0.00% | N/A (Continuous) |
| `id_02` | `float64` | 3,361 | 2.33% | N/A (Continuous) |
| `id_03` | `float64` | 77,909 | 54.02% | 24 |
| `id_04` | `float64` | 77,909 | 54.02% | 15 |
| `id_05` | `float64` | 7,368 | 5.11% | N/A (Continuous) |
| `id_06` | `float64` | 7,368 | 5.11% | N/A (Continuous) |
| `id_07` | `float64` | 139,078 | 96.43% | N/A (Continuous) |
| `id_08` | `float64` | 139,078 | 96.43% | N/A (Continuous) |
| `id_09` | `float64` | 69,307 | 48.05% | 46 |
| `id_10` | `float64` | 69,307 | 48.05% | N/A (Continuous) |
| `id_11` | `float64` | 3,255 | 2.26% | N/A (Continuous) |
| `id_12` | `str` | 0 | 0.00% | 2 |
| `id_13` | `float64` | 16,913 | 11.73% | N/A (Continuous) |
| `id_14` | `float64` | 64,189 | 44.50% | 25 |
| `id_15` | `str` | 3,248 | 2.25% | 3 |
| `id_16` | `str` | 14,893 | 10.33% | 2 |
| `id_17` | `float64` | 4,864 | 3.37% | N/A (Continuous) |
| `id_18` | `float64` | 99,120 | 68.72% | 18 |
| `id_19` | `float64` | 4,915 | 3.41% | N/A (Continuous) |
| `id_20` | `float64` | 4,972 | 3.45% | N/A (Continuous) |
| `id_21` | `float64` | 139,074 | 96.42% | N/A (Continuous) |
| `id_22` | `float64` | 139,064 | 96.42% | 25 |
| `id_23` | `str` | 139,064 | 96.42% | 3 |
| `id_24` | `float64` | 139,486 | 96.71% | 12 |
| `id_25` | `float64` | 139,101 | 96.44% | N/A (Continuous) |
| `id_26` | `float64` | 139,070 | 96.42% | N/A (Continuous) |
| `id_27` | `str` | 139,064 | 96.42% | 2 |
| `id_28` | `str` | 3,255 | 2.26% | 2 |
| `id_29` | `str` | 3,255 | 2.26% | 2 |
| `id_30` | `str` | 66,668 | 46.22% | N/A (Continuous) |
| `id_31` | `str` | 3,951 | 2.74% | N/A (Continuous) |
| `id_32` | `float64` | 66,647 | 46.21% | 4 |
| `id_33` | `str` | 70,944 | 49.19% | N/A (Continuous) |
| `id_34` | `str` | 66,428 | 46.06% | 4 |
| `id_35` | `str` | 3,248 | 2.25% | 2 |
| `id_36` | `str` | 3,248 | 2.25% | 2 |
| `id_37` | `str` | 3,248 | 2.25% | 2 |
| `id_38` | `str` | 3,248 | 2.25% | 2 |
| `DeviceType` | `str` | 3,423 | 2.37% | 2 |
| `DeviceInfo` | `str` | 25,567 | 17.73% | N/A (Continuous) |

## 6. Suspicious / Leakage-Prone Columns and Engineering Notes

- **`TransactionID`**: This is a unique transaction identifier. It must NOT be used directly as a feature in model training because it can act as a proxy for time/order and lead to serious data leakage.
- **`TransactionDT`**: This represents the elapsed time in seconds from a reference point. In practice, this serves as the timestamp. Random train/test splits would leak future information to past predictions. We must use a **temporal train/test split** (e.g., splitting by the last 20% of `TransactionDT` or another time-based division) to ensure the system is evaluated realistically on unseen future transactions.
- **`isFraud`**: The target label. Must be strictly removed from the feature set during training. We must also ensure that no statistics calculated from `isFraud` (like target encoding) are computed on the entire dataset without cross-validation/out-of-fold techniques to avoid target leakage.
- **Highly Missing Columns**: Many columns in both transaction (e.g., `dist2`, `D` columns, `V` columns) and identity (e.g., `id_21`-`id_26`) have missing value rates higher than 80-90%. These require careful handling (e.g., tree-based models like LightGBM/XGBoost that handle NaNs natively, or specific imputation strategies).

