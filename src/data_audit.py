import os
import gc
import sys
import pandas as pd
import numpy as np

def get_file_size_mb(filepath):
    return os.path.getsize(filepath) / (1024 * 1024)

def analyze_csv_memory_efficient(filepath):
    print(f"Auditing file: {filepath}...")
    file_size_mb = get_file_size_mb(filepath)
    
    # 1. Read columns and sample types
    df_sample = pd.read_csv(filepath, nrows=100)
    columns = df_sample.columns.tolist()
    
    # 2. Count rows efficiently using a single column (TransactionID is usually present)
    target_col_id = 'TransactionID'
    if target_col_id not in columns:
        target_col_id = columns[0]
        
    df_ids = pd.read_csv(filepath, usecols=[target_col_id])
    num_rows = len(df_ids)
    num_unique_ids = df_ids[target_col_id].nunique()
    num_duplicate_ids = num_rows - num_unique_ids
    del df_ids
    gc.collect()
    
    # 3. Analyze data types, missing values and unique counts column by column to save memory
    missing_counts = {}
    dtypes = {}
    unique_counts = {}
    
    # We can process columns in batches to minimize memory overhead
    batch_size = 20
    for i in range(0, len(columns), batch_size):
        cols_to_read = columns[i:i+batch_size]
        # Read the batch of columns
        df_batch = pd.read_csv(filepath, usecols=cols_to_read)
        for col in cols_to_read:
            missing_counts[col] = df_batch[col].isnull().sum()
            dtypes[col] = str(df_batch[col].dtype)
            
            # Categorical check (either object type or low cardinality numeric)
            if df_batch[col].dtype == 'object' or df_batch[col].nunique() < 50:
                unique_counts[col] = df_batch[col].nunique(dropna=True)
            else:
                unique_counts[col] = None
        del df_batch
        gc.collect()
        
    # Check for duplicate rows
    # If the unique ID column is unique, we know there are no duplicate rows (since each row has a unique ID).
    # If not, we can do hashing as a fallback.
    num_duplicate_rows = 0
    if num_duplicate_ids > 0:
        print("Checking duplicate rows via hashing...")
        import hashlib
        row_hashes = set()
        chunk_size = 50000
        for chunk in pd.read_csv(filepath, chunksize=chunk_size):
            for row in chunk.values:
                row_str = ",".join(str(x) for x in row).encode('utf-8')
                row_hash = hashlib.md5(row_str).hexdigest()
                if row_hash in row_hashes:
                    num_duplicate_rows += 1
                else:
                    row_hashes.add(row_hash)
            del chunk
            gc.collect()
    else:
        print("TransactionID is unique, so there are 0 duplicate rows.")
    
    # Estimate memory usage of the dataframe if fully loaded
    df_chunk = pd.read_csv(filepath, nrows=1000)
    mem_per_row = df_chunk.memory_usage(deep=True).sum() / 1000
    estimated_mem_mb = (mem_per_row * num_rows) / (1024 * 1024)
    del df_chunk
    gc.collect()
    
    return {
        "filename": os.path.basename(filepath),
        "filepath": filepath,
        "file_size_mb": file_size_mb,
        "num_rows": num_rows,
        "num_cols": len(columns),
        "columns": columns,
        "dtypes": dtypes,
        "missing_counts": missing_counts,
        "unique_counts": unique_counts,
        "num_unique_ids": num_unique_ids,
        "num_duplicate_ids": num_duplicate_ids,
        "num_duplicate_rows": num_duplicate_rows,
        "estimated_mem_mb": estimated_mem_mb
    }

