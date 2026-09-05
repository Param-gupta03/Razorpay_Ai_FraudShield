'use client';

import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import DashboardTab from '../components/DashboardTab';
import TransactionsTab from '../components/TransactionsTab';
import AnalyzerTab from '../components/AnalyzerTab';
import ModelTab from '../components/ModelTab';
import AboutTab from '../components/AboutTab';
import { DemoTransaction } from '../lib/demoData';
import { fetchHealth } from '../lib/api';

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [preselectedTx, setPreselectedTx] = useState<DemoTransaction | null>(null);
  const [apiHealthy, setApiHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function check() {
      try {
        const res = await fetchHealth();
        if (isMounted) setApiHealthy(res.status === 'healthy');
      } catch (err) {
        if (isMounted) setApiHealthy(false);
      }
    }

    check();
    const interval = setInterval(check, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleSelectTx = (tx: DemoTransaction) => {
    setPreselectedTx(tx);
    setActiveTab('analyzer');
  };

  return (
    <div className="max-w-7xl mx-auto flex flex-col gap-5">
      {/* Navbar styled like assignment Navbar.jsx */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        apiHealthy={apiHealthy}
      />

      {/* Backend alert banner */}
      {apiHealthy === false && (
        <div className="bg-rose-50 border border-rose-200 text-rose-700 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs shadow-sm">
          <div className="flex items-center gap-2.5">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500"></span>
            </span>
            <span>
              <strong>Risk API Offline:</strong> FastAPI backend is unreachable on port 8000. Run{' '}
              <code className="bg-rose-100 px-1.5 py-0.5 rounded font-mono text-rose-800">
                uvicorn app.main:app --reload
              </code>.
            </span>
          </div>
          <button
            onClick={async () => {
              setApiHealthy(null);
              try {
                const res = await fetchHealth();
                setApiHealthy(res.status === 'healthy');
              } catch {
                setApiHealthy(false);
              }
            }}
            className="px-3 py-1.5 rounded-lg font-medium bg-rose-100 hover:bg-rose-200 text-rose-800 transition cursor-pointer self-end sm:self-auto"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Active Tab View */}
      <main className="min-h-[520px]">
        {activeTab === 'dashboard' && <DashboardTab setActiveTab={setActiveTab} />}
        {activeTab === 'transactions' && (
          <TransactionsTab
            onSelectTransaction={handleSelectTx}
            apiHealthy={apiHealthy}
          />
        )}
        {activeTab === 'analyzer' && (
          <AnalyzerTab
            preselectedTx={preselectedTx}
            clearPreselectedTx={() => setPreselectedTx(null)}
            apiHealthy={apiHealthy}
          />
        )}
        {activeTab === 'model' && <ModelTab />}
        {activeTab === 'about' && <AboutTab />}
      </main>

      {/* Footer matching assignment style */}
      <footer className="text-center py-2 text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2 border-t border-slate-200 pt-4">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-700">FraudShield</span>
          <span>•</span>
          <span>Risk Decision Engine</span>
          <span className="text-slate-400 font-mono text-[11px]">v2.4.0</span>
        </div>
        <div className="text-[11px] text-slate-500">
          LightGBM (loss-optimized cutoff: 0.05) • Defense-only advisory system
        </div>
      </footer>
    </div>
  );
}
