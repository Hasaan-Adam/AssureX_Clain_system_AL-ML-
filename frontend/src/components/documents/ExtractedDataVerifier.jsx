import React, { useState } from 'react';
import { Check, Edit3, AlertCircle, CheckCircle2, RefreshCw } from 'lucide-react';
import { formatCurrency, formatDate } from '../../utils/formatters';

export const ExtractedDataVerifier = ({
  claimData,
  ocrData,
  onVerify,
  onCorrection,
  loading = false,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [correctedData, setCorrectedData] = useState({
    invoice_date: ocrData?.invoice_date || claimData?.purchase_date || '',
    total_amount: ocrData?.total_amount || claimData?.claim_amount || '',
    serial_number: ocrData?.serial_detected || claimData?.serial_number || '',
  });

  const handleSaveCorrection = () => {
    if (onCorrection) {
      onCorrection(correctedData);
    }
    setIsEditing(false);
  };

  const serialMatches =
    String(claimData?.serial_number || '').trim().toLowerCase() ===
    String(ocrData?.serial_detected || claimData?.serial_number || '').trim().toLowerCase();

  return (
    <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-sm font-bold text-slate-900 dark:text-white">
            Document vs Claim Cross-Verification
          </h4>
          <p className="text-xs text-slate-500">
            Compare claimed values with optical text recognition output
          </p>
        </div>

        <button
          type="button"
          onClick={() => setIsEditing(!isEditing)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
        >
          <Edit3 className="w-3.5 h-3.5" />
          <span>{isEditing ? 'Cancel Edit' : 'Edit Discrepancies'}</span>
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left">
          <thead className="bg-slate-50 dark:bg-slate-800/50 text-slate-500 uppercase font-semibold">
            <tr>
              <th className="py-2.5 px-3">Field</th>
              <th className="py-2.5 px-3">Claimed Value</th>
              <th className="py-2.5 px-3">OCR Extracted</th>
              <th className="py-2.5 px-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            <tr>
              <td className="py-3 px-3 font-semibold text-slate-700 dark:text-slate-300">
                Serial Number
              </td>
              <td className="py-3 px-3 font-mono text-slate-600 dark:text-slate-400">
                {claimData?.serial_number || 'N/A'}
              </td>
              <td className="py-3 px-3 font-mono">
                {isEditing ? (
                  <input
                    type="text"
                    value={correctedData.serial_number}
                    onChange={(e) =>
                      setCorrectedData({ ...correctedData, serial_number: e.target.value })
                    }
                    className="px-2 py-1 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded text-xs"
                  />
                ) : (
                  <span className="text-slate-900 dark:text-white">
                    {ocrData?.serial_detected || claimData?.serial_number || 'N/A'}
                  </span>
                )}
              </td>
              <td className="py-3 px-3">
                {serialMatches ? (
                  <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-semibold">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Exact Match
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-amber-600 dark:text-amber-400 font-semibold">
                    <AlertCircle className="w-3.5 h-3.5" /> Mismatch
                  </span>
                )}
              </td>
            </tr>

            <tr>
              <td className="py-3 px-3 font-semibold text-slate-700 dark:text-slate-300">
                Claim / Invoice Amount
              </td>
              <td className="py-3 px-3 text-slate-600 dark:text-slate-400">
                {formatCurrency(claimData?.claim_amount || 0)}
              </td>
              <td className="py-3 px-3">
                {isEditing ? (
                  <input
                    type="number"
                    value={correctedData.total_amount}
                    onChange={(e) =>
                      setCorrectedData({ ...correctedData, total_amount: e.target.value })
                    }
                    className="px-2 py-1 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded text-xs"
                  />
                ) : (
                  <span className="text-slate-900 dark:text-white">
                    {formatCurrency(ocrData?.total_amount || claimData?.claim_amount || 0)}
                  </span>
                )}
              </td>
              <td className="py-3 px-3">
                <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5" /> In Policy Range
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {isEditing && (
        <div className="flex justify-end pt-2">
          <button
            type="button"
            onClick={handleSaveCorrection}
            className="px-4 py-1.5 bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold rounded-xl transition-colors"
          >
            Apply Corrections
          </button>
        </div>
      )}
    </div>
  );
};

export default ExtractedDataVerifier;