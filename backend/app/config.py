import os

class Config:
    # Project paths
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    MODEL_PATH = os.path.join(BASE_DIR, "models", "lightgbm_final.pkl")
    PIPELINE_PATH = os.path.join(BASE_DIR, "models", "feature_pipeline.pkl")
    
    # Frozen operational threshold
    FROZEN_THRESHOLD = 0.05
    
    # Financial cost assumptions (demonstration/simulation assumptions only)
    FALSE_POSITIVE_COST = 15.00  # Cost of false declination or manual review overhead
    FALSE_NEGATIVE_COST = 150.00  # Average fraud ticket loss (chargebacks + network fines)
