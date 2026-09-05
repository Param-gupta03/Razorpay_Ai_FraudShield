import os
import gc
import pickle
import json
import pandas as pd
import numpy as np
import sys
from typing import Dict, Any, Tuple

# Add src to system path so pickle can resolve features.FeaturePipeline
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from app.config import Config

class ModelService:
    def __init__(self):
        self.model = None
        self.pipeline = None
        self.feature_names = []
        self.raw_columns = []
        self.load_artifacts()
        
    def load_artifacts(self):
        """
        Loads the final LightGBM model, fitted feature pipeline, and feature metadata.
        Also reads raw CSV headers to know the complete list of raw fields.
        """
        print("Loading ModelService artifacts...")
        
        # 1. Load Model
        if not os.path.exists(Config.MODEL_PATH):
            raise FileNotFoundError(f"Production model not found at: {Config.MODEL_PATH}")
        with open(Config.MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)
        print("- LightGBM model loaded.")
        
        # 2. Load Pipeline
        if not os.path.exists(Config.PIPELINE_PATH):
            raise FileNotFoundError(f"Feature pipeline not found at: {Config.PIPELINE_PATH}")
        with open(Config.PIPELINE_PATH, "rb") as f:
            self.pipeline = pickle.load(f)
        print("- Feature pipeline loaded.")
        
        # 3. Load Feature Names Metadata
        metadata_path = os.path.join(Config.BASE_DIR, "reports", "feature_metadata.json")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Feature metadata not found at: {metadata_path}")
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            self.feature_names = metadata["feature_names"]
        print(f"- Feature metadata loaded ({len(self.feature_names)} features).")
        
        # 4. Infer Raw Columns List
        # To make sure our input df has all raw columns expected by the pipeline, 
        # we check reports/raw_columns.json first, or read CSV headers if available
        raw_columns_path = os.path.join(Config.BASE_DIR, "reports", "raw_columns.json")
        if os.path.exists(raw_columns_path):
            with open(raw_columns_path, "r", encoding="utf-8") as f:
                self.raw_columns = json.load(f)
        else:
            trans_raw_path = os.path.join(Config.BASE_DIR, "data", "train_transaction.csv")
            ident_raw_path = os.path.join(Config.BASE_DIR, "data", "train_identity.csv")
            
            if not os.path.exists(trans_raw_path):
                raise FileNotFoundError(f"Neither {raw_columns_path} nor {trans_raw_path} found.")
                
            trans_header = pd.read_csv(trans_raw_path, nrows=0)
            raw_cols = set(trans_header.columns)
            
            if os.path.exists(ident_raw_path):
                ident_header = pd.read_csv(ident_raw_path, nrows=0)
                raw_cols = raw_cols.union(set(ident_header.columns))
                
            self.raw_columns = list(raw_cols)
        print(f"- Raw column template mapped ({len(self.raw_columns)} columns).")
        
    def predict_single(self, transaction_input: Dict[str, Any]) -> Tuple[float, pd.Series]:
        """
        Processes a single transaction input, transforms it, and predicts fraud probability.
        """
        # Create a dictionary initialized to NaN for all raw columns
        full_raw_dict = {col: np.nan for col in self.raw_columns}
        
        # Overwrite with the client's input values (skip None to keep np.nan float dtypes)
        for key, value in transaction_input.items():
            if key in full_raw_dict:
                if value is not None:
                    full_raw_dict[key] = value
                
        # Handle TransactionID if not provided
        if full_raw_dict.get('TransactionID') is None or pd.isna(full_raw_dict['TransactionID']):
            full_raw_dict['TransactionID'] = 9999999  # Dummy ID for pipeline
            
        # Create DataFrame (1 row)
        df_raw = pd.DataFrame([full_raw_dict])
        
        # Run exact same pipeline transformations
        df_transformed = self.pipeline.transform(df_raw)
        
        # Extract features aligned exactly to training columns
        X = df_transformed[self.feature_names]
        
        # Predict probability
        prob = float(self.model.predict_proba(X)[0, 1])
        
        # Return probability and the transformed row (as a DataFrame) for SHAP
        return prob, X.iloc[[0]]
        
    def predict_batch(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Processes a batch of raw transactions (DataFrame) and returns predictions.
        """
        # Align columns of df_raw to have all raw columns needed
        # Any missing column will be initialized to NaN without fragmentation
        missing_cols = [col for col in self.raw_columns if col not in df_raw.columns]
        if missing_cols:
            missing_df = pd.DataFrame(np.nan, index=df_raw.index, columns=missing_cols)
            aligned_df = pd.concat([df_raw, missing_df], axis=1)
        else:
            aligned_df = df_raw.copy()
                
        # Drop isFraud if present in upload
        if 'isFraud' in aligned_df.columns:
            aligned_df = aligned_df.drop(columns=['isFraud'])
            
        # Run transformations
        df_transformed = self.pipeline.transform(aligned_df)
        
        # Extract features aligned exactly to training
        X = df_transformed[self.feature_names]
        
        # Predict probabilities
        probs = self.model.predict_proba(X)[:, 1]
        
        # Create return dataframe
        results = pd.DataFrame({
            "TransactionID": df_raw["TransactionID"] if "TransactionID" in df_raw.columns else np.arange(len(df_raw)),
            "fraud_probability": probs
        })
        
        return results
