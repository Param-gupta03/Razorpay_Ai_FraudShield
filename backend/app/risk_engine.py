from app.config import Config

class RiskEngine:
    @staticmethod
    def get_risk_level(probability: float) -> str:
        """
        Classifies transaction risk based on fraud probability:
        - LOW: probability < 0.10
        - MEDIUM: 0.10 <= probability < 0.30
        - HIGH: probability >= 0.30
        """
        if probability < Config.FROZEN_THRESHOLD:
            return "LOW"
        elif probability < 0.30:
            return "MEDIUM"
        else:
            return "HIGH"
            
    @staticmethod
    def get_recommended_action(risk_level: str) -> str:
        """
        Recommends a defense-only action based on the risk level:
        - LOW -> APPROVE
        - MEDIUM -> REVIEW
        - HIGH -> REVIEW
        """
        if risk_level == "LOW":
            return "APPROVE"
        else:
            return "REVIEW"
            
    @staticmethod
    def calculate_decision_cost(probability: float, action: str) -> float:
        """
        Calculates the expected decision cost:
        - If APPROVED (probability < 0.10):
          Expected Cost = P(Fraud) * FALSE_NEGATIVE_COST
          We risk a chargeback.
        - If REVIEWED (probability >= 0.10):
          Expected Cost = P(Legitimate) * FALSE_POSITIVE_COST
          We risk user friction / manual review cost of a legitimate customer.
        """
        if action == "APPROVE":
            return float(probability * Config.FALSE_NEGATIVE_COST)
        else:
            return float((1.0 - probability) * Config.FALSE_POSITIVE_COST)
