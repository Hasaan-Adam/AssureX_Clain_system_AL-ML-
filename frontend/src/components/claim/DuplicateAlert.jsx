import React from 'react';
import { ShieldAlert, AlertTriangle, ArrowRight, History } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DuplicateAlert = ({
  fraudScore = 0.85,
  duplicateClaimNumber = 'CLM-2025-0412',
  serialNumber = 'SN-SNY-2025-0819',
}) => {
  return (
    <div className="p-5 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-300 dark:border-rose-800 shadow-sm space-y-3 animate-slide-up">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-xl bg-rose-100 dark:bg-rose-900/60 text-rose-600 dark:text-rose-300 shrink-0">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-bold text-rose-900 dark:text-rose-200">
            Duplicate Claim Detection
          </h4>
          <p className="text-xs text-rose-700 dark:text-rose-300 mt-0.5">
            Serial Number <strong className="font-mono">{serialNumber}</strong> was previously adjudicated under claim{' '}
            <strong className="font-mono">{duplicateClaimNumber}</strong>. High anomaly score ({Math.round(fraudScore * 100)}%).
          </p>
        </div>
      </div>

      <div className="flex items-center justify-end gap-2 pt-2 border-t border-rose-200 dark:border-rose-900/60">
        <Link
          to={`/claims/by-number/${duplicateClaimNumber}`}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-xl transition-colors shadow-xs"
        >
          <History className="w-3.5 h-3.5" />
          <span>Inspect Historical Claim</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
};

export default DuplicateAlert;