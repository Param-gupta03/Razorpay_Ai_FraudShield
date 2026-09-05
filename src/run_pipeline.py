import os
import gc
import json
import sys
import pandas as pd
import numpy as np

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_preparation import load_and_merge, temporal_split, verify_and_assert_splits
from features import FeaturePipeline

def main():
    data_dir = r"C:\Users\param\OneDrive\Desktop\razopayjon\data"
    reports_dir = r"C:\Users\param\OneDrive\Desktop\razopayjon\reports"
    processed_dir = os.path.join(data_dir, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    # 1. Load raw data and merge (left join on TransactionID)
    print("Step 1: Loading and merging raw datasets...")
    merged_df = load_and_merge(data_dir)
    print(f"Merged raw DataFrame shape: {merged_df.shape}")
    
    # 2. Temporal Chronological Splitting
    print("\nStep 2: Performing temporal chronological split...")
    train_df, val_df, test_df, p70, p85 = temporal_split(merged_df)
    
    # Verify split boundaries and integrity
    verify_and_assert_splits(train_df, val_df, test_df)
    
    # Clean up merged_df
    del merged_df
    gc.collect()
    
    # 3. Fit and Apply Feature Pipeline
    print("\nStep 3: Fitting and transforming features...")
    pipeline = FeaturePipeline()
    pipeline.fit(train_df)
    
    # Transform splits
    print("Transforming training features...")
    X_train = pipeline.transform(train_df)
    
    print("Transforming validation features...")
    X_val = pipeline.transform(val_df)
    
    print("Transforming test features...")
    X_test = pipeline.transform(test_df)
    
    # Clean up raw split dataframes
    del train_df, val_df, test_df
    gc.collect()
    
    # 4. Target Distributions
    train_rate = X_train['isFraud'].mean() * 100
    val_rate = X_val['isFraud'].mean() * 100
    test_rate = X_test['isFraud'].mean() * 100
    
    print("\nTarget Class Distribution:")
    print(f"Train Shape: {X_train.shape} | Fraud Count: {X_train['isFraud'].sum():,} | Fraud Rate: {train_rate:.4f}%")
    print(f"Val Shape: {X_val.shape}   | Fraud Count: {X_val['isFraud'].sum():,} | Fraud Rate: {val_rate:.4f}%")
    print(f"Test Shape: {X_test.shape}  | Fraud Count: {X_test['isFraud'].sum():,}  | Fraud Rate: {test_rate:.4f}%")
    
    # 5. Assertions/Leakage Checks
    print("\nStep 4: Running explicit data leakage checks...")
    
    # No TransactionID overlap
    train_ids = set(X_train['TransactionID'])
    val_ids = set(X_val['TransactionID'])
    test_ids = set(X_test['TransactionID'])
    
    assert len(train_ids.intersection(val_ids)) == 0, "Leakage Error: TransactionID overlap between Train and Val!"
    assert len(train_ids.intersection(test_ids)) == 0, "Leakage Error: TransactionID overlap between Train and Test!"
    assert len(val_ids.intersection(test_ids)) == 0, "Leakage Error: TransactionID overlap between Val and Test!"
    print("- Passed: Zero TransactionID overlap between splits.")
    
    # Chronological timestamps
    assert X_train['TransactionDT'].max() <= X_val['TransactionDT'].min(), "Leakage Error: Temporal overlap between Train and Val!"
    assert X_val['TransactionDT'].max() <= X_test['TransactionDT'].min(), "Leakage Error: Temporal overlap between Val and Test!"
    print("- Passed: Strict chronological order of timestamps.")
    
    # No target, key or chronological time in feature names
    feature_cols = [c for c in X_train.columns if c not in ['isFraud', 'TransactionID', 'TransactionDT']]
    assert 'isFraud' not in feature_cols, "Leakage Error: isFraud target column is in X features!"
    assert 'TransactionID' not in feature_cols, "Leakage Error: TransactionID key is in X features!"
    assert 'TransactionDT' not in feature_cols, "Leakage Error: TransactionDT key is in X features!"
    print("- Passed: X features exclude target ('isFraud'), key ('TransactionID'), and timestamp ('TransactionDT').")
    
    # 6. Save Processed Feature Datasets
    print("\nStep 5: Saving processed features to disk...")
    X_train.to_pickle(os.path.join(processed_dir, "train_features.pkl"))
    X_val.to_pickle(os.path.join(processed_dir, "val_features.pkl"))
    X_test.to_pickle(os.path.join(processed_dir, "test_features.pkl"))
    print("Features saved successfully as pickle files.")
    
    # 7. Save Feature Metadata
    print("\nStep 6: Generating and saving feature metadata...")
    metadata = {
        "total_features": len(feature_cols),
        "feature_names": feature_cols,
        "categorical_features": [c for c in pipeline.categorical_cols if c in feature_cols],
        "numerical_features": [c for c in feature_cols if c not in pipeline.categorical_cols]
    }
    
    metadata_path = os.path.join(reports_dir, "feature_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
        
    print(f"[SUCCESS] Saved feature metadata for {len(feature_cols)} features to {metadata_path}")
    print(f"- Categorical features: {len(metadata['categorical_features'])}")
    print(f"- Numerical features: {len(metadata['numerical_features'])}")

    # 8. Save Fitted Feature Pipeline
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(models_dir, exist_ok=True)
    pipeline_path = os.path.join(models_dir, "feature_pipeline.pkl")
    print(f"\nStep 7: Saving fitted feature pipeline to {pipeline_path}...")
    import pickle
    with open(pipeline_path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"[SUCCESS] Saved fitted feature pipeline to {pipeline_path}")

if __name__ == "__main__":
    main()
