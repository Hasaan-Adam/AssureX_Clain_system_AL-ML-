import React from 'react';
import { CheckCircle2, XCircle, AlertCircle, ShieldAlert, FileCheck } from 'lucide-react';

export const RuleResultPanel = ({
  rules = [],
}) => {
  const passedCount = rules.filter((r) => r.passed).length;
  const totalCount = rules.length;
  const allPassed = passedCount === totalCount;

  return (
    <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
            <FileCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Warranty Rule Validation
            </h3>
            <p className="text-xs text-slate-500">
              Deterministic Rules & Warranty Rule Validation
            </p>
          </div>
        </div>

        <div className="text-xs font-bold px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          {passedCount} of {totalCount} Rules Passed
        </div>
      </div>

      {rules.length === 0 ? (
        <div className="p-8 text-center">
          <FileCheck className="w-10 h-10 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
          <p className="text-sm font-semibold text-slate-500">Rule evaluation pending</p>
          <p className="text-xs text-slate-400 mt-1">Rules will appear after AI adjudication completes</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {rules.map((rule) => (
            <div
              key={rule.id}
              className={`p-3.5 rounded-2xl border transition-all flex items-start gap-3 ${
                rule.passed
                  ? 'bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-200/80 dark:border-emerald-900/40'
                  : 'bg-rose-50/40 dark:bg-rose-950/20 border-rose-200/80 dark:border-rose-900/40'
              }`}
            >
              <div className="shrink-0 mt-0.5">
                {rule.passed ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                ) : (
                  <XCircle className="w-5 h-5 text-rose-600 dark:text-rose-400" />
                )}
              </div>
              <div className="flex-1">
                <p className="text-xs font-bold text-slate-900 dark:text-white">
                  {rule.name}
                </p>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                  {rule.details}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RuleResultPanel;