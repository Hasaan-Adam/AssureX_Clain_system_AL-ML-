import React from 'react';
import { Lightbulb, ThumbsUp, AlertTriangle, BookOpen, Sparkles } from 'lucide-react';

export const DecisionExplanation = ({
  decision = 'APPROVE',
  reasons = [],
  riskFactors = [],
  policyBasis = null,
}) => {
  const isApproved = decision === 'APPROVE';
  const isRejected = decision === 'REJECT';

  return (
    <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
      <div className="flex items-center gap-2.5 border-b border-slate-100 dark:border-slate-800 pb-4">
        <div className="p-2 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400">
          <Lightbulb className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            Adjudication Reasoning & Explainability
          </h3>
          <p className="text-xs text-slate-500">
            Transparent breakdown of model adjudication factors
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Supporting Factors */}
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5 mb-2">
            <ThumbsUp className="w-3.5 h-3.5" />
            <span>Favorable Adjudication Factors</span>
          </h4>
          {reasons.length === 0 ? (
            <p className="text-sm text-slate-500 italic">No explanation provided by the AI engine for this decision.</p>
          ) : (
            <ul className="space-y-1.5">
              {reasons.map((r, i) => (
                <li
                  key={i}
                  className="text-xs text-slate-700 dark:text-slate-300 flex items-start gap-2 bg-slate-50 dark:bg-slate-800/40 p-2.5 rounded-xl border border-slate-100 dark:border-slate-800"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Risk Factors if any */}
        {riskFactors.length > 0 && (
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400 flex items-center gap-1.5 mb-2">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Identified Risk / Discrepancy Factors</span>
            </h4>
            <ul className="space-y-1.5">
              {riskFactors.map((rf, i) => (
                <li
                  key={i}
                  className="text-xs text-slate-700 dark:text-slate-300 flex items-start gap-2 bg-amber-50/50 dark:bg-amber-950/20 p-2.5 rounded-xl border border-amber-200/60 dark:border-amber-900/30"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                  <span>{rf}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Policy Reference */}
        {policyBasis && (
          <div className="pt-2">
            <div className="p-3.5 rounded-2xl bg-brand-50/60 dark:bg-brand-950/30 border border-brand-100 dark:border-brand-900/40 flex items-start gap-2.5 text-xs text-brand-900 dark:text-brand-200">
              <BookOpen className="w-4 h-4 text-brand-600 dark:text-brand-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Governing Policy Basis: </span>
                <span>{policyBasis}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DecisionExplanation;
