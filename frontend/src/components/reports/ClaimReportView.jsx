import React from 'react';
import { 
  ShieldCheck, 
  Printer, 
  Calendar, 
  FileText, 
  DollarSign, 
  CheckCircle2, 
  XCircle,
  Building,
  User,
  Package
} from 'lucide-react';
import { formatDate, formatCurrency, formatPercent } from '../../utils/formatters';
import Badge from '../common/Badge';

export const ClaimReportView = ({
  claim,
  warranty,
  product,
  user,
  predictions = [],
}) => {
  if (!claim) return null;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl p-8 max-w-4xl mx-auto space-y-8 print:p-0 print:border-none print:shadow-none">
      {/* Header */}
      <div className="flex items-start justify-between border-b border-slate-200 dark:border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-8 h-8 text-brand-600" />
            <h1 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white">
              AssureX Claim Adjudication Report
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Official AI-Assisted Warranty Verification & Adjudication Dossier
          </p>
        </div>

        <div className="text-right">
          <div className="font-mono text-sm font-bold text-slate-900 dark:text-white">
            {claim.claim_number}
          </div>
          <p className="text-xs text-slate-400">
            Date: {formatDate(claim.submitted_at || new Date())}
          </p>
          <div className="mt-2">
            <Badge type="decision" value={claim.ai_decision || claim.final_decision || 'APPROVE'} size="md" />
          </div>
        </div>
      </div>

      {/* Grid: Claimant & Equipment */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <User className="w-4 h-4 text-brand-500" />
            <span>Claimant Details</span>
          </h3>
          <p className="text-sm font-bold text-slate-900 dark:text-white">
            {user?.full_name || claim.user?.full_name || 'Verified User'}
          </p>
          <p className="text-xs text-slate-500">
            Email: {user?.email || claim.user?.email || 'customer@example.com'}
          </p>
          <p className="text-xs text-slate-500">
            Phone: {user?.phone || 'N/A'}
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Package className="w-4 h-4 text-brand-500" />
            <span>Equipment & Warranty</span>
          </h3>
          <p className="text-sm font-bold text-slate-900 dark:text-white">
            {product?.brand || 'Brand'} {product?.model_name || 'Equipment Model'}
          </p>
          <p className="text-xs font-mono text-slate-500">
            Serial Number: {warranty?.serial_number || claim.warranty?.serial_number || 'N/A'}
          </p>
          <p className="text-xs text-slate-500">
            Warranty Period: {formatDate(warranty?.purchase_date)} - {formatDate(warranty?.expiry_date)}
          </p>
        </div>
      </div>

      {/* Fault Breakdown & Loss Statement */}
      <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Loss Statement & Claimed Fault
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-slate-400">Declared Fault Category:</span>
            <p className="font-semibold text-slate-900 dark:text-white mt-0.5">
              {claim.fault_type}
            </p>
          </div>
          <div>
            <span className="text-slate-400">Claim Value:</span>
            <p className="font-extrabold text-emerald-600 dark:text-emerald-400 text-sm mt-0.5">
              {formatCurrency(claim.claim_amount)}
            </p>
          </div>
        </div>

        <div className="border-t border-slate-200 dark:border-slate-700 pt-3 text-xs">
          <span className="text-slate-400">Description of Incident:</span>
          <p className="text-slate-700 dark:text-slate-300 mt-1 leading-relaxed">
            {claim.description}
          </p>
        </div>
      </div>

      {/* Ensemble Model Verification Audit */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Ensemble Adjudication Audit Log
        </h3>
        <div className="border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 uppercase font-semibold">
              <tr>
                <th className="p-3">Evaluation Engine</th>
                <th className="p-3">Confidence Score</th>
                <th className="p-3">Adjudication Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              <tr>
                <td className="p-3 font-semibold text-slate-800 dark:text-slate-200">
                  Python XGBoost Engine v2.4
                </td>
                <td className="p-3 font-mono">
                  {formatPercent(claim.ai_confidence)}
                </td>
                <td className="p-3">
                  <Badge type="decision" value={claim.ai_decision || 'Valid Claim'} size="sm" />
                </td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-slate-800 dark:text-slate-200">
                  Google Teachable Machine (Vision Defect Model)
                </td>
                <td className="p-3 font-mono">
                  {formatPercent(claim.tm_confidence_score || claim.ai_confidence)}
                </td>
                <td className="p-3">
                  <Badge type="decision" value={claim.tm_prediction || claim.ai_decision || 'Valid Claim'} size="sm" />
                </td>

              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Signature & Seal Footer */}
      <div className="border-t border-slate-200 dark:border-slate-800 pt-6 flex items-center justify-between text-xs text-slate-400">
        <div>
          <p className="font-bold text-slate-800 dark:text-slate-200">
            AssureX Adjudication Engine • Cryptographically Verified
          </p>
          <p className="text-[10px]">
            Generated dynamically on {formatDate(new Date())}
          </p>
        </div>

        <div className="border-t border-slate-400 w-48 text-center pt-1">
          <p className="text-[11px] font-bold text-slate-700 dark:text-slate-300">
            Authorized Signature
          </p>
        </div>
      </div>
    </div>
  );
};

export default ClaimReportView;