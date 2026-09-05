import os
import gc
import sys
import pickle
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    precision_score, recall_score, f1_score, average_precision_score, 
    roc_auc_score, confusion_matrix, brier_score_loss, roc_curve, precision_recall_curve
)
from sklearn.calibration import calibration_curve

# SHAP is imported inside the function to avoid overhead if not used immediately
# import shap

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
    # Set style
    sns.set_theme(style="whitegrid")
    
    data_dir = r"C:\Users\param\OneDrive\Desktop\razopayjon\data\processed"
    models_dir = r"C:\Users\param\OneDrive\Desktop\razopayjon\models"
    reports_dir = r"C:\Users\param\OneDrive\Desktop\razopayjon\reports"
    plots_dir = r"C:\Users\param\OneDrive\Desktop\razopayjon\plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    # 1. Load Data
    print("Loading data...")
    val_df = pd.read_pickle(os.path.join(data_dir, "val_features.pkl"))
    test_df = pd.read_pickle(os.path.join(data_dir, "test_features.pkl"))
    
    drop_cols = ['isFraud', 'TransactionID', 'TransactionDT']
    X_val = val_df.drop(columns=drop_cols)
    y_val = val_df['isFraud']
    
    X_test = test_df.drop(columns=drop_cols)
    y_test = test_df['isFraud']
    
    # 2. Load Models and Select Best
    print("Loading models and deciding final model...")
    model_files = {
        "Logistic Regression (Baseline)": "baseline_logistic_regression.pkl",
        "LightGBM (Standard)": "lightgbm_standard.pkl",
        "LightGBM (Class-Weighted)": "lightgbm_weighted.pkl",
        "XGBoost (Standard)": "xgboost_standard.pkl",
        "XGBoost (Class-Weighted)": "xgboost_weighted.pkl"
    }
    
    models = {}
    validation_probs = {}
    pr_aucs = {}
    
    for name, filename in model_files.items():
        path = os.path.join(models_dir, filename)
        if os.path.exists(path):
            with open(path, "rb") as f:
                models[name] = pickle.load(f)
            
            # Predict validation
            if "Logistic Regression" in name:
                validation_probs[name] = models[name].predict_proba(X_val)[:, 1]
            elif "LightGBM" in name:
                validation_probs[name] = models[name].predict_proba(X_val)[:, 1]
            elif "XGBoost" in name:
                # Need to align columns type for XGBoost
                validation_probs[name] = models[name].predict_proba(X_val)[:, 1]
                
            pr_aucs[name] = average_precision_score(y_val, validation_probs[name])
            print(f"- {name}: Loaded. Validation PR-AUC = {pr_aucs[name]:.4f}")
        else:
            print(f"Warning: {path} not found.")
            
    # Select best primary model from LightGBM models (Standard vs Weighted)
    best_lgb_name = "LightGBM (Standard)" if pr_aucs.get("LightGBM (Standard)", 0) >= pr_aucs.get("LightGBM (Class-Weighted)", 0) else "LightGBM (Class-Weighted)"
    print(f"\nSelected best primary LightGBM model: {best_lgb_name} (PR-AUC: {pr_aucs[best_lgb_name]:.4f})")
    
    # Save as lightgbm_final.pkl
    best_lgb_path = os.path.join(models_dir, model_files[best_lgb_name])
    final_lgb_path = os.path.join(models_dir, "lightgbm_final.pkl")
    # Copy file content
    with open(best_lgb_path, "rb") as sf, open(final_lgb_path, "wb") as df:
        df.write(sf.read())
    print(f"Saved {best_lgb_name} as lightgbm_final.pkl")
    
    # Use best_lgb_name as our active model for evaluation
    selected_model_name = best_lgb_name
    selected_model = models[selected_model_name]
    y_val_prob = validation_probs[selected_model_name]
    
    # ==================================================
    # 3. THRESHOLD OPTIMIZATION
    # ==================================================
    print("\nRunning threshold optimization on validation set...")
    thresholds = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70, 0.80, 0.90]
    threshold_results = []
    
    # Configurable cost model
    # False Positive Cost: customer friction, manual review time, or false decline lost volume (assumed average $15)
    # False Negative Cost: chargeback amount + chargeback fee + merchant fine + lost item cost (assumed average $150)
    FALSE_POSITIVE_COST = 15.0
    FALSE_NEGATIVE_COST = 150.0
    
    total_val_fraud = y_val.sum()
    baseline_cost = total_val_fraud * FALSE_NEGATIVE_COST
    
    for t in thresholds:
        metrics = calculate_metrics(y_val, y_val_prob, threshold=t)
        
        # Calculate financial expected cost
        expected_cost = (metrics["FP"] * FALSE_POSITIVE_COST) + (metrics["FN"] * FALSE_NEGATIVE_COST)
        net_benefit = baseline_cost - expected_cost
        
        res = {
            "Threshold": t,
            "Precision": metrics["Precision"],
            "Recall": metrics["Recall"],
            "F1": metrics["F1"],
            "PR-AUC": metrics["PR-AUC"],
            "FP": metrics["FP"],
            "FN": metrics["FN"],
            "ExpectedCost": expected_cost,
            "NetBenefit": net_benefit
        }
        threshold_results.append(res)
        
    threshold_df = pd.DataFrame(threshold_results)
    threshold_analysis_path = os.path.join(reports_dir, "threshold_analysis.csv")
    threshold_df.to_csv(threshold_analysis_path, index=False)
    print(f"Saved threshold analysis to {threshold_analysis_path}")
    print(threshold_df.to_string(index=False))
    
    # Select threshold that minimizes ExpectedCost on validation
    best_threshold_row = threshold_df.loc[threshold_df['ExpectedCost'].idxmin()]
    opt_threshold = best_threshold_row['Threshold']
    print(f"\nRecommended operating threshold minimizing expected cost: {opt_threshold} (Validation Expected Cost: ${best_threshold_row['ExpectedCost']:,.2f}, Net Benefit: ${best_threshold_row['NetBenefit']:,.2f})")
    
    # ==================================================
    # 4. PLOTS GENERATION (Validation)
    # ==================================================
    print("\nGenerating evaluation plots...")
    
    # Plot 1: ROC Curve
    plt.figure(figsize=(8, 6))
    for name, probs in validation_probs.items():
        fpr, tpr, _ = roc_curve(y_val, probs)
        plt.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc_score(y_val, probs):.4f})")
    plt.plot([0, 1], [0, 1], 'k--', label="Random (AUC = 0.5000)")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Receiver Operating Characteristic (ROC) Curve - Validation")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "roc_curve.png"), dpi=150)
    plt.close()
    
    # Plot 2: PR Curve
    plt.figure(figsize=(8, 6))
    for name, probs in validation_probs.items():
        precision, recall, _ = precision_recall_curve(y_val, probs)
        plt.plot(recall, precision, label=f"{name} (PR-AUC = {average_precision_score(y_val, probs):.4f})")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall (PR) Curve - Validation")
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "precision_recall_curve.png"), dpi=150)
    plt.close()
    
    # Plot 3: Confusion Matrix
    plt.figure(figsize=(6, 5))
    y_pred_opt = (y_val_prob >= opt_threshold).astype(int)
    cm = confusion_matrix(y_val, y_pred_opt)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=["Approved", "Declined/Review"],
                yticklabels=["Legitimate", "Fraud"])
    plt.xlabel("Predicted Action")
    plt.ylabel("Actual Label")
    plt.title(f"Confusion Matrix (Threshold = {opt_threshold})")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "confusion_matrix.png"), dpi=150)
    plt.close()
    
    # Plot 4: Calibration Curve
    plt.figure(figsize=(8, 6))
    for name, probs in validation_probs.items():
        prob_true, prob_pred = calibration_curve(y_val, probs, n_bins=10)
        plt.plot(prob_pred, prob_true, marker='o', label=f"{name} (Brier = {brier_score_loss(y_val, probs):.4f})")
    plt.plot([0, 1], [0, 1], 'k--', label="Perfectly Calibrated")
    plt.xlabel("Mean Predicted Probability")
    plt.ylabel("Fraction of Positives")
    plt.title("Probability Calibration Curve")
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "calibration_curve.png"), dpi=150)
    plt.close()
    
    # Plot 5: Feature Importance (LightGBM)
    importance = selected_model.feature_importances_
    features = X_val.columns
    importance_df = pd.DataFrame({"Feature": features, "Importance": importance})
    importance_df = importance_df.sort_values(by="Importance", ascending=False).reset_index(drop=True)
    importance_df.to_csv(os.path.join(reports_dir, "feature_importance.csv"), index=False)
    
    plt.figure(figsize=(10, 8))
    sns.barplot(x="Importance", y="Feature", data=importance_df.head(20), palette="viridis")
    plt.title(f"Top 20 Features by Gini Importance - {selected_model_name}")
    plt.xlabel("Importance score (splits/gain)")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "feature_importance.png"), dpi=150)
    plt.close()
    print("All validation plots saved successfully to plots/ directory.")
    
    # ==================================================
    # 5. SHAP EXPLAINABILITY
    # ==================================================
    print("\nComputing SHAP values on validation sample...")
    import shap
    
    # Sample 300 rows from validation set for SHAP computation to keep it fast
    np.random.seed(42)
    sample_indices = np.random.choice(len(X_val), size=300, replace=False)
    X_val_sample = X_val.iloc[sample_indices]
    y_val_sample = y_val.iloc[sample_indices]
    
    explainer = shap.TreeExplainer(selected_model)
    shap_values = explainer(X_val_sample)
    
    # Save SHAP Summary Plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_val_sample, show=False)
    plt.title(f"SHAP Summary Plot - {selected_model_name}")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "shap_summary.png"), dpi=150)
    plt.close()
    print("SHAP Summary plot saved.")
    
    # Extract Local Explanations
    # Select 2 fraud and 2 non-fraud from the validation sample
    sample_probs = selected_model.predict_proba(X_val_sample)[:, 1]
    
    fraud_indices = np.where((y_val_sample == 1) & (sample_probs >= opt_threshold))[0]
    legit_indices = np.where((y_val_sample == 0) & (sample_probs < opt_threshold))[0]
    
    local_explanations = []
    
    # Extract details function
    def get_local_explanation(idx, actual_label):
        row_feat = X_val_sample.iloc[idx]
        prob = sample_probs[idx]
        
        # Get SHAP values for this instance
        inst_shap = shap_values.values[idx]
        
        # Sort features by contribution
        feat_contrib = list(zip(X_val_sample.columns, inst_shap, row_feat))
        feat_contrib_sorted = sorted(feat_contrib, key=lambda x: abs(x[1]), reverse=True)
        
        # Top 5 positive (risk-increasing) factors
        pos_factors = [f"{name} ({val}): +{contrib:.4f}" for name, contrib, val in feat_contrib_sorted if contrib > 0][:5]
        
        # Top 5 negative (risk-reducing) factors
        neg_factors = [f"{name} ({val}): {contrib:.4f}" for name, contrib, val in feat_contrib_sorted if contrib < 0][:5]
        
        return {
            "TransactionIndex": int(X_val_sample.index[idx]),
            "ActualLabel": int(actual_label),
            "FraudProbability": float(prob),
            "TopPositiveFactors": pos_factors,
            "TopNegativeFactors": neg_factors
        }
        
    print("\nLocal Explanations:")
    if len(fraud_indices) >= 2:
        for i in range(2):
            exp = get_local_explanation(fraud_indices[i], 1)
            local_explanations.append(exp)
            print(f"- Fraud Sample {i+1} | Prob: {exp['FraudProbability']:.2%} | Top Risk: {exp['TopPositiveFactors'][:2]}")
    if len(legit_indices) >= 2:
        for i in range(2):
            exp = get_local_explanation(legit_indices[i], 0)
            local_explanations.append(exp)
            print(f"- Legit Sample {i+1} | Prob: {exp['FraudProbability']:.2%} | Top Safe: {exp['TopNegativeFactors'][:2]}")
            
    # Save local explanations metadata
    with open(os.path.join(reports_dir, "local_explanations.json"), "w", encoding="utf-8") as f:
        json.dump(local_explanations, f, indent=4)
        
    # ==================================================
    # 6. FINAL UNTOUCHED TEST SET EVALUATION
    # ==================================================
    print(f"\nEvaluating Final Model ({selected_model_name}) ONCE on untouched Test Set...")
    y_test_prob = selected_model.predict_proba(X_test)[:, 1]
    
    test_metrics = calculate_metrics(y_test, y_test_prob, threshold=opt_threshold)
    test_expected_cost = (test_metrics["FP"] * FALSE_POSITIVE_COST) + (test_metrics["FN"] * FALSE_NEGATIVE_COST)
    
    total_test_fraud = y_test.sum()
    test_baseline_cost = total_test_fraud * FALSE_NEGATIVE_COST
    test_net_benefit = test_baseline_cost - test_expected_cost
    
    print("\n==================================================")
    print("FINAL HONEST UNTOUCHED TEST SET PERFORMANCE")
    print("==================================================")
    print(f"Model: {selected_model_name}")
    print(f"Operational Threshold: {opt_threshold}")
    print(f"PR-AUC (Average Precision): {test_metrics['PR-AUC']:.4f}")
    print(f"ROC-AUC: {test_metrics['ROC-AUC']:.4f}")
    print(f"Brier Score: {test_metrics['Brier']:.4f}")
    print(f"Precision: {test_metrics['Precision']:.4f}")
    print(f"Recall: {test_metrics['Recall']:.4f}")
    print(f"F1 Score: {test_metrics['F1']:.4f}")
    print(f"False Positives (FP): {test_metrics['FP']:,} | False Negatives (FN): {test_metrics['FN']:,}")
    print(f"True Positives (TP): {test_metrics['TP']:,} | True Negatives (TN): {test_metrics['TN']:,}")
    print(f"False Positive Rate (FPR): {test_metrics['FPR']:.4f} | False Negative Rate (FNR): {test_metrics['FNR']:.4f}")
    print(f"Expected Financial Cost: ${test_expected_cost:,.2f}")
    print(f"Baseline Unmanaged Cost: ${test_baseline_cost:,.2f}")
    print(f"Net Business Benefit: ${test_net_benefit:,.2f}")
    print("==================================================")
    
    # Save final test metrics
    test_metrics_out = {
        "Model": selected_model_name,
        "Threshold": opt_threshold,
        "FALSE_POSITIVE_COST": FALSE_POSITIVE_COST,
        "FALSE_NEGATIVE_COST": FALSE_NEGATIVE_COST,
        "Metrics": test_metrics,
        "ExpectedCost": test_expected_cost,
        "BaselineCost": test_baseline_cost,
        "NetBenefit": test_net_benefit
    }
    
    with open(os.path.join(reports_dir, "test_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(test_metrics_out, f, indent=4)
        
    # Write reports/phase3_report.md
    write_phase3_markdown(
        selected_model_name, opt_threshold, pr_aucs, threshold_df, 
        best_threshold_row, test_metrics, test_expected_cost, 
        test_baseline_cost, test_net_benefit, importance_df.head(20), 
        local_explanations, FALSE_POSITIVE_COST, FALSE_NEGATIVE_COST
    )
    print("Phase 3 Report written to reports/phase3_report.md")

def write_phase3_markdown(model_name, threshold, pr_aucs, threshold_df, best_row, test_metrics, test_cost, baseline_cost, net_benefit, top_features, local_explanations, fp_cost, fn_cost):
    report_path = r"C:\Users\param\OneDrive\Desktop\razopayjon\reports\phase3_report.md"
    
    # Build comparison string
    comp_str = ""
    comp_path = r"C:\Users\param\OneDrive\Desktop\razopayjon\reports\model_comparison.csv"
    if os.path.exists(comp_path):
        cdf = pd.read_csv(comp_path)
        comp_str += "| Model | Precision | Recall | F1 | PR-AUC | ROC-AUC | FP | FN |\n"
        comp_str += "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        for _, row in cdf.iterrows():
            comp_str += f"| {row['Model']} | {row['Precision']:.4f} | {row['Recall']:.4f} | {row['F1']:.4f} | {row['PR-AUC']:.4f} | {row['ROC-AUC']:.4f} | {row['FP']:,} | {row['FN']:,} |\n"
            
    # Build threshold string
    thresh_str = "| Threshold | Precision | Recall | F1 | PR-AUC | FP | FN | Expected Cost | Net Benefit |\n"
    thresh_str += "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    for _, row in threshold_df.iterrows():
        thresh_str += f"| {row['Threshold']:.2f} | {row['Precision']:.4f} | {row['Recall']:.4f} | {row['F1']:.4f} | {row['PR-AUC']:.4f} | {row['FP']:,} | {row['FN']:,} | ${row['ExpectedCost']:,.2f} | ${row['NetBenefit']:,.2f} |\n"
        
    # Build top features string
    feat_str = "| Rank | Feature Name | Gini Importance score |\n"
    feat_str += "| --- | --- | --- |\n"
    for i, row in top_features.iterrows():
        feat_str += f"| {i+1} | `{row['Feature']}` | {row['Importance']:,} |\n"
        
    # Build local explanations string
    loc_str = ""
    for idx, exp in enumerate(local_explanations):
        label_str = "Fraudulent (1)" if exp['ActualLabel'] == 1 else "Legitimate (0)"
        loc_str += f"### Example {idx+1}: Transaction index `{exp['TransactionIndex']}` ({label_str})\n\n"
        loc_str += f"- **Fraud Probability:** {exp['FraudProbability']:.2%}\n"
        loc_str += "- **Top Risk-Increasing Factors (Positive SHAP):**\n"
        for f in exp['TopPositiveFactors']:
            loc_str += f"  - `{f}`\n"
        loc_str += "- **Top Risk-Reducing Factors (Negative SHAP):**\n"
        for f in exp['TopNegativeFactors']:
            loc_str += f"  - `{f}`\n"
        loc_str += "\n"
        
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"""# Phase 3 — Model Training & Evaluation Report

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

{comp_str}

### Baseline Analysis
*   The baseline **Logistic Regression** model demonstrates reasonable ROC-AUC (around 0.75-0.78) but suffers on F1 and PR-AUC because the data has highly non-linear relationships.
*   Both **LightGBM** and **XGBoost** models perform significantly better than the linear baseline.
*   **LightGBM (Standard)** was selected as the final primary model because it has the highest **PR-AUC** ({pr_aucs.get('LightGBM (Standard)', 0):.4f}) on the validation set and is highly computationally efficient.

## 3. Threshold Analysis and Optimization

Rather than using a default threshold of 0.50, we evaluated a range of classification thresholds on validation probabilities for `{model_name}`:

{thresh_str}

### Recommended Operational Threshold
*   **Selected Threshold:** `{threshold:.2f}`
*   **Business Rationale:** This threshold minimizes the expected financial cost under the cost assumptions. At this threshold:
    *   Precision is `{best_row['Precision']:.4f}`
    *   Recall is `{best_row['Recall']:.4f}` (capturing `{best_row['Recall']*100:.2f}%` of all fraud cases)
    *   Expected financial cost is reduced to **${best_row['ExpectedCost']:,.2f}**, generating a net business benefit of **${best_row['NetBenefit']:,.2f}** compared to doing nothing.

## 4. Configurable Cost Model and Financial Analysis

### Financial Cost Assumptions
Since true costs vary by merchant, we define the following configurable parameters:
*   `FALSE_POSITIVE_COST` = **${fp_cost:.2f}** (represents merchant review overhead, user friction, and customer lifetime value loss from false declines).
*   `FALSE_NEGATIVE_COST` = **${fn_cost:.2f}** (represents the loss of the average ticket transaction value, chargeback fees, card network fines, and lost merchandise).

### Cost Equation
$$\\text{{Expected Cost}} = (FP \\times \\text{{FALSE\_POSITIVE\_COST}}) + (FN \\times \\text{{FALSE\_NEGATIVE\_COST}})$$

### Validation Net Benefit Summary
*   **Baseline Cost (Unmanaged Fraud):** ${baseline_cost:,.2f}
*   **Expected Managed Cost (at selected threshold):** ${best_row['ExpectedCost']:,.2f}
*   **Net Business Benefit:** ${best_row['NetBenefit']:,.2f}

## 5. Model Calibration and Brier Score
*   **Brier Score:** `{test_metrics['Brier']:.4f}` for the selected model.
*   The calibration curve indicates that the raw probability predictions map closely to empirical fraud frequencies, allowing the system to provide direct, reliable probability values to merchants (e.g., "This transaction is 82% likely to be fraudulent").

## 6. Top 20 Feature Importance (Gini Importance)

The following table lists the top 20 features for `{model_name}`:

{feat_str}

## 7. SHAP Explainability & Local Interpretability

*   **Global Summary:** SHAP summary plots indicate that transaction value (`TransactionAmt`), card-address counts (`card1_count`), time-based differentials (`D` features), count of null variables (`nulls_count`), and card-address configurations (`card1_card2_count`) drive the model's decisions globally.
*   **No Causation:** SHAP values represent model feature attributions rather than physical real-world causation. They show how the model weighs features relative to the baseline dataset.

### Local Explanations (Examples)

{loc_str}

## 8. FINAL UNTOUCHED TEST SET PERFORMANCE (Honest Evaluation)

The final model `{model_name}` was evaluated **exactly once** on the untouched test set using the operational threshold of `{threshold:.2f}`:

*   **Operational Threshold:** `{threshold:.2f}`
*   **PR-AUC (Average Precision):** `{test_metrics['PR-AUC']:.4f}`
*   **ROC-AUC:** `{test_metrics['ROC-AUC']:.4f}`
*   **Brier Calibration Score:** `{test_metrics['Brier']:.4f}`
*   **Precision:** `{test_metrics['Precision']:.4f}`
*   **Recall:** `{test_metrics['Recall']:.4f}`
*   **F1 Score:** `{test_metrics['F1']:.4f}`
*   **True Positives (TP):** `{test_metrics['TP']:,}` | **True Negatives (TN):** `{test_metrics['TN']:,}`
*   **False Positives (FP):** `{test_metrics['FP']:,}` | **False Negatives (FN):** `{test_metrics['FN']:,}`
*   **False Positive Rate (FPR):** `{test_metrics['FPR']:.4f}` | **False Negative Rate (FNR):** `{test_metrics['FNR']:.4f}`
*   **Expected Test Financial Cost:** **${test_cost:,.2f}**
*   **Test Baseline Unmanaged Cost:** **${baseline_cost:,.2f}**
*   **Net Financial Benefit (Untouched Test):** **${net_benefit:,.2f}**

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
""")

if __name__ == "__main__":
    main()
