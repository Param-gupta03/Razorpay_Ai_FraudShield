import os
import gc
import sys
import pickle
import json
import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, average_precision_score, roc_auc_score, confusion_matrix, brier_score_loss

import lightgbm as lgb
import xgboost as xgb

def calculate_metrics(y_true, y_pred_prob, threshold=0.5):
    y_pred = (y_pred_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    pr_auc = average_precision_score(y_true, y_pred_prob)
    roc_auc = roc_auc_score(y_true, y_pred_prob)
    brier = brier_score_loss(y_true, y_pred_prob)
    
    fpr = fp / (tn + fp) if (tn + fp) > 0 else 0
    fnr = fn / (tp + fn) if (tp + fn) > 0 else 0
    
    return {
        "Precision": float(precision),
        "Recall": float(recall),
        "F1": float(f1),
        "PR-AUC": float(pr_auc),
        "ROC-AUC": float(roc_auc),
        "Brier": float(brier),
        "TP": int(tp),
        "TN": int(tn),
        "FP": int(fp),
        "FN": int(fn),
        "FPR": float(fpr),
        "FNR": float(fnr)
    }

def main():
    data_dir = r"C:\Users\param\OneDrive\Desktop\razopayjon\data\processed"
    models_dir = r"C:\Users\param\OneDrive\Desktop\razopayjon\models"
    reports_dir = r"C:\Users\param\OneDrive\Desktop\razopayjon\reports"
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    # 1. Load Datasets
    print("Loading datasets from data/processed...")
    train_df = pd.read_pickle(os.path.join(data_dir, "train_features.pkl"))
    val_df = pd.read_pickle(os.path.join(data_dir, "val_features.pkl"))
    
    # Separate X and y
    print("Preparing feature matrices...")
    drop_cols = ['isFraud', 'TransactionID', 'TransactionDT']
    X_train = train_df.drop(columns=drop_cols)
    y_train = train_df['isFraud']
    
    X_val = val_df.drop(columns=drop_cols)
    y_val = val_df['isFraud']
    
    print(f"X_train shape: {X_train.shape}, y_train class ratio: {y_train.mean()*100:.4f}%")
    print(f"X_val shape: {X_val.shape}, y_val class ratio: {y_val.mean()*100:.4f}%")
    
    del train_df, val_df
    gc.collect()
    
    # Model comparison registry
    comparison_results = []
    
    # ==================================================
    # 1. BASELINE MODEL: Logistic Regression
    # ==================================================
    print("\nTraining Baseline Model: Logistic Regression...")
    
    # Preprocessing pipeline
    low_card_cats = [c for c in X_train.columns if X_train[c].dtype.name == 'category' and X_train[c].nunique() < 10]
    numerical_cols = [c for c in X_train.columns if X_train[c].dtype.name != 'category']
    
    print(f"LR Preprocessor: scaling {len(numerical_cols)} numerical cols, one-hot encoding {len(low_card_cats)} low-card categorical cols.")
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numerical_cols),
            ('cat', categorical_transformer, low_card_cats)
        ]
    )
    
    lr_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(max_iter=500, random_state=42, class_weight='balanced', n_jobs=-1))
    ])
    
    # Fit LR
    lr_pipeline.fit(X_train, y_train)
    
    # Predict validation probabilities
    y_val_prob_lr = lr_pipeline.predict_proba(X_val)[:, 1]
    
    # Evaluate LR
    lr_metrics = calculate_metrics(y_val, y_val_prob_lr)
    lr_metrics["Model"] = "Logistic Regression (Baseline)"
    comparison_results.append(lr_metrics)
    print(f"LR PR-AUC: {lr_metrics['PR-AUC']:.4f} | ROC-AUC: {lr_metrics['ROC-AUC']:.4f} | F1: {lr_metrics['F1']:.4f}")
    
    # Save LR model
    with open(os.path.join(models_dir, "baseline_logistic_regression.pkl"), "wb") as f:
        pickle.dump(lr_pipeline, f)
    print("Baseline Logistic Regression model saved.")
    
    # Clean up LR predictions & model (to free up memory)
    del lr_pipeline, y_val_prob_lr
    gc.collect()
    
    # ==================================================
    # 2. PRIMARY MODEL: LightGBM (Standard)
    # ==================================================
    print("\nTraining Standard LightGBM (Tuned)...")
    lgb_std = lgb.LGBMClassifier(
        n_estimators=1000,
        learning_rate=0.03,
        num_leaves=127,
        max_depth=12,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_samples=50,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    callbacks = [lgb.early_stopping(stopping_rounds=50, verbose=False)]
    lgb_std.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=callbacks
    )
    
    y_val_prob_lgb_std = lgb_std.predict_proba(X_val)[:, 1]
    lgb_std_metrics = calculate_metrics(y_val, y_val_prob_lgb_std)
    lgb_std_metrics["Model"] = "LightGBM (Standard)"
    comparison_results.append(lgb_std_metrics)
    print(f"LightGBM Standard PR-AUC: {lgb_std_metrics['PR-AUC']:.4f} | ROC-AUC: {lgb_std_metrics['ROC-AUC']:.4f} | F1: {lgb_std_metrics['F1']:.4f}")
    
    # ==================================================
    # 3. PRIMARY MODEL: LightGBM (Class-Weighted)
    # ==================================================
    print("\nTraining Class-Weighted LightGBM (Tuned)...")
    lgb_weighted = lgb.LGBMClassifier(
        n_estimators=1000,
        learning_rate=0.03,
        num_leaves=127,
        max_depth=12,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_samples=50,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    lgb_weighted.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=callbacks
    )
    
    y_val_prob_lgb_weighted = lgb_weighted.predict_proba(X_val)[:, 1]
    lgb_weighted_metrics = calculate_metrics(y_val, y_val_prob_lgb_weighted)
    lgb_weighted_metrics["Model"] = "LightGBM (Class-Weighted)"
    comparison_results.append(lgb_weighted_metrics)
    print(f"LightGBM Weighted PR-AUC: {lgb_weighted_metrics['PR-AUC']:.4f} | ROC-AUC: {lgb_weighted_metrics['ROC-AUC']:.4f} | F1: {lgb_weighted_metrics['F1']:.4f}")
    
    with open(os.path.join(models_dir, "lightgbm_standard.pkl"), "wb") as f:
        pickle.dump(lgb_std, f)
    with open(os.path.join(models_dir, "lightgbm_weighted.pkl"), "wb") as f:
        pickle.dump(lgb_weighted, f)
        
    del lgb_std, lgb_weighted
    gc.collect()
    
    # ==================================================
    # 4. OPTIONAL MODEL: XGBoost (Standard)
    # ==================================================
    print("\nTraining Standard XGBoost (Tuned with GPU)...")
    xgb_std = xgb.XGBClassifier(
        n_estimators=1000,
        learning_rate=0.03,
        max_depth=8,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        enable_categorical=True,
        eval_metric='logloss',
        early_stopping_rounds=50,
        tree_method="hist",
        device="cuda"
    )
    xgb_std.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    y_val_prob_xgb_std = xgb_std.predict_proba(X_val)[:, 1]
    xgb_std_metrics = calculate_metrics(y_val, y_val_prob_xgb_std)
    xgb_std_metrics["Model"] = "XGBoost (Standard)"
    comparison_results.append(xgb_std_metrics)
    print(f"XGBoost Standard PR-AUC: {xgb_std_metrics['PR-AUC']:.4f} | ROC-AUC: {xgb_std_metrics['ROC-AUC']:.4f} | F1: {xgb_std_metrics['F1']:.4f}")
    
    # ==================================================
    # 5. OPTIONAL MODEL: XGBoost (Class-Weighted)
    # ==================================================
    print("\nTraining Class-Weighted XGBoost (Tuned with GPU)...")
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_weight = neg_count / pos_count
    print(f"Calculated scale_pos_weight for XGBoost: {scale_weight:.4f}")
    
    xgb_weighted = xgb.XGBClassifier(
        n_estimators=1000,
        learning_rate=0.03,
        max_depth=8,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_weight,
        random_state=42,
        n_jobs=-1,
        enable_categorical=True,
        eval_metric='logloss',
        early_stopping_rounds=50,
        tree_method="hist",
        device="cuda"
    )
    xgb_weighted.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    y_val_prob_xgb_weighted = xgb_weighted.predict_proba(X_val)[:, 1]
    xgb_weighted_metrics = calculate_metrics(y_val, y_val_prob_xgb_weighted)
    xgb_weighted_metrics["Model"] = "XGBoost (Class-Weighted)"
    comparison_results.append(xgb_weighted_metrics)
    print(f"XGBoost Weighted PR-AUC: {xgb_weighted_metrics['PR-AUC']:.4f} | ROC-AUC: {xgb_weighted_metrics['ROC-AUC']:.4f} | F1: {xgb_weighted_metrics['F1']:.4f}")
    
    with open(os.path.join(models_dir, "xgboost_standard.pkl"), "wb") as f:
        pickle.dump(xgb_std, f)
    with open(os.path.join(models_dir, "xgboost_weighted.pkl"), "wb") as f:
        pickle.dump(xgb_weighted, f)
        
    del xgb_std, xgb_weighted
    gc.collect()
    
    # ==================================================
    # 6. Save Comparison Table
    # ==================================================
    comparison_df = pd.DataFrame(comparison_results)
    # Reorder columns
    cols_order = [
        "Model", "Precision", "Recall", "F1", "PR-AUC", "ROC-AUC", 
        "Brier", "TP", "TN", "FP", "FN", "FPR", "FNR"
    ]
    comparison_df = comparison_df[cols_order]
    
    comparison_path = os.path.join(reports_dir, "model_comparison.csv")
    comparison_df.to_csv(comparison_path, index=False)
    print(f"\nSaved model comparison table to {comparison_path}")
    print("\nModel Comparison Table:")
    print(comparison_df.to_string(index=False))

if __name__ == "__main__":
    main()
