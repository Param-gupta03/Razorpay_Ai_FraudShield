'use client';

import React, { useState } from 'react';
import {
  TrendingUp,
  ShieldCheck,
  AlertTriangle,
  PiggyBank,
  ArrowUpRight,
  Info,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from 'recharts';

interface DashboardTabProps {
  setActiveTab: (tab: string) => void;
}

export default function DashboardTab({ setActiveTab }: DashboardTabProps) {
  const [timeRange, setTimeRange] = useState<'test' | 'full'>('test');

  const stats = [
    {
      title: 'Scored Transactions',
      val: '88,581',
      badge: 'Test Set',
      sub: 'Chronological test split volume',
      badgeClass: 'bg-slate-100 text-slate-700 border-slate-200',
    },
    {
      title: 'Fraud Catch Rate',
      val: '67.5%',
      badge: '2,080 / 3,083',
      sub: 'Recall caught at 0.05 threshold',
      badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
    {
      title: 'Queue Review Rate',
      val: '8.3%',
      badge: '7,362 Items',
      sub: 'Flagged for human analyst validation',
      badgeClass: 'bg-amber-50 text-amber-700 border-amber-200',
    },
    {
      title: 'Estimated Net Savings',
      val: '$232,770',
      badge: '+50.3% ROI',
      sub: 'Chargebacks avoided less review costs',
      badgeClass: 'bg-blue-50 text-blue-700 border-blue-200',
    },
  ];

  const distribution = [
    { name: 'Auto-Approved (Low Risk)', value: 81219, pct: '91.7%', color: '#10b981' },
    { name: 'Review Queue (False Alarm)', value: 5282, pct: '6.0%', color: '#f59e0b' },
    { name: 'Review Queue (Caught Fraud)', value: 2080, pct: '2.3%', color: '#ef4444' },
  ];

  const costComparison = [
    { name: 'Unmanaged Fraud (No ML)', cost: 462450, fill: '#ef4444' },
    { name: 'Managed (FraudShield)', cost: 229680, fill: '#2563eb' },
  ];

  return (
    <div className="flex flex-col gap-5">
      {/* Top Banner & Range Toggles */}
      <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-tight">
              Executive Risk Overview
            </h2>
            <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold border bg-blue-50 text-blue-700 border-blue-200 font-mono">
              Cutoff: 0.05
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Evaluating checkouts chronologically with calibrated loss matrix. Defense-only mode: approves or flags for review.
          </p>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-between sm:justify-end">
          <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
            <button
              onClick={() => setTimeRange('test')}
              className={`px-3 py-1 rounded-md font-medium transition cursor-pointer ${
                timeRange === 'test' ? 'bg-white text-slate-900 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Temporal Test Split
            </button>
            <button
              onClick={() => setTimeRange('full')}
              className={`px-3 py-1 rounded-md font-medium transition cursor-pointer ${
                timeRange === 'full' ? 'bg-white text-slate-900 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Full Population
            </button>
          </div>

          <button
            onClick={() => setActiveTab('analyzer')}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-3.5 py-2 rounded-lg transition shadow-sm cursor-pointer"
          >
            <span>Scan Transaction</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Metrics Cards Grid - styled like assignment MetricsCards.jsx */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => (
          <div
            key={idx}
            className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between gap-2"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                {stat.title}
              </span>
              <span className={`px-2 py-0.5 rounded-full text-[11px] font-semibold border ${stat.badgeClass}`}>
                {stat.badge}
              </span>
            </div>
            <div>
              <div className="text-2xl font-bold font-mono text-slate-900">{stat.val}</div>
              <div className="text-xs text-slate-500 mt-0.5">{stat.sub}</div>
            </div>
          </div>
        ))}
      </section>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Outcome Donut Chart */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between gap-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Checkout Disposition</h3>
              <p className="text-xs text-slate-500">Distribution across 88,581 temporal test transactions</p>
            </div>
            <span className="text-xs font-mono text-slate-500 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded">
              88.5k Total
            </span>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-6 my-2">
            <div className="w-full sm:w-1/2 h-52">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={75}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                    }}
                    itemStyle={{ color: '#0f172a', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="w-full sm:w-1/2 space-y-2">
              {distribution.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs"
                >
                  <div className="flex items-center gap-2">
                    <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-slate-700 text-[11px] font-medium">{item.name}</span>
                  </div>
                  <div className="text-right">
                    <span className="font-mono font-semibold text-slate-900 block">
                      {item.value.toLocaleString()}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">{item.pct}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>SLA: Review items within 2 hrs</span>
            <button
              onClick={() => setActiveTab('transactions')}
              className="text-blue-600 hover:text-blue-700 font-medium hover:underline cursor-pointer"
            >
              Open review queue →
            </button>
          </div>
        </div>

        {/* Financial Cost Impact Bar Chart */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between gap-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Expected Loss Comparison</h3>
              <p className="text-xs text-slate-500">Unmanaged fraud vs. FraudShield managed cost</p>
            </div>
            <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold border bg-emerald-50 text-emerald-700 border-emerald-200 font-mono">
              -$232,770 net savings
            </span>
          </div>

          <div className="h-52 my-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={costComparison} margin={{ top: 15, right: 20, left: 10, bottom: 5 }}>
                <XAxis
                  dataKey="name"
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  axisLine={{ stroke: '#e2e8f0' }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: '#64748b', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  cursor={{ fill: '#f1f5f9' }}
                  formatter={(val) => [`$${Number(val).toLocaleString()}`, 'Expected Cost']}
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                  }}
                  itemStyle={{ color: '#0f172a', fontSize: '12px' }}
                />
                <Bar dataKey="cost" radius={[6, 6, 0, 0]} barSize={56}>
                  {costComparison.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Model assumption: $15 manual review, $150 chargeback</span>
            <button
              onClick={() => setActiveTab('model')}
              className="text-blue-600 hover:text-blue-700 font-medium hover:underline cursor-pointer"
            >
              View model audit →
            </button>
          </div>
        </div>
      </div>

      {/* Merchant Notice Card */}
      <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-900 flex items-start gap-3 shadow-sm">
        <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
        <div>
          <strong className="font-semibold text-blue-950">Operational Policy Note:</strong> Transactions between{' '}
          <span className="font-mono font-semibold">0.05</span> and <span className="font-mono font-semibold">0.30</span>{' '}
          probability are placed into the human review queue rather than being auto-declined. This saves legitimate checkout conversions and protects customer lifetime value.
        </div>
      </div>
    </div>
  );
}
