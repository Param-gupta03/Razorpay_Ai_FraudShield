from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any

class TransactionInput(BaseModel):
    TransactionDT: int = Field(..., description="Seconds since reference point (elapsed time)")
    TransactionAmt: float = Field(..., description="Transaction amount in USD")
    TransactionID: Optional[int] = Field(None, description="Unique transaction ID. Generated if not supplied.")
    ProductCD: Optional[str] = Field("W", description="Product code (e.g. W, H, C, S, R)")
    card1: Optional[int] = Field(None, description="Card category ID")
    card2: Optional[float] = Field(None, description="Card issuer ID")
    card3: Optional[float] = Field(None, description="Card Type / Country ID")
    card4: Optional[str] = Field(None, description="Card brand (e.g. visa, mastercard)")
    card5: Optional[float] = Field(None, description="Card Category Code")
    card6: Optional[str] = Field(None, description="Card type (e.g. debit, credit)")
    addr1: Optional[float] = Field(None, description="Billing zip/region")
    addr2: Optional[float] = Field(None, description="Billing country")
    P_emaildomain: Optional[str] = Field(None, description="Purchaser Email Domain")
    R_emaildomain: Optional[str] = Field(None, description="Recipient Email Domain")

    # Allow arbitrary extra fields dynamically (C, D, V, id columns, DeviceInfo, DeviceType, etc.)
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
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
        }
    )

class SHAPFactor(BaseModel):
    feature: str
    impact: str = Field(..., description="Impact direction: 'increases_risk' or 'reduces_risk'")
    importance: float = Field(..., description="Attribution value (SHAP value magnitude)")

class PredictionResponse(BaseModel):
    transaction_id: int
    fraud_probability: float
    risk_level: str = Field(..., description="LOW, MEDIUM, or HIGH")
    recommended_action: str = Field(..., description="APPROVE or REVIEW")
    threshold: float
    decision_cost: float = Field(..., description="Estimated decision cost in USD based on prediction outcome")
    top_risk_factors: List[SHAPFactor]
    top_mitigating_factors: List[SHAPFactor]