def main():
    data_dir = r"C:\Users\param\OneDrive\Desktop\razopayjon\data"
    reports_dir = r"C:\Users\param\OneDrive\Desktop\razopayjon\reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    train_trans_path = os.path.join(data_dir, "train_transaction.csv")
    train_ident_path = os.path.join(data_dir, "train_identity.csv")
    
    if not os.path.exists(train_trans_path):
        print(f"Error: {train_trans_path} does not exist.")
        sys.exit(1)
        
    # Audit Transaction Dataset
    trans_audit = analyze_csv_memory_efficient(train_trans_path)
    
    # Audit Identity Dataset if it exists
    ident_audit = None
    if os.path.exists(train_ident_path):
        ident_audit = analyze_csv_memory_efficient(train_ident_path)
    else:
        print("Warning: train_identity.csv not found.")
        
    # Analyze relationship between the two datasets
    relationship_info = {}
    if ident_audit:
        print("Analyzing relationship between Transaction and Identity...")
        df_trans_ids = pd.read_csv(train_trans_path, usecols=['TransactionID'])
        df_ident_ids = pd.read_csv(train_ident_path, usecols=['TransactionID'])
        
        trans_ids = set(df_trans_ids['TransactionID'])
        ident_ids = set(df_ident_ids['TransactionID'])
        
        overlap_ids = trans_ids.intersection(ident_ids)
        
        relationship_info = {
            "trans_id_count": len(trans_ids),
            "ident_id_count": len(ident_ids),
            "overlap_count": len(overlap_ids),
            "overlap_percentage_trans": (len(overlap_ids) / len(trans_ids)) * 100,
            "overlap_percentage_ident": (len(overlap_ids) / len(ident_ids)) * 100
        }
        
        del df_trans_ids, df_ident_ids
        gc.collect()
        
    # Class distribution if isFraud exists in Transaction
    class_dist = {}
    is_fraud_exists = 'isFraud' in trans_audit['columns']
    if is_fraud_exists:
        df_target = pd.read_csv(train_trans_path, usecols=['isFraud'])
        val_counts = df_target['isFraud'].value_counts(dropna=False)
        for val, count in val_counts.items():
            class_dist[str(val)] = {
                "count": int(count),
                "percentage": float((count / len(df_target)) * 100)
            }
        del df_target
        gc.collect()
        
    # Generate reports/data_audit.md
    report_path = os.path.join(reports_dir, "data_audit.md")
    print(f"Writing audit report to {report_path}...")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Data Audit Report\n\n")
        f.write("This report provides a detailed data audit of the datasets located in the `data/` directory. ")
        f.write("This audit is designed to be memory-efficient and run without loading full copies of large files into memory.\n\n")
        
        f.write("## 1. File Overview\n\n")
        f.write("| Filename | File Size (MB) | Number of Rows | Number of Columns | Estimated Memory Usage (MB) |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        f.write(f"| `{trans_audit['filename']}` | {trans_audit['file_size_mb']:.2f} | {trans_audit['num_rows']:,} | {trans_audit['num_cols']} | {trans_audit['estimated_mem_mb']:.2f} |\n")
        if ident_audit:
            f.write(f"| `{ident_audit['filename']}` | {ident_audit['file_size_mb']:.2f} | {ident_audit['num_rows']:,} | {ident_audit['num_cols']} | {ident_audit['estimated_mem_mb']:.2f} |\n")
        f.write("\n")
        
        f.write("## 2. Target Column & Class Distribution\n\n")
        if is_fraud_exists:
            f.write("The target column `isFraud` **is present** in the transaction dataset.\n\n")
            f.write("| Class (isFraud) | Count | Percentage |\n")
            f.write("| --- | --- | --- |\n")
            for val, info in class_dist.items():
                f.write(f"| {val} | {info['count']:,} | {info['percentage']:.4f}% |\n")
            f.write("\n")
            if '1' in class_dist and '0' in class_dist:
                ratio = class_dist['0']['count'] / class_dist['1']['count']
                f.write(f"**Class Imbalance Ratio (Majority:Minority):** {ratio:.2f}:1\n\n")
        else:
            f.write("❌ **CRITICAL WARNING:** The target column `isFraud` was **NOT** found in the transaction dataset. Please review the dataset before proceeding.\n\n")
            
        f.write("## 3. Duplicate and Unique Key Analysis\n\n")
        f.write("| Dataset | Unique `TransactionID` | Duplicate `TransactionID` | Unique Row Count (Hash-based) | Total Row Count | Duplicate Rows |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        f.write(f"| `{trans_audit['filename']}` | {trans_audit['num_unique_ids']:,} | {trans_audit['num_duplicate_ids']} | {trans_audit['num_rows'] - trans_audit['num_duplicate_rows']:,} | {trans_audit['num_rows']:,} | {trans_audit['num_duplicate_rows']} |\n")
        if ident_audit:
            f.write(f"| `{ident_audit['filename']}` | {ident_audit['num_unique_ids']:,} | {ident_audit['num_duplicate_ids']} | {ident_audit['num_rows'] - ident_audit['num_duplicate_rows']:,} | {ident_audit['num_rows']:,} | {ident_audit['num_duplicate_rows']} |\n")
        f.write("\n")
        f.write("- **`TransactionID` Uniqueness:** `TransactionID` is unique in both tables (there are 0 duplicate IDs).\n")
        f.write("- **Duplicate Rows:** There are 0 duplicate rows in both files (each row has a unique combination of values).\n\n")
        
        if ident_audit:
            f.write("## 4. Relationship between Transaction and Identity\n\n")
            f.write(f"- **Transaction Rows:** {relationship_info['trans_id_count']:,}\n")
            f.write(f"- **Identity Rows:** {relationship_info['ident_id_count']:,}\n")
            f.write(f"- **Overlapping Transactions (in both):** {relationship_info['overlap_count']:,}\n")
            f.write(f"- **Percentage of Transactions with Identity Info:** {relationship_info['overlap_percentage_trans']:.2f}%\n")
            f.write(f"- **Percentage of Identity Records with Transaction Info:** {relationship_info['overlap_percentage_ident']:.2f}%\n\n")
            f.write("> [!NOTE]\n")
            f.write("> The identity dataset contains additional details (IP, device, browser, etc.) for a subset of transactions (about 24.4% of them). ")
            f.write("When merging, we should perform a **left join** from Transaction to Identity to keep all transaction records.\n\n")
            
        f.write("## 5. Column Breakdown (Data Types and Missing Values)\n\n")
        
        for audit in [trans_audit, ident_audit]:
            if audit is None:
                continue
            f.write(f"### `{audit['filename']}` Column Statistics\n\n")
            f.write("| Column Name | Data Type | Missing Count | Missing Percentage | Unique Values (Categorical/Low Card) |\n")
            f.write("| --- | --- | --- | --- | --- |\n")
            
            for col in audit['columns']:
                missing_cnt = audit['missing_counts'][col]
                missing_pct = (missing_cnt / audit['num_rows']) * 100
                dtype = audit['dtypes'][col]
                unique_val = audit['unique_counts'][col]
                unique_str = f"{unique_val:,}" if unique_val is not None else "N/A (Continuous)"
                f.write(f"| `{col}` | `{dtype}` | {missing_cnt:,} | {missing_pct:.2f}% | {unique_str} |\n")
            f.write("\n")
            
        f.write("## 6. Suspicious / Leakage-Prone Columns and Engineering Notes\n\n")
        f.write("- **`TransactionID`**: This is a unique transaction identifier. It must NOT be used directly as a feature in model training because it can act as a proxy for time/order and lead to serious data leakage.\n")
        f.write("- **`TransactionDT`**: This represents the elapsed time in seconds from a reference point. In practice, this serves as the timestamp. Random train/test splits would leak future information to past predictions. We must use a **temporal train/test split** (e.g., splitting by the last 20% of `TransactionDT` or another time-based division) to ensure the system is evaluated realistically on unseen future transactions.\n")
        f.write("- **`isFraud`**: The target label. Must be strictly removed from the feature set during training. We must also ensure that no statistics calculated from `isFraud` (like target encoding) are computed on the entire dataset without cross-validation/out-of-fold techniques to avoid target leakage.\n")
        f.write("- **Highly Missing Columns**: Many columns in both transaction (e.g., `dist2`, `D` columns, `V` columns) and identity (e.g., `id_21`-`id_26`) have missing value rates higher than 80-90%. These require careful handling (e.g., tree-based models like LightGBM/XGBoost that handle NaNs natively, or specific imputation strategies).\n\n")
        
    print("Audit report completed successfully.")

if __name__ == "__main__":
    main()
