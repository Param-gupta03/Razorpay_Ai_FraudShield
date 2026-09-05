'use client';

import React from 'react';
import {
  ShieldAlert,
  LayoutDashboard,
  ReceiptText,
  ScanSearch,
  Activity,
  FileQuestion,
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  apiHealthy: boolean | null;
}

export default function Navbar({ activeTab, setActiveTab, apiHealthy }: NavbarProps) {
  const tabs = [
    { id: 'dashboard', label: 'Overview', icon: LayoutDashboard },
    { id: 'transactions', label: 'Transactions', icon: ReceiptText },
    { id: 'analyzer', label: 'Risk Analyzer', icon: ScanSearch },
    { id: 'model', label: 'Model Metrics', icon: Activity },
    { id: 'about', label: 'Policy & Docs', icon: FileQuestion },
  ];

  const isConnected = apiHealthy === true;
  const isConnecting = apiHealthy === null;

  const statusBg = isConnected
    ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
    : isConnecting
    ? 'bg-amber-50 text-amber-700 border-amber-200'
    : 'bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100 cursor-pointer';

  const dotColor = isConnected
    ? 'bg-emerald-500'
    : isConnecting
    ? 'bg-amber-500 animate-pulse'
    : 'bg-rose-500';

  return (
    <header className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
      {/* Brand logo & title */}
      <div
        className="flex items-center gap-3 cursor-pointer"
        onClick={() => setActiveTab('dashboard')}
      >
        <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center shrink-0">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base sm:text-lg font-bold text-slate-900 leading-tight">
              FraudShield AI
            </h1>
            <span className="text-[10px] font-mono font-medium uppercase bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200">
              Live Desk
            </span>
          </div>
          <p className="text-xs text-slate-500">
            Real-time transaction risk scoring and defense advisory console
          </p>
        </div>
      </div>

      {/* Navigation tabs styled like assignment segmented control */}
      <nav className="flex flex-wrap gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs w-full lg:w-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition cursor-pointer ${
                isActive
                  ? 'bg-white text-slate-900 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Right controls: Merchant Tag & Backend Status */}
      <div className="flex items-center gap-3 w-full lg:w-auto justify-between lg:justify-end">
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-medium">Merchant:</span>
          <span className="text-xs font-mono bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-slate-700">
            acme_corp
          </span>
        </div>

        <div
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs border font-medium transition ${statusBg}`}
        >
          <span className={`w-2 h-2 rounded-full ${dotColor}`} />
          <span>
            {isConnected
              ? 'Engine Online'
              : isConnecting
              ? 'Connecting...'
              : 'Engine Offline'}
          </span>
        </div>
      </div>
    </header>
  );
}
