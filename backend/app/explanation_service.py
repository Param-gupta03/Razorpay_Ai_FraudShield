import os
import sys
import pandas as pd
import numpy as np
import shap
from typing import List, Dict, Any, Tuple

# Add src/ backend to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

class ExplanationService:
    def __init__(self, model):
        """
        Initializes the SHAP TreeExplainer on the given tree-based model.
        """
        print("Initializing SHAP TreeExplainer for predictions explainability...")
        self.explainer = shap.TreeExplainer(model)
        
    def explain_instance(self, X_row: pd.DataFrame) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Calculates local SHAP values for a single transaction row and extracts 
        the top 3 risk-increasing and top 3 risk-reducing features.
        """
        # X_row is already a 1-row DataFrame, preserving dtypes
        shap_values = self.explainer(X_row)
        
        features = X_row.columns.tolist()
        vals = shap_values.values[0]
        row_vals = X_row.iloc[0].values
        
        # Collect non-zero feature contributions
        factors = []
        for feat, val, raw_val in zip(features, vals, row_vals):
            # Ignore micro-impacts to keep explanation output clean
            if abs(val) > 0.005:
                factors.append({
                    "feature": feat,
                    "shap_val": val,
                    "raw_val": raw_val
                })
                
        # Separate positive (risk-increasing) and negative (risk-reducing) impacts
        pos_factors = sorted([f for f in factors if f["shap_val"] > 0], key=lambda x: x["shap_val"], reverse=True)
        neg_factors = sorted([f for f in factors if f["shap_val"] < 0], key=lambda x: abs(x["shap_val"]), reverse=True)
        
        # Format risk-increasing factors (top 3)
        top_risk = []
        for f in pos_factors[:3]:
            raw_str = f"'{f['raw_val']}'" if isinstance(f['raw_val'], str) else f"{f['raw_val']:.2f}" if isinstance(f['raw_val'], float) else str(f['raw_val'])
            top_risk.append({
                "feature": f["feature"],
                "impact": "increases_risk",
                "importance": float(abs(f["shap_val"])),
                "details": f"Feature {f['feature']} value ({raw_str}) contributed to a higher predicted fraud risk"
            })
            
        # Format risk-reducing factors (top 3)
        top_mitigating = []
        for f in neg_factors[:3]:
            raw_str = f"'{f['raw_val']}'" if isinstance(f['raw_val'], str) else f"{f['raw_val']:.2f}" if isinstance(f['raw_val'], float) else str(f['raw_val'])
            top_mitigating.append({
                "feature": f["feature"],
                "impact": "reduces_risk",
                "importance": float(abs(f["shap_val"])),
                "details": f"Feature {f['feature']} value ({raw_str}) contributed to a lower predicted fraud risk"
            })
            
        return top_risk, top_mitigating
