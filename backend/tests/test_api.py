import sys
import os
import pytest
import io
import pandas as pd
from fastapi.testclient import TestClient

# Add app folders to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.config import Config

@pytest.fixture(scope="module")
def client():
    """
    Fixtured test client that manages the lifespan context (model & pipeline loading).
    """
    with TestClient(app) as c:
        yield c

def test_health(client):
    """
    Tests /health endpoint for a 200 response and correct metadata structures.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model"] == "LightGBM"
    assert data["threshold"] == Config.FROZEN_THRESHOLD

def test_model_info(client):
    """
    Tests /model-info endpoint for metadata and performance metrics.
    """
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "validation_metrics" in data
    assert "final_untouched_test_metrics" in data
    assert data["frozen_decision_threshold"] == Config.FROZEN_THRESHOLD

def test_predict_valid(client):
    """
    Tests /predict endpoint with a valid payload representing an actual transaction.
    """
    payload = {
        "TransactionDT": 86400,
        "TransactionAmt": 150.00,
        "TransactionID": 2987004,
        "ProductCD": "W",
        "card1": 13926,
        "card2": 523.0,
        "card6": "debit",
        "P_emaildomain": "gmail.com",
        "C1": 1.0,
        "C13": 1.0,
        "DeviceInfo": "Windows",
        "id_31": "chrome 63.0"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "fraud_probability" in data
    assert "risk_level" in data
    assert "recommended_action" in data
    assert "decision_cost" in data
    assert "top_risk_factors" in data
    
    # Assert risk-level mapping bounds
    prob = data["fraud_probability"]
    risk = data["risk_level"]
    action = data["recommended_action"]
    
    if prob < Config.FROZEN_THRESHOLD:
        assert risk == "LOW"
        assert action == "APPROVE"
    elif prob < 0.30:
        assert risk == "MEDIUM"
        assert action == "REVIEW"
    else:
        assert risk == "HIGH"
        assert action == "REVIEW"

def test_predict_missing_required(client):
    """
    Tests Pydantic validation: fails with 422 if required TransactionAmt is missing.
    """
    payload = {
        "TransactionDT": 86400,
        "ProductCD": "W"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_predict_bad_types(client):
    """
    Tests Pydantic validation: fails with 422 if TransactionAmt is an unconvertible string.
    """
    payload = {
        "TransactionDT": 86400,
        "TransactionAmt": "not-a-number",
        "ProductCD": "W"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_batch_prediction(client):
    """
    Tests /predict/batch endpoint with a CSV file upload, asserting correct columns in return.
    """
    csv_data = (
        "TransactionID,TransactionDT,TransactionAmt,ProductCD,card1,card2\n"
        "10001,86500,50.00,W,10001,150.0\n"
        "10002,86600,200.00,W,10002,200.0\n"
    )
    files = {"file": ("test.csv", csv_data, "text/csv")}
    response = client.post("/predict/batch", files=files)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    
    # Read returned CSV
    df = pd.read_csv(io.StringIO(response.text))
    assert "TransactionID" in df.columns
    assert "fraud_probability" in df.columns
    assert "risk_level" in df.columns
    assert "recommended_action" in df.columns
    assert len(df) == 2
    assert df.loc[0, "TransactionID"] == 10001
