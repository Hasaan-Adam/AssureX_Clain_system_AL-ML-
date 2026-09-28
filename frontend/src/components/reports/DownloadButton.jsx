import React, { useState } from 'react';
import reportAPI from '../../api/reportAPI';
import { useNotification } from '../../context/NotificationContext';
import { Download, FileText, Printer } from 'lucide-react';
import Loader from '../common/Loader';

export const DownloadButton = ({
  claimId,
  variant = 'pdf', // 'pdf' or 'print'
  label = 'Download Official Report',
}) => {
  const [downloading, setDownloading] = useState(false);
  const { toastSuccess, toastError } = useNotification();

  const handleDownload = async () => {
    if (variant === 'print') {
      window.print();
      return;
    }

    setDownloading(true);
    try {
      const res = await reportAPI.downloadReportPdf(claimId);
      const blob = res.data || res;
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `AssureX_Claim_Report_${claimId}.pdf`);
      document.body.appendChild(link);
      link.click();
      setTimeout(() => {
        link.parentNode?.removeChild(link);
        window.URL.revokeObjectURL(url);
      }, 100);
      toastSuccess('Official PDF Report downloaded successfully.');
    } catch (err) {
      console.error('PDF Download Error:', err);
      toastError(err.message || 'Failed to download report PDF');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <button
      type="button"
      disabled={downloading}
      onClick={handleDownload}
      className="inline-flex items-center gap-1.5 px-4 py-2 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white text-xs font-semibold rounded-xl shadow-md shadow-brand-500/20 transition-all"
    >
      {downloading ? (
        <Loader size="sm" text="" />
      ) : variant === 'print' ? (
        <Printer className="w-3.5 h-3.5" />
      ) : (
        <Download className="w-3.5 h-3.5" />
      )}
      <span>{label}</span>
    </button>
  );
};

export default DownloadButton;