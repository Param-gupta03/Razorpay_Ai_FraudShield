'use client';

import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertCircle,
  Loader2,
  RotateCcw,
  Sparkles,
  ArrowRight,
  Code2,
  TrendingUp,
  TrendingDown,
} from 'lucide-react';
import { DemoTransaction } from '../lib/demoData';
import { predictTransaction } from '../lib/api';
import { PredictionResponse, TransactionInput } from '../types';

interface AnalyzerTabProps {
  preselectedTx: DemoTransaction | null;
  clearPreselectedTx: () => void;
  apiHealthy: boolean | null;
}

const FEATURE_LABELS: Record<string, string> = {
  TransactionAmt: 'Order Amount',
  ProductCD: 'Channel Code',
  card1: 'Card BIN / Issuer ID',
  card2: 'Card Sub-bank Code',
  card6: 'Card Funding Type',
  P_emaildomain: 'Buyer Email Provider',
  addr1_count: 'Billing Zip Velocity',
  card2_count: 'Card Issuer Velocity',
  DeviceInfo: 'Device Type',
  id_31: 'Browser Version',
  id_33: 'Screen Resolution',
  C1: 'Card Association Count',
  C13: 'Payment Attempt Count',
  C14: 'Velocity Counter C14',
  D1: 'Card Age / Days Since First Seen',
  V54: 'Identity Match Flag V54',
  V314: 'Cumulative Spend Profile',
};

