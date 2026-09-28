import React, { useState } from 'react';
import reportAPI from '../api/reportAPI';
import { useNotification } from '../context/NotificationContext';
import { FileDown, FileText, CheckSquare, BarChart3 } from 'lucide-react';
import Loader from '../components/common/Loader';

const downloadBlob = (data, filename) => {
  const blob = data instanceof Blob ? data : new Blob([data]);
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

export const ReportsPage = () => {
  const { toastSuccess, toastError, toastInfo } = useNotification();
  
  const [downloading, setDownloading] = useState({
    claimsCSV: false,
    claimsExcel: false,
    reviewsCSV: false,
  });

  const [dateFilter, setDateFilter] = useState({ from: '', to: '' });

  const handleExport = async (type) => {
    setDownloading(prev => ({ ...prev, [type]: true }));
    try {
      let response;
      let filename;
      const params = {};
      if (dateFilter.from) params.from = dateFilter.from;
      if (dateFilter.to) params.to = dateFilter.to;

      if (type === 'claimsCSV') {
        response = await reportAPI.exportClaimsCSV(params);
        filename = 'assurex_claims.csv';
      } else if (type === 'claimsExcel') {
        response = await reportAPI.exportClaimsExcel(params);
        filename = 'assurex_claims.xlsx';
      } else if (type === 'reviewsCSV') {
        response = await reportAPI.exportReviewsCSV(params);
        filename = 'assurex_reviews.csv';
      }

      if (response) {
        downloadBlob(response, filename);
        toastSuccess(`${filename} downloaded successfully.`);
      }
    } catch (error) {
      console.error(error);
      toastError(`Failed to export ${type}.`);
    } finally {
      setDownloading(prev => ({ ...prev, [type]: false }));
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-3 border-b border-slate-200 dark:border-slate-800 pb-5">
        <FileDown className="w-8 h-8 text-brand-600" />
        <div>
          <h1 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white">Reports & Export Center</h1>
          <p className="text-sm text-slate-500 mt-1">Professional Data Export and Analytics</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Card 1 - Claims Report */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-brand-200 dark:border-brand-900 shadow-sm p-6 flex flex-col">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-brand-100 dark:bg-brand-900/50 rounded-xl text-brand-600 dark:text-brand-400">
              <FileText className="w-6 h-6" />
            </div>
            <h2 className="font-bold text-lg text-slate-900 dark:text-white">Claims Data Export</h2>
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 flex-1">
            Full claims dataset with AI decisions, confidence scores, and audit trail
          </p>
          
          <div className="space-y-4">
            <div className="flex gap-2">
              <input type="date" className="text-sm p-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800 w-full" value={dateFilter.from} onChange={e => setDateFilter({...dateFilter, from: e.target.value})} title="From Date" />
              <input type="date" className="text-sm p-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800 w-full" value={dateFilter.to} onChange={e => setDateFilter({...dateFilter, to: e.target.value})} title="To Date" />
            </div>
            
            <div className="flex gap-3">
              <button 
                onClick={() => handleExport('claimsCSV')} 
                disabled={downloading.claimsCSV || downloading.claimsExcel}
                className="flex-1 flex justify-center items-center py-2 border border-brand-600 text-brand-600 hover:bg-brand-50 dark:hover:bg-brand-900/20 disabled:opacity-50 rounded-xl text-sm font-semibold transition-colors"
              >
                {downloading.claimsCSV ? <Loader size="sm" text="" /> : 'Export CSV'}
              </button>
              <button 
                onClick={() => handleExport('claimsExcel')} 
                disabled={downloading.claimsCSV || downloading.claimsExcel}
                className="flex-1 flex justify-center items-center py-2 bg-brand-600 hover:bg-brand-700 text-white disabled:opacity-50 rounded-xl text-sm font-semibold transition-colors"
              >
                {downloading.claimsExcel ? <Loader size="sm" text="" /> : 'Export Excel'}
              </button>
            </div>
          </div>
        </div>

        {/* Card 2 - Review Activity */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-violet-200 dark:border-violet-900 shadow-sm p-6 flex flex-col">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-violet-100 dark:bg-violet-900/50 rounded-xl text-violet-600 dark:text-violet-400">
              <CheckSquare className="w-6 h-6" />
            </div>
            <h2 className="font-bold text-lg text-slate-900 dark:text-white">Review Activity Report</h2>
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 flex-1">
            Adjudicator decisions, manual overrides, and SLA compliance data
          </p>
          <button 
            onClick={() => handleExport('reviewsCSV')} 
            disabled={downloading.reviewsCSV}
            className="w-full flex justify-center items-center py-2 bg-violet-600 hover:bg-violet-700 text-white disabled:opacity-50 rounded-xl text-sm font-semibold transition-colors mt-auto"
          >
            {downloading.reviewsCSV ? <Loader size="sm" text="" /> : 'Export CSV'}
          </button>
        </div>

        {/* Card 3 - AI Performance */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-emerald-200 dark:border-emerald-900 shadow-sm p-6 flex flex-col">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-emerald-100 dark:bg-emerald-900/50 rounded-xl text-emerald-600 dark:text-emerald-400">
              <BarChart3 className="w-6 h-6" />
            </div>
            <h2 className="font-bold text-lg text-slate-900 dark:text-white">AI Model Performance</h2>
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 flex-1">
            Dual-model accuracy metrics, confusion matrices, and confidence analysis
          </p>
          <button 
            onClick={() => toastInfo('Coming soon')} 
            className="w-full flex justify-center items-center py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-semibold transition-colors mt-auto"
          >
            Generate Report
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;

