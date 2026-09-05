import os
import sys
import io
import json
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Add backend directory to system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import Config
from app.schemas import TransactionInput, PredictionResponse, SHAPFactor
from app.model_service import ModelService
from app.risk_engine import RiskEngine
from app.explanation_service import ExplanationService

# Singleton services
model_service = None
explanation_service = None
risk_engine = RiskEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for loading models and pipeline artifacts.
    """
    global model_service, explanation_service
    try:
        model_service = ModelService()
        explanation_service = ExplanationService(model_service.model)
        print("FastAPI startup: All ML artifacts loaded successfully.")
    except Exception as e:
        print(f"CRITICAL ERROR on startup during artifact loading: {str(e)}")
        # We don't raise here to allow health endpoint to run and report status
    yield
    # Shutdown cleaning
    print("FastAPI shutdown: Cleaning up models.")
    del model_service, explanation_service
    import gc
    gc.collect()

app = FastAPI(
    title="AI Fraud Risk Manager Backend",
    description="Defense-only AI Fraud Risk scoring API featuring real-time SHAP explainability and decision costing.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware to allow origins from the Next.js frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health():
    """
    Returns API health status, loaded model type, version and operating threshold.
    """
    if model_service is None or model_service.model is None:
        return {
            "status": "unhealthy",
            "detail": "ML models/pipeline failed to load. Please inspect logs.",
            "threshold": Config.FROZEN_THRESHOLD
        }
    return {
        "status": "healthy",
        "model": "LightGBM",
        "model_version": "LGBMClassifier v4.7.0",
        "threshold": Config.FROZEN_THRESHOLD
    }

@app.get("/model-info", tags=["Health"])
def model_info():
    """
    Exposes model metadata, performance metrics (distinguishing validation vs test), 
    limitations, and dataset descriptions.
    """
    # Hardcoded fallback metrics if report files are missing
    val_pr_auc, val_recall = 0.5372, 0.6026
    test_pr_auc, test_recall = 0.4505, 0.5754
    
    # Load dynamically if available
    reports_dir = os.path.join(Config.BASE_DIR, "reports")
    test_metrics_path = os.path.join(reports_dir, "test_metrics.json")
    if os.path.exists(test_metrics_path):
        try:
            with open(test_metrics_path, "r", encoding="utf-8") as f:
                tm = json.load(f)
                test_pr_auc = tm["Metrics"]["PR-AUC"]
                test_recall = tm["Metrics"]["Recall"]
        except Exception:
            pass
            
    return {
        "model_type": "LightGBM Classifier (Standard)",
        "model_version": "1.0.0",
        "frozen_decision_threshold": Config.FROZEN_THRESHOLD,
        "dataset_description": "Vesta / IEEE-CIS Fraud Detection dataset merged with Identity metadata (590,540 rows total).",
        "validation_metrics": {
            "description": "Validation split (15% next chronological data) used for threshold tuning and hyperparameter selection.",
            "PR_AUC": val_pr_auc,
            "Recall": val_recall,
            "Precision": 0.4036,
            "F1": 0.4834
        },
        "final_untouched_test_metrics": {
            "description": "Untouched test split (15% latest chronological data) evaluated exactly once to estimate generalization performance.",
            "PR_AUC": test_pr_auc,
            "Recall": test_recall,
            "Precision": 0.2876,
            "F1": 0.3835
        },
        "limitations": [
            "Assumes temporal stationarity. Shifts in fraud patterns will degrade predictions and require re-training.",
            "Device and network identity details are missing for ~75% of raw transactions, forcing reliance on checkout-only parameters."
        ]
    }

@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(transaction: TransactionInput):
    """
    Scores an incoming transaction to predict fraud probability and returns risk classification, 
    defense-only recommended action, expected decision cost, and SHAP explainability.
    """
    if model_service is None or model_service.model is None:
        raise HTTPException(
            status_code=503, 
            detail="Service Unhealthy: Fraud risk models are not initialized."
        )
        
    try:
        # Convert Pydantic request to dictionary (including extra fields)
        input_dict = transaction.model_dump()
        extra_fields = transaction.model_extra or {}
        input_dict.update(extra_fields)
        
        transaction_id = input_dict.get("TransactionID") or 9999999
        
        # 1. Execute prediction and pipeline transformation
        prob, X_row = model_service.predict_single(input_dict)
        
        # 2. Risk level classification
        risk_level = risk_engine.get_risk_level(prob)
        
        # 3. Recommended action (APPROVE / REVIEW)
        action = risk_engine.get_recommended_action(risk_level)
        
        # 4. Expected decision cost
        decision_cost = risk_engine.calculate_decision_cost(prob, action)
        
        # 5. SHAP explainability
        top_risk, top_mitigating = explanation_service.explain_instance(X_row)
        
        # Format response
        response = {
            "transaction_id": int(transaction_id),
            "fraud_probability": round(prob, 4),
            "risk_level": risk_level,
            "recommended_action": action,
            "threshold": Config.FROZEN_THRESHOLD,
            "decision_cost": round(decision_cost, 2),
            "top_risk_factors": [
                SHAPFactor(feature=f["feature"], impact=f["impact"], importance=f["importance"])
                for f in top_risk
            ],
            "top_mitigating_factors": [
                SHAPFactor(feature=f["feature"], impact=f["impact"], importance=f["importance"])
                for f in top_mitigating
            ]
        }
        
        return response
        
    except Exception as e:
        # Hide internal stack trace and return bad request
        raise HTTPException(
            status_code=400, 
            detail=f"Feature pipeline or prediction failed: {str(e)}"
        )

@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(file: UploadFile = File(...)):
    """
    Accepts a CSV file containing transactions, scores them in batch, and returns a CSV download 
    with TransactionID, fraud_probability, risk_level, and recommended_action columns.
    """
    if model_service is None or model_service.model is None:
        raise HTTPException(
            status_code=503, 
            detail="Service Unhealthy: Fraud risk models are not initialized."
        )
        
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only CSV files are supported."
        )
        
    try:
        contents = await file.read()
        df_raw = pd.read_csv(io.BytesIO(contents))
        
        # Run batch predictions
        results_df = model_service.predict_batch(df_raw)
        
        # Map risk and actions
        results_df["risk_level"] = results_df["fraud_probability"].apply(risk_engine.get_risk_level)
        results_df["recommended_action"] = results_df["risk_level"].apply(risk_engine.get_recommended_action)
        
        # Serialize to CSV stream
        stream = io.StringIO()
        results_df.to_csv(stream, index=False)
        
        response = StreamingResponse(
            iter([stream.getvalue()]), 
            media_type="text/csv"
        )
        response.headers["Content-Disposition"] = f"attachment; filename=predictions_{file.filename}"
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Batch prediction processing failed: {str(e)}"
        )
