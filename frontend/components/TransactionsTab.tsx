'use client';

import React, { useState, useMemo } from 'react';
import {
  Upload,
  ArrowRight,
  Download,
  Filter,
  Search,
  CheckCircle2,
  AlertTriangle,
  FileSpreadsheet,
  RefreshCw,
} from 'lucide-react';
import { DEMO_TRANSACTIONS, DemoTransaction } from '../lib/demoData';
import { predictBatch } from '../lib/api';

interface TransactionsTabProps {
  onSelectTransaction: (tx: DemoTransaction) => void;
  apiHealthy: boolean | null;
}

export default function TransactionsTab({
  onSelectTransaction,
  apiHealthy,
}: TransactionsTabProps) {
  const [filterRisk, setFilterRisk] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [batchResults, setBatchResults] = useState<{
    total: number;
    highRisk: number;
    reviewRequired: number;
    avgProbability: number;
    downloadUrl: string;
    fileName: string;
  } | null>(null);

  const filtered = useMemo(() => {
    return DEMO_TRANSACTIONS.filter((tx) => {
      if (filterRisk !== 'ALL' && tx.expectedRisk !== filterRisk) return false;
      if (!searchQuery.trim()) return true;

      const q = searchQuery.toLowerCase();
      const matchId = tx.TransactionID.toString().includes(q);
      const matchEmail = (tx.P_emaildomain || '').toLowerCase().includes(q);
      const matchCard = (tx.card1?.toString() || '').includes(q);
      const matchProduct = (tx.ProductCD || '').toLowerCase().includes(q);
      return matchId || matchEmail || matchCard || matchProduct;
    });
  }, [filterRisk, searchQuery]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadError(null);
      setBatchResults(null);
    }
  };

  const handleBatchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      const resultBlob = await predictBatch(file);
      const text = await resultBlob.text();
      const rows = text.split('\n').map((r) => r.split(','));

      if (rows.length < 2) {
        throw new Error('Returned CSV has no rows.');
      }

      const headers = rows[0].map((h) => h.trim().replace(/"/g, ''));
      const probIdx = headers.indexOf('fraud_probability');
      const riskIdx = headers.indexOf('risk_level');
      const actionIdx = headers.indexOf('recommended_action');

      let total = 0;
      let highRisk = 0;
      let reviewRequired = 0;
      let sumProb = 0.0;

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (row.length < headers.length) continue;

        total++;
        const prob = parseFloat(row[probIdx]);
        const risk = row[riskIdx]?.trim().replace(/"/g, '');
        const action = row[actionIdx]?.trim().replace(/"/g, '');

        if (!isNaN(prob)) sumProb += prob;
        if (risk === 'HIGH') highRisk++;
        if (action === 'REVIEW') reviewRequired++;
      }

      const downloadUrl = window.URL.createObjectURL(resultBlob);

      setBatchResults({
        total,
        highRisk,
        reviewRequired,
        avgProbability: total > 0 ? sumProb / total : 0,
        downloadUrl,
        fileName: `scored_${file.name}`,
      });
    } catch (err: any) {
      setUploadError(err.message || 'Batch upload failed. Verify CSV columns.');
    } finally {
      setIsUploading(false);
    }
  };

  const downloadSampleCsv = () => {
    const header = 'TransactionID,TransactionDT,TransactionAmt,ProductCD,card1,card2,card6,P_emaildomain\n';
    const sampleRows = [
      '3000001,86450,45.00,W,13926,523.0,debit,gmail.com',
      '3000002,86490,185.00,W,9500,321.0,credit,anonymous.com',
      '3000003,86530,12.50,C,4461,375.0,debit,yahoo.com',
      '3000004,86580,240.00,W,13926,523.0,credit,hotmail.com',
    ].join('\n');

    const blob = new Blob([header + sampleRows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_transactions.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col gap-5">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left 8 cols: Table styled like assignment JobHistory.jsx */}
        <section className="lg:col-span-8 bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between gap-4">
          <div>
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
              <div>
                <h2 className="text-sm font-bold text-slate-900">Audited Transactions Queue</h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Verified historic test cases. Click <strong>Inspect</strong> to run through live risk engine.
                </p>
              </div>

              {/* Controls */}
              <div className="flex items-center gap-2 w-full sm:w-auto">
                <div className="relative flex-1 sm:flex-initial">
                  <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                  <input
                    type="text"
                    placeholder="Search ID, card, email..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full sm:w-44 bg-slate-50 border border-slate-200 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 outline-none focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  />
                </div>

                <div className="flex items-center gap-1.5 bg-slate-50 px-2 py-1.5 rounded-lg border border-slate-200 text-xs">
                  <Filter className="w-3.5 h-3.5 text-slate-400" />
                  <select
                    value={filterRisk}
                    onChange={(e) => setFilterRisk(e.target.value)}
                    className="bg-transparent text-xs text-slate-700 outline-none cursor-pointer"
                  >
                    <option value="ALL">All Tiers</option>
                    <option value="LOW">Low Risk</option>
                    <option value="MEDIUM">Medium Risk</option>
                    <option value="HIGH">High Risk</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold text-[11px] tracking-wider">
                    <th className="p-3">Tx ID</th>
                    <th className="p-3">Amount</th>
                    <th className="p-3">Channel</th>
                    <th className="p-3">Card / Email</th>
                    <th className="p-3">Model Score</th>
                    <th className="p-3">Action</th>
                    <th className="p-3 text-right">Inspect</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filtered.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="p-8 text-center text-slate-400 italic bg-slate-50/50">
                        No transactions match search criteria.
                      </td>
                    </tr>
                  ) : (
                    filtered.map((tx) => (
                      <tr key={tx.TransactionID} className="hover:bg-slate-50/80 transition">
                        <td className="p-3 font-mono font-medium text-slate-900">
                          #{tx.TransactionID}
                        </td>
                        <td className="p-3 font-mono font-semibold text-slate-900">
                          ${tx.TransactionAmt.toFixed(2)}
                        </td>
                        <td className="p-3">
                          <span className="bg-slate-100 px-2 py-0.5 rounded text-[11px] font-mono text-slate-700 border border-slate-200">
                            {tx.ProductCD}
                          </span>
                        </td>
                        <td className="p-3">
                          <div className="text-[11px] text-slate-600 leading-tight">
                            <span>{tx.card1} ({tx.card6})</span>
                            <span className="block text-slate-400 font-mono text-[10px]">
                              {tx.P_emaildomain || 'no domain'}
                            </span>
                          </div>
                        </td>
                        <td className="p-3">
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                              tx.expectedRisk === 'LOW'
                                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                                : tx.expectedRisk === 'MEDIUM'
                                ? 'bg-amber-50 text-amber-700 border-amber-200'
                                : 'bg-rose-50 text-rose-700 border-rose-200'
                            }`}
                          >
                            {tx.expectedRisk}
                          </span>
                        </td>
                        <td className="p-3 font-medium">
                          <span
                            className={`text-[11px] ${
                              tx.expectedAction === 'APPROVE' ? 'text-emerald-700' : 'text-amber-700'
                            }`}
                          >
                            {tx.expectedAction}
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <button
                            onClick={() => onSelectTransaction(tx)}
                            className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium text-xs cursor-pointer transition hover:underline"
                          >
                            <span>Analyze</span>
                            <ArrowRight className="w-3 h-3" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Showing {filtered.length} audited transactions</span>
            <span>IEEE-CIS Benchmark Samples</span>
          </div>
        </section>

        {/* Right 4 cols: Batch CSV Prediction */}
        <section className="lg:col-span-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between gap-4">
          <div>
            <div className="flex items-center justify-between mb-1">
              <h3 className="text-sm font-bold text-slate-900">Batch CSV Scoring</h3>
              <button
                onClick={downloadSampleCsv}
                className="text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1 cursor-pointer hover:underline"
              >
                <FileSpreadsheet className="w-3.5 h-3.5" />
                <span>Sample CSV</span>
              </button>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Upload a transactions list to run bulk LightGBM inference and export risk predictions.
            </p>

            <form onSubmit={handleBatchSubmit} className="space-y-3">
              <label className="border-2 border-dashed border-slate-200 hover:border-slate-300 bg-slate-50 rounded-xl p-6 block transition text-center cursor-pointer">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="hidden"
                  disabled={isUploading || apiHealthy === false}
                />
                <Upload className="w-7 h-7 text-slate-400 mx-auto mb-2" />
                <div className="text-xs font-semibold text-slate-700">
                  {file ? file.name : 'Choose CSV or drag & drop'}
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">Up to 50MB per batch</div>
              </label>

              {uploadError && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-xs flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0 text-rose-500" />
                  <span>{uploadError}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={!file || isUploading || apiHealthy === false}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs py-2.5 rounded-lg transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center gap-2"
              >
                {isUploading ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Scoring Batch CSV...</span>
                  </>
                ) : (
                  <span>Run Batch Inference</span>
                )}
              </button>
            </form>

            <div className="mt-4 p-3 rounded-lg bg-slate-50 border border-slate-200 text-[11px] text-slate-500 space-y-1">
              <span className="font-semibold text-slate-700 block">Required Columns:</span>
              <code className="text-[10px] text-blue-700 font-mono block">
                TransactionID, TransactionDT, TransactionAmt, ProductCD, card1
              </code>
              <p className="text-[10px] text-slate-400 mt-1">
                Optional columns are imputed dynamically if missing.
              </p>
            </div>
          </div>

          {/* Results card */}
          {batchResults && (
            <div className="mt-2 p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-3 animate-fadeIn">
              <div className="flex items-center gap-2 text-emerald-800 text-xs font-semibold">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Batch Scored Successfully</span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-center text-xs">
                <div className="bg-white p-2 rounded-lg border border-emerald-100 shadow-xs">
                  <span className="text-[10px] text-slate-500 block">Total Scored</span>
                  <span className="font-mono font-bold text-slate-900">{batchResults.total}</span>
                </div>
                <div className="bg-white p-2 rounded-lg border border-emerald-100 shadow-xs">
                  <span className="text-[10px] text-slate-500 block">Avg Risk</span>
                  <span className="font-mono font-bold text-slate-900">
                    {(batchResults.avgProbability * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="bg-white p-2 rounded-lg border border-emerald-100 shadow-xs">
                  <span className="text-[10px] text-slate-500 block">High Risk</span>
                  <span className="font-mono font-bold text-rose-600">{batchResults.highRisk}</span>
                </div>
                <div className="bg-white p-2 rounded-lg border border-emerald-100 shadow-xs">
                  <span className="text-[10px] text-slate-500 block">Review Flagged</span>
                  <span className="font-mono font-bold text-amber-600">
                    {batchResults.reviewRequired}
                  </span>
                </div>
              </div>

              <a
                href={batchResults.downloadUrl}
                download={batchResults.fileName}
                className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs py-2 rounded-lg transition shadow-sm text-center cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download Scored Results (.csv)</span>
              </a>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
