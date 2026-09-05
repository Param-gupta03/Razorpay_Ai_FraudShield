'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { ArrowDownRight, Layers } from 'lucide-react';

export default function ModelTab() {
  const featureImportance = [
    { name: 'DeviceInfo', score: 190, label: 'Device Platform' },
    { name: 'id_31', score: 122, label: 'Browser Version' },
    { name: 'P_emaildomain', score: 96, label: 'Email Domain' },
    { name: 'TransactionAmt', score: 89, label: 'Order Value' },
    { name: 'addr1_count', score: 88, label: 'Billing Region Velocity' },
    { name: 'C13', score: 79, label: 'Velocity Counter C13' },
    { name: 'card2_count', score: 75, label: 'Bank Velocity' },
    { name: 'card1', score: 70, label: 'Card Issuer BIN' },
    { name: 'card2', score: 67, label: 'Sub-bank ID' },
    { name: 'id_33', score: 64, label: 'Screen Resolution' },
  ];

  return (
    <div className="flex flex-col gap-5">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-tight">
            Model Governance & Benchmark Evaluation
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Production LightGBM pipeline evaluated across chronological splits to measure temporal stability.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono text-slate-600 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200 w-fit">
          <span>Operating Threshold:</span>
          <span className="text-blue-600 font-bold">0.05</span>
        </div>
      </div>

      {/* Split Comparison Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Validation Split */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Validation Split (Tuning Window)</h3>
              <span className="text-xs text-blue-600 font-mono">
                88,581 transactions • Chronological middle 15%
              </span>
            </div>
            <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold border bg-blue-50 text-blue-700 border-blue-200 font-mono">
              In-Sample
            </span>
          </div>

          <p className="text-xs text-slate-500">
            Used to optimize LightGBM tree hyperparameters and calculate the cost-minimizing cutoff (0.05).
          </p>

          <div className="grid grid-cols-5 gap-2 text-center pt-1">
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-500 block">ROC-AUC</span>
              <span className="font-mono font-bold text-slate-900 text-sm">0.9306</span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-500 block">PR-AUC</span>
              <span className="font-mono font-bold text-slate-900 text-sm">0.6185</span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-500 block">Recall</span>
              <span className="font-mono font-bold text-slate-900 text-sm">70.6%</span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-500 block">Precision</span>
              <span className="font-mono font-bold text-slate-900 text-sm">35.2%</span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-500 block">Brier</span>
              <span className="font-mono font-bold text-slate-900 text-sm">0.0198</span>
            </div>
          </div>
        </div>

        {/* Temporal Test Split */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Untouched Out-of-Time Test Set</h3>
              <span className="text-xs text-amber-600 font-mono">
                88,581 transactions • Latest chronological 15%
              </span>
            </div>
            <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold border bg-amber-50 text-amber-700 border-amber-200 font-mono">
              Evaluated Once
            </span>
          </div>

          <p className="text-xs text-slate-500">
            Locked parameters evaluated exactly once to verify out-of-time stability against fraud concept drift.
          </p>

          <div className="grid grid-cols-5 gap-2 text-center pt-1">
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-500 block">ROC-AUC</span>
              <span className="font-mono font-bold text-slate-900 text-sm">0.9057</span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-500 block">PR-AUC</span>
              <span className="font-mono font-bold text-amber-700 text-sm">0.5459</span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-500 block">Recall</span>
              <span className="font-mono font-bold text-slate-900 text-sm">67.5%</span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-500 block">Precision</span>
              <span className="font-mono font-bold text-slate-900 text-sm">28.3%</span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[10px] text-slate-500 block">Brier</span>
              <span className="font-mono font-bold text-slate-900 text-sm">0.0220</span>
            </div>
          </div>
        </div>
      </div>

      {/* Drift Notice Card */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-900 flex items-start gap-3 shadow-sm">
        <ArrowDownRight className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <strong className="font-semibold text-amber-950">Temporal Drift Observation:</strong> PR-AUC decreased from 0.6185 on validation to 0.5459 on the out-of-time test set. This drop is standard across payment datasets due to evolving card fraud patterns, and underscores the need for bi-weekly pipeline re-training in production.
        </div>
      </div>

      {/* Confusion Matrix and Feature Importance */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Confusion Matrix (5 cols) */}
        <div className="lg:col-span-5 bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between gap-4">
          <div>
            <div className="flex items-center justify-between mb-1">
              <h3 className="text-sm font-bold text-slate-900">Test Confusion Matrix</h3>
              <span className="text-xs font-mono text-slate-500 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded">
                Threshold: 0.05
              </span>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Classification performance on all 88,581 out-of-time test checkouts.
            </p>

            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              <div />
              <div className="bg-slate-50 p-2 rounded-lg font-medium text-slate-600 text-[11px]">
                Actual Legit
              </div>
              <div className="bg-slate-50 p-2 rounded-lg font-medium text-slate-600 text-[11px]">
                Actual Fraud
              </div>

              <div className="bg-slate-50 p-2 rounded-lg font-medium text-slate-600 text-[11px] flex items-center justify-center">
                Pred. Approve
              </div>
              <div className="bg-emerald-50 border border-emerald-200 p-3 rounded-lg flex flex-col justify-center">
                <span className="font-mono font-bold text-emerald-800 text-sm">80,216</span>
                <span className="text-[9px] text-emerald-600 uppercase font-mono mt-0.5">True Neg (93.8%)</span>
              </div>
              <div className="bg-rose-50 border border-rose-200 p-3 rounded-lg flex flex-col justify-center">
                <span className="font-mono font-bold text-rose-800 text-sm">1,003</span>
                <span className="text-[9px] text-rose-600 uppercase font-mono mt-0.5">False Neg (1.1%)</span>
              </div>

              <div className="bg-slate-50 p-2 rounded-lg font-medium text-slate-600 text-[11px] flex items-center justify-center">
                Pred. Review
              </div>
              <div className="bg-amber-50 border border-amber-200 p-3 rounded-lg flex flex-col justify-center">
                <span className="font-mono font-bold text-amber-800 text-sm">5,282</span>
                <span className="text-[9px] text-amber-600 uppercase font-mono mt-0.5">False Pos (6.0%)</span>
              </div>
              <div className="bg-emerald-50 border border-emerald-200 p-3 rounded-lg flex flex-col justify-center">
                <span className="font-mono font-bold text-emerald-800 text-sm">2,080</span>
                <span className="text-[9px] text-emerald-600 uppercase font-mono mt-0.5">True Pos (2.3%)</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 text-xs text-slate-600 space-y-1">
            <div className="flex justify-between">
              <span>Caught Frauds:</span>
              <span className="font-mono font-semibold text-slate-900">2,080 / 3,083 (67.5% Recall)</span>
            </div>
            <div className="flex justify-between">
              <span>Review Rate:</span>
              <span className="font-mono font-semibold text-slate-900">8.31% of checkout traffic</span>
            </div>
          </div>
        </div>

        {/* Feature Importance (7 cols) */}
        <div className="lg:col-span-7 bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between gap-4">
          <div>
            <div className="flex items-center justify-between mb-1">
              <h3 className="text-sm font-bold text-slate-900">Top Feature Splits</h3>
              <span className="text-xs font-mono text-slate-500 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded">
                LightGBM Trees
              </span>
            </div>
            <p className="text-xs text-slate-500 mb-2">
              Frequency of tree branch splits across all boosted estimators in the ensemble.
            </p>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={featureImportance}
                  layout="vertical"
                  margin={{ top: 5, right: 20, left: 70, bottom: 5 }}
                >
                  <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    tick={{ fill: '#334155', fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    width={85}
                  />
                  <Tooltip
                    cursor={{ fill: '#f1f5f9' }}
                    formatter={(val) => [val, 'Split Count']}
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                    }}
                    itemStyle={{ color: '#0f172a', fontSize: '12px' }}
                  />
                  <Bar dataKey="score" radius={[0, 4, 4, 0]} barSize={12}>
                    {featureImportance.map((_, idx) => (
                      <Cell key={`cell-${idx}`} fill="#2563eb" />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100 text-[11px] text-slate-400 text-center">
            Feature importances reflect statistical split utility; they do not indicate real-world physical causation.
          </div>
        </div>
      </div>
    </div>
  );
}