export default function AnalyzerTab({
  preselectedTx,
  clearPreselectedTx,
  apiHealthy,
}: AnalyzerTabProps) {
  const [txId, setTxId] = useState<string>('2987004');
  const [txDT, setTxDT] = useState<string>('86400');
  const [txAmt, setTxAmt] = useState<string>('150.00');
  const [productCD, setProductCD] = useState<string>('W');
  const [card1, setCard1] = useState<string>('13926');
  const [card2, setCard2] = useState<string>('523.0');
  const [card6, setCard6] = useState<string>('debit');
  const [emailDomain, setEmailDomain] = useState<string>('gmail.com');
  const [customFields, setCustomFields] = useState<string>(
    JSON.stringify(
      {
        C1: 1.0,
        C13: 1.0,
        DeviceInfo: 'Windows',
        id_31: 'chrome 63.0',
      },
      null,
      2
    )
  );

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!preselectedTx) return;

    setTxId(preselectedTx.TransactionID.toString());
    setTxDT(preselectedTx.TransactionDT.toString());
    setTxAmt(preselectedTx.TransactionAmt.toString());
    setProductCD(preselectedTx.ProductCD);
    setCard1(preselectedTx.card1?.toString() || '');
    setCard2(preselectedTx.card2?.toString() || '');
    setCard6(preselectedTx.card6 || 'debit');
    setEmailDomain(preselectedTx.P_emaildomain || '');

    const reserved = [
      'TransactionID',
      'TransactionDT',
      'TransactionAmt',
      'ProductCD',
      'card1',
      'card2',
      'card6',
      'P_emaildomain',
      'expectedProb',
      'expectedRisk',
      'expectedAction',
      'actualLabel',
    ];
    const extra: Record<string, any> = {};
    Object.keys(preselectedTx).forEach((k) => {
      if (!reserved.includes(k)) {
        extra[k] = preselectedTx[k];
      }
    });

    setCustomFields(JSON.stringify(extra, null, 2));
    setPrediction(null);
    setError(null);

    if (apiHealthy === true) {
      runAnalysis(preselectedTx);
    }
    clearPreselectedTx();
  }, [preselectedTx]);

  const runAnalysis = async (directPayload?: TransactionInput) => {
    setIsLoading(true);
    setError(null);

    let payload: TransactionInput;

    if (directPayload) {
      payload = directPayload;
    } else {
      const amtVal = parseFloat(txAmt);
      const dtVal = parseInt(txDT, 10);
      if (isNaN(amtVal) || isNaN(dtVal)) {
        setError('Please enter valid numeric values for Amount and Elapsed Time.');
        setIsLoading(false);
        return;
      }

      payload = {
        TransactionDT: dtVal,
        TransactionAmt: amtVal,
        TransactionID: txId ? parseInt(txId, 10) : undefined,
        ProductCD: productCD,
        card1: card1 ? parseInt(card1, 10) : undefined,
        card2: card2 ? parseFloat(card2) : undefined,
        card6: card6 || undefined,
        P_emaildomain: emailDomain || undefined,
      };

      if (customFields.trim()) {
        try {
          const parsed = JSON.parse(customFields);
          payload = { ...payload, ...parsed };
        } catch {
          setError('Invalid custom fields JSON. Please check formatting.');
          setIsLoading(false);
          return;
        }
      }
    }

    try {
      const res = await predictTransaction(payload);
      setPrediction(res);
    } catch (err: any) {
      setError(err.message || 'Scoring engine failed. Ensure backend server is reachable.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadPreset = (type: 'legit' | 'high_risk' | 'micropay') => {
    setError(null);
    setPrediction(null);

    if (type === 'legit') {
      setTxId('437512');
      setTxDT('120450');
      setTxAmt('34.00');
      setProductCD('W');
      setCard1('9500');
      setCard2('321.0');
      setCard6('debit');
      setEmailDomain('gmail.com');
      setCustomFields('{\n  "C1": 1.0,\n  "C13": 2.0,\n  "addr1_count": 450,\n  "DeviceInfo": "iOS"\n}');
    } else if (type === 'high_risk') {
      setTxId('443491');
      setTxDT('145020');
      setTxAmt('150.00');
      setProductCD('W');
      setCard1('13926');
      setCard2('523.0');
      setCard6('credit');
      setEmailDomain('anonymous.com');
      setCustomFields('{\n  "C1": 14.0,\n  "C13": 28.0,\n  "C14": 9.0,\n  "addr1_count": 12,\n  "DeviceInfo": "Windows"\n}');
    } else {
      setTxId('441478');
      setTxDT('98000');
      setTxAmt('13.28');
      setProductCD('C');
      setCard1('4461');
      setCard2('375.0');
      setCard6('credit');
      setEmailDomain('hotmail.com');
      setCustomFields('{\n  "C1": 8.0,\n  "C13": 11.0,\n  "D1": 0.0,\n  "DeviceInfo": "Android"\n}');
    }
  };

  const handleReset = () => {
    setTxId('2987004');
    setTxDT('86400');
    setTxAmt('150.00');
    setProductCD('W');
    setCard1('13926');
    setCard2('523.0');
    setCard6('debit');
    setEmailDomain('gmail.com');
    setCustomFields('{\n  "C1": 1.0,\n  "C13": 1.0,\n  "DeviceInfo": "Windows",\n  "id_31": "chrome 63.0"\n}');
    setPrediction(null);
    setError(null);
  };

  return (
    <div className="flex flex-col gap-5">
      {/* Quick Presets Bar */}
      <div className="bg-white p-3 sm:p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 text-slate-600">
          <Sparkles className="w-4 h-4 text-blue-600" />
          <span className="font-semibold text-slate-800">Quick Test Scenarios:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => loadPreset('legit')}
            className="px-3 py-1 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs font-medium cursor-pointer transition"
          >
            Normal Checkout ($34 Debit)
          </button>
          <button
            onClick={() => loadPreset('high_risk')}
            className="px-3 py-1 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-medium cursor-pointer transition"
          >
            High Velocity ($150 Credit)
          </button>
          <button
            onClick={() => loadPreset('micropay')}
            className="px-3 py-1 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200 text-xs font-medium cursor-pointer transition"
          >
            Micro-charge Testing ($13.28)
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left 5 cols: Transaction Input Form */}
        <div className="lg:col-span-5 bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between gap-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Transaction Parameters</h3>
                <p className="text-xs text-slate-500">Inputs evaluated by LightGBM model pipeline</p>
              </div>
              <button
                onClick={handleReset}
                className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1 cursor-pointer transition"
                title="Reset fields to defaults"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Reset</span>
              </button>
            </div>

            {/* Parameter Fields */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="space-y-1">
                <label className="text-slate-600 font-medium text-[11px]">Transaction ID</label>
                <input
                  type="text"
                  value={txId}
                  onChange={(e) => setTxId(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-800 font-mono text-xs focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-600 font-medium text-[11px]">Elapsed Sec (DT)</label>
                <input
                  type="text"
                  value={txDT}
                  onChange={(e) => setTxDT(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-800 font-mono text-xs focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-600 font-medium text-[11px]">Amount ($ USD)</label>
                <input
                  type="text"
                  value={txAmt}
                  onChange={(e) => setTxAmt(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-800 font-mono text-xs focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-600 font-medium text-[11px]">Channel (ProductCD)</label>
                <select
                  value={productCD}
                  onChange={(e) => setProductCD(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2 py-1.5 text-slate-800 text-xs focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none cursor-pointer"
                >
                  <option value="W">Web Checkout (W)</option>
                  <option value="H">Host Integration (H)</option>
                  <option value="C">Checkout Gateway (C)</option>
                  <option value="S">Store POS (S)</option>
                  <option value="R">Refunds (R)</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-slate-600 font-medium text-[11px]">Card BIN (card1)</label>
                <input
                  type="text"
                  value={card1}
                  onChange={(e) => setCard1(e.target.value)}
                  placeholder="e.g. 13926"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-800 font-mono text-xs focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-600 font-medium text-[11px]">Bank Issuer (card2)</label>
                <input
                  type="text"
                  value={card2}
                  onChange={(e) => setCard2(e.target.value)}
                  placeholder="e.g. 523.0"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-800 font-mono text-xs focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-600 font-medium text-[11px]">Funding (card6)</label>
                <select
                  value={card6}
                  onChange={(e) => setCard6(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2 py-1.5 text-slate-800 text-xs focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none cursor-pointer"
                >
                  <option value="debit">debit</option>
                  <option value="credit">credit</option>
                  <option value="charge card">charge card</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-slate-600 font-medium text-[11px]">Email Provider</label>
                <input
                  type="text"
                  value={emailDomain}
                  onChange={(e) => setEmailDomain(e.target.value)}
                  placeholder="gmail.com"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-800 text-xs focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                />
              </div>
            </div>

            {/* Custom JSON parameters */}
            <div className="space-y-1 text-xs">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-slate-600">
                  <Code2 className="w-3.5 h-3.5 text-slate-500" />
                  <label className="font-medium text-[11px]">Additional Vesta Features (JSON)</label>
                </div>
                <span className="text-[10px] text-slate-400">C/D/V columns, Device</span>
              </div>
              <textarea
                value={customFields}
                onChange={(e) => setCustomFields(e.target.value)}
                rows={4}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-800 font-mono text-[11px] focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none"
              />
            </div>
          </div>

          <button
            onClick={() => runAnalysis()}
            disabled={isLoading || apiHealthy === false}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs py-2.5 rounded-lg transition shadow-sm flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Running Pipeline & SHAP...</span>
              </>
            ) : (
              <>
                <span>Evaluate Transaction</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>

        {/* Right 7 cols: Prediction Results & Explanations */}
        <div className="lg:col-span-7 flex flex-col gap-5">
          {/* Empty / Idle State */}
          {!isLoading && !prediction && !error && (
            <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center text-center h-full min-h-[420px]">
              <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center mb-3">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-bold text-slate-900">Analyzer Ready</h3>
              <p className="text-xs text-slate-500 mt-1 max-w-sm">
                Pick a preset scenario above or click <strong>Evaluate Transaction</strong> to execute feature engineering, LightGBM classification, and SHAP attribution.
              </p>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center text-center h-full min-h-[420px]">
              <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
              <h3 className="text-sm font-bold text-slate-900">Executing Model Pipeline</h3>
              <p className="text-xs text-slate-500 mt-1">
                Transforming categorical frequencies and calculating TreeExplainer SHAP values...
              </p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-start gap-3 text-rose-800 text-xs shadow-sm">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <strong className="font-semibold text-rose-900">Inference Error:</strong>
                <p className="mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {/* Prediction Result Display */}
          {prediction && (
            <div className="flex flex-col gap-5 animate-fadeIn">
              {/* Score Dial and Action Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Score Dial */}
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between gap-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Fraud Probability
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded-full text-[11px] font-semibold border ${
                        prediction.risk_level === 'LOW'
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                          : prediction.risk_level === 'MEDIUM'
                          ? 'bg-amber-50 text-amber-700 border-amber-200'
                          : 'bg-rose-50 text-rose-700 border-rose-200'
                      }`}
                    >
                      {prediction.risk_level} RISK
                    </span>
                  </div>

                  <div>
                    <div className="text-3xl font-bold font-mono text-slate-900">
                      {(prediction.fraud_probability * 100).toFixed(1)}%
                    </div>

                    <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden mt-3 border border-slate-200">
                      <div
                        className={`h-full transition-all duration-500 ${
                          prediction.risk_level === 'LOW'
                            ? 'bg-emerald-500'
                            : prediction.risk_level === 'MEDIUM'
                            ? 'bg-amber-500'
                            : 'bg-rose-500'
                        }`}
                        style={{ width: `${Math.min(prediction.fraud_probability * 100, 100)}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-[10px] text-slate-400 font-mono mt-1">
                      <span>0%</span>
                      <span className="text-slate-600 font-medium">Cutoff: {(prediction.threshold * 100).toFixed(0)}%</span>
                      <span>100%</span>
                    </div>
                  </div>

                  <div className="text-[11px] text-slate-500 pt-2 border-t border-slate-100">
                    Calculated via LightGBM 456-feature model
                  </div>
                </div>

                {/* Recommended Action */}
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between gap-3">
                  <div>
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Decision Recommendation
                    </span>
                    <div className="flex items-center gap-3 mt-3">
                      {prediction.recommended_action === 'APPROVE' ? (
                        <div className="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-600 flex items-center justify-center shrink-0">
                          <ShieldCheck className="w-5 h-5" />
                        </div>
                      ) : (
                        <div className="w-10 h-10 rounded-lg bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center shrink-0">
                          <ShieldAlert className="w-5 h-5" />
                        </div>
                      )}
                      <div>
                        <div
                          className={`text-base font-bold ${
                            prediction.recommended_action === 'APPROVE' ? 'text-emerald-700' : 'text-amber-700'
                          }`}
                        >
                          {prediction.recommended_action === 'APPROVE' ? 'APPROVE ORDER' : 'FLAG FOR REVIEW'}
                        </div>
                        <span className="text-xs text-slate-500 block">
                          {prediction.recommended_action === 'APPROVE'
                            ? 'Score is below 0.05 cutoff; safe to approve.'
                            : 'Score exceeds 0.05 cutoff; flag for analyst.'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                    <span>Expected Decision Loss:</span>
                    <span className="font-mono font-bold text-slate-900">
                      ${prediction.decision_cost.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>

              {/* SHAP Explanations */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col gap-4">
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Local Drivers (SHAP Attributions)</h3>
                  <p className="text-xs text-slate-500">
                    Signals that shifted this specific transaction's score away from the dataset baseline.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Risk-increasing */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-rose-700">
                      <TrendingUp className="w-4 h-4" />
                      <span>Risk-Increasing Factors (+SHAP)</span>
                    </div>

                    <div className="space-y-2">
                      {prediction.top_risk_factors.length === 0 ? (
                        <div className="text-xs text-slate-400 italic p-3 bg-slate-50 rounded-lg border border-slate-200">
                          No significant risk drivers identified.
                        </div>
                      ) : (
                        prediction.top_risk_factors.map((f, idx) => (
                          <div
                            key={idx}
                            className="bg-rose-50/40 border border-rose-100 p-2.5 rounded-lg flex items-center justify-between text-xs"
                          >
                            <div>
                              <span className="font-semibold text-slate-900 block">
                                {FEATURE_LABELS[f.feature] || f.feature}
                              </span>
                              <span className="text-[10px] text-slate-500 font-mono">{f.feature}</span>
                            </div>
                            <span className="font-mono font-bold text-rose-600">
                              +{f.importance.toFixed(3)}
                            </span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {/* Mitigating */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
                      <TrendingDown className="w-4 h-4" />
                      <span>Risk-Reducing Factors (-SHAP)</span>
                    </div>

                    <div className="space-y-2">
                      {prediction.top_mitigating_factors.length === 0 ? (
                        <div className="text-xs text-slate-400 italic p-3 bg-slate-50 rounded-lg border border-slate-200">
                          No significant mitigating factors identified.
                        </div>
                      ) : (
                        prediction.top_mitigating_factors.map((f, idx) => (
                          <div
                            key={idx}
                            className="bg-emerald-50/40 border border-emerald-100 p-2.5 rounded-lg flex items-center justify-between text-xs"
                          >
                            <div>
                              <span className="font-semibold text-slate-900 block">
                                {FEATURE_LABELS[f.feature] || f.feature}
                              </span>
                              <span className="text-[10px] text-slate-500 font-mono">{f.feature}</span>
                            </div>
                            <span className="font-mono font-bold text-emerald-600">
                              -{f.importance.toFixed(3)}
                            </span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>

                <div className="text-[10px] text-slate-400 text-center pt-2 border-t border-slate-100 italic">
                  SHAP values describe statistical feature contributions in the tree; they do not establish real-world physical causation.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
