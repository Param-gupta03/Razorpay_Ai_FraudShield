'use client';

import React from 'react';
import {
  ShieldAlert,
  GitBranch,
  CheckCircle2,
  DollarSign,
  AlertTriangle,
} from 'lucide-react';

export default function AboutTab() {
  return (
    <div className="flex flex-col gap-5 max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center shrink-0">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-tight">
            Risk Policy & Methodology
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Operational rules, decision thresholds, and loss matrix formulation
          </p>
        </div>
      </div>

      {/* Methodology Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Out-of-Time Splitting */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <GitBranch className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">Chronological Splitting</h3>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            Standard k-fold cross validation causes massive temporal data leakage in payment streams. We split strictly along the timeline (<code className="font-mono text-slate-700">TransactionDT</code>):
          </p>
          <ul className="text-xs text-slate-600 space-y-1.5 list-disc pl-4">
            <li>
              <strong className="text-slate-800">Train (70% earliest):</strong> 413,378 checkouts used to train LightGBM trees.
            </li>
            <li>
              <strong className="text-slate-800">Validation (15% middle):</strong> 88,581 checkouts used to select the 0.05 cutoff.
            </li>
            <li>
              <strong className="text-slate-800">Test (15% latest):</strong> 88,581 checkouts evaluated once for honest performance.
            </li>
          </ul>
        </div>

        {/* Defense-Only Policy */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <h3 className="text-sm font-bold text-slate-900">Defense-Only Policy</h3>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            To prevent false declines from destroying legitimate customer lifetime value, FraudShield operates strictly as an advisory system:
          </p>
          <div className="space-y-2 text-xs">
            <div className="p-2.5 rounded-lg bg-emerald-50/50 border border-emerald-200">
              <span className="font-semibold text-emerald-800">Score &lt; 0.05 → AUTO APPROVE</span>
              <p className="text-emerald-700 text-[11px] mt-0.5">
                Low risk. Transaction passes directly to settlement without customer friction.
              </p>
            </div>
            <div className="p-2.5 rounded-lg bg-amber-50/50 border border-amber-200">
              <span className="font-semibold text-amber-800">Score ≥ 0.05 → ROUTE TO REVIEW</span>
              <p className="text-amber-700 text-[11px] mt-0.5">
                Elevated risk. Queued for human verification or secondary authentication.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Expected Loss Model */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
          <DollarSign className="w-4 h-4 text-emerald-600" />
          <h3 className="text-sm font-bold text-slate-900">Expected Financial Cost Model</h3>
        </div>

        <p className="text-xs text-slate-500">
          The 0.05 cutoff minimizes total expected merchant cost under asymmetric payment failure costs:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
            <span className="text-[11px] text-slate-500 font-medium block">
              False Positive Cost (Review Friction)
            </span>
            <span className="font-mono text-xl font-bold text-slate-900 mt-0.5 block">$15.00</span>
            <span className="text-[10px] text-slate-400">Manual review staff overhead and friction</span>
          </div>

          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
            <span className="text-[11px] text-slate-500 font-medium block">
              False Negative Cost (Missed Fraud)
            </span>
            <span className="font-mono text-xl font-bold text-slate-900 mt-0.5 block">$150.00</span>
            <span className="text-[10px] text-slate-400">Chargeback dispute fines + lost merchandise</span>
          </div>
        </div>

        <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 font-mono text-xs text-slate-700 space-y-1">
          <div className="text-[11px] text-slate-400">// Expected Loss Formula</div>
          <div>if action == &apos;APPROVE&apos;: cost = P(Fraud) * $150.00</div>
          <div>if action == &apos;REVIEW&apos;:  cost = (1 - P(Fraud)) * $15.00</div>
        </div>
      </div>

      {/* Production Disclosures */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-900 space-y-2 shadow-sm">
        <div className="flex items-center gap-2 font-semibold text-amber-950">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
          <span>Operational Disclosures</span>
        </div>
        <ul className="space-y-1 list-disc pl-4 text-[11px] text-amber-800">
          <li>
            <strong>Probabilistic, not deterministic:</strong> Scores represent likelihood estimates based on historical patterns. A high probability does not constitute proof of fraud.
          </li>
          <li>
            <strong>SHAP Local Attributions:</strong> Feature contributions describe what mathematical signals pushed the decision tree; they do not imply physical causation.
          </li>
          <li>
            <strong>Missing Identity Profiles:</strong> In the benchmark dataset, ~75% of raw checkouts lack browser/OS telemetry. The engine gracefully relies on card velocity and billing frequencies.
          </li>
        </ul>
      </div>
    </div>
  );
}
