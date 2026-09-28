import React, { useMemo } from 'react';
import { AlertTriangle, CheckCircle2, AlertCircle, Clock, ShieldAlert } from 'lucide-react';
import { DOCUMENT_TYPES } from '../../utils/constants';

export const PreparationAssistancePanel = ({ claimData, selectedWarranty, uploadedFiles }) => {

  const analysis = useMemo(() => {
    const issues = [];
    let isComplete = true;

    const uploadedTypes = uploadedFiles.map(f => f.document_type || 'OTHER');
    const missing = DOCUMENT_TYPES.filter(type => type.required && !uploadedTypes.includes(type.id));
    if (missing.length > 0) {
      isComplete = false;
      issues.push({
        type: 'missing_docs',
        level: 'error',
        title: 'Missing Required Documentation',
        desc: `You have not uploaded: ${missing.map(m => m.label).join(', ')}. Auto-adjudication will fail without these.`,
      });
    }

    if (selectedWarranty && selectedWarranty.expiry_date) {
      const expiry = new Date(selectedWarranty.expiry_date);
      const now = new Date();
      const daysLeft = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));
      
      if (daysLeft < 0 && daysLeft >= -14) { // 14 day grace period
        issues.push({
          type: 'grace_period',
          level: 'warning',
          title: 'Warranty Grace Period',
          desc: `Your warranty expired ${Math.abs(daysLeft)} days ago. You are within the 14-day grace period, but expect strict scrutiny.`,
        });
      } else if (daysLeft < 0) {
        isComplete = false;
        issues.push({
          type: 'expired',
          level: 'error',
          title: 'Warranty Expired',
          desc: `Your warranty expired on ${selectedWarranty.expiry_date}. This claim will likely be rejected.`,
        });
      }
    }

    if (claimData.incident_date && selectedWarranty?.purchase_date) {
      if (new Date(claimData.incident_date) < new Date(selectedWarranty.purchase_date)) {
        isComplete = false;
        issues.push({
          type: 'contradiction',
          level: 'error',
          title: 'Chronological Contradiction Detected',
          desc: `The incident date (${claimData.incident_date}) is before the product purchase date. This will trigger a fraud flag.`,
        });
      }
    }

    if (!claimData.description || claimData.description.length < 20) {
      issues.push({
        type: 'missing_info',
        level: 'warning',
        title: 'Vague Fault Description',
        desc: 'Your fault description is very short. Providing more detail increases the chance of automated approval.',
      });
    }

    return { issues, isComplete };
  }, [claimData, selectedWarranty, uploadedFiles]);

  if (analysis.issues.length === 0) {
    return (
      <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/60 flex items-center gap-3">
        <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
        <div>
          <p className="text-xs font-bold text-emerald-900 dark:text-emerald-200">
            Pre-Submission Check Passed
          </p>
          <p className="text-[11px] text-emerald-700 dark:text-emerald-400">
            No contradictions or missing data found. Claim is ready for AI adjudication.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-2">
        <ShieldAlert className="w-5 h-5 text-amber-500" />
        <h4 className="text-sm font-bold text-slate-900 dark:text-white">
          Claim Preparation Assistance
        </h4>
      </div>
      
      {analysis.issues.map((issue, idx) => (
        <div 
          key={idx} 
          className={`p-4 rounded-2xl border flex items-start gap-3 ${
            issue.level === 'error' 
              ? 'bg-rose-50 dark:bg-rose-950/30 border-rose-200 dark:border-rose-900/60' 
              : 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-900/60'
          }`}
        >
          {issue.level === 'error' ? (
            <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
          )}
          <div>
            <p className={`text-xs font-bold ${
              issue.level === 'error' ? 'text-rose-900 dark:text-rose-200' : 'text-amber-900 dark:text-amber-200'
            }`}>
              {issue.title}
            </p>
            <p className={`text-[11px] mt-0.5 ${
              issue.level === 'error' ? 'text-rose-700 dark:text-rose-400' : 'text-amber-700 dark:text-amber-400'
            }`}>
              {issue.desc}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default PreparationAssistancePanel;
