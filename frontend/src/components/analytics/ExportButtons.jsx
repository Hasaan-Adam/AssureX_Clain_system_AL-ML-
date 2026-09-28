import React, { useState } from 'react';
import analyticsAPI from '../../api/analyticsAPI';
import reportAPI from '../../api/reportAPI';
import { useNotification } from '../../context/NotificationContext';
import { Download, FileSpreadsheet, FileText, Code2 } from 'lucide-react';
import Loader from '../common/Loader';

export const ExportButtons = ({ params = {} }) => {
  const [exporting, setExporting] = useState(false);
  const { toastSuccess, toastError } = useNotification();

  const handleExportCsv = async () => {
    setExporting(true);
    try {
      const blob = await reportAPI.downloadReportCsv(params);
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `assurex_claims_export_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      toastSuccess('Claims dataset CSV successfully downloaded.');
    } catch (err) {
      toastError(err.message || 'CSV export failed.');
    } finally {
      setExporting(false);
    }
  };

  const handleExportExcel = async () => {
    setExporting(true);
    try {
      const blob = await reportAPI.downloadReportExcel(params);
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `assurex_claims_export_${Date.now()}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      toastSuccess('Claims dataset Excel successfully downloaded.');
    } catch (err) {
      toastError(err.message || 'Excel export failed.');
    } finally {
      setExporting(false);
    }
  };

  const handleExportJson = async () => {
    setExporting(true);
    try {
      const res = await analyticsAPI.exportAnalytics('json', params);
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(res, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', dataStr);
      downloadAnchor.setAttribute('download', `assurex_analytics_${Date.now()}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
      toastSuccess('Analytics JSON exported.');
    } catch (err) {
      toastError(err.message || 'JSON export failed.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        disabled={exporting}
        onClick={handleExportCsv}
        className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl transition-colors shadow-xs"
      >
        <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
        <span>Export CSV</span>
      </button>

      <button
        type="button"
        disabled={exporting}
        onClick={handleExportExcel}
        className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl transition-colors shadow-xs"
      >
        <FileSpreadsheet className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
        <span>Export Excel</span>
      </button>

      <button
        type="button"
        disabled={exporting}
        onClick={handleExportJson}
        className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl transition-colors shadow-xs"
      >
        <Code2 className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />
        <span>Export JSON</span>
      </button>
    </div>
  );
};

export default ExportButtons;
