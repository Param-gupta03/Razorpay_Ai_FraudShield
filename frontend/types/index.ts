export interface TransactionInput {
  TransactionDT: number;
  TransactionAmt: number;
  TransactionID?: number;
  ProductCD?: string;
  card1?: number;
  card2?: number;
  card3?: number;
  card4?: string;
  card5?: number;
  card6?: string;
  addr1?: number;
  addr2?: number;
  P_emaildomain?: string;
  R_emaildomain?: string;
  [key: string]: any; // Allow dynamic extra fields
}

export interface SHAPFactor {
  feature: string;
  impact: 'increases_risk' | 'reduces_risk';
  importance: number;
  details?: string;
}

export interface PredictionResponse {
  transaction_id: number;
  fraud_probability: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  recommended_action: 'APPROVE' | 'REVIEW';
  threshold: number;
  decision_cost: number;
  top_risk_factors: SHAPFactor[];
  top_mitigating_factors: SHAPFactor[];
}

export interface SplitMetrics {
  description: string;
  PR_AUC: number;
  Recall: number;
  Precision: number;
  F1: number;
}

export interface ModelInfoResponse {
  model_type: string;
  model_version: string;
  frozen_decision_threshold: number;
  dataset_description: string;
  validation_metrics: SplitMetrics;
  final_untouched_test_metrics: SplitMetrics;
  limitations: string[];
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  model: string;
  model_version: string;
  threshold: number;
  detail?: string;
}

export interface ScoredTransactionRecord {
  TransactionID: number;
  TransactionDT: number;
  TransactionAmt: number;
  ProductCD: string;
  card1?: number;
  card2?: number;
  card6?: string;
  P_emaildomain?: string;
  fraud_probability: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  recommended_action: 'APPROVE' | 'REVIEW';
  isDemo?: boolean;
}
