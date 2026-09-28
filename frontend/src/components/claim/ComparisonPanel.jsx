import React from 'react';
import { GitCompare, CheckCircle2, AlertTriangle, XCircle, ArrowRightLeft, ShieldAlert } from 'lucide-react';
import { formatPercent } from '../../utils/formatters';
import Badge from '../common/Badge';

export const ComparisonPanel = ({
  pythonMLScore = null,
  teachableMachineScore = null,
  agreementScore = null,
  comparisonCategory = 'Strong Match', // 'Strong Match', 'Acceptable', 'Weak', 'Disagreement'
}) => {
  const hasScores = pythonMLScore !== null && teachableMachineScore !== null;
  const delta = hasScores ? Math.abs(pythonMLScore - teachableMachineScore) : 0.0;

  let badgeType = comparisonCategory || 'Strong Match';
  let badgeColor = 'bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-950/60 dark:text-emerald-300';
  let adviceText = 'High confidence consensus reached between tabular ML model and visual classification model. Auto-adjudication eligible.';

  if (!hasScores) {
    badgeType = 'Evaluating Models';
    badgeColor = 'bg-slate-50 text-slate-700 border-slate-300 dark:bg-slate-950/60 dark:text-slate-300';
    adviceText = 'Multi-model consensus evaluation is computing live inferences for this claim.';
  } else if (delta > 0.35 || comparisonCategory === 'Disagreement') {
    badgeType = 'Model Disagreement';
    badgeColor = 'bg-rose-50 text-rose-700 border-rose-300 dark:bg-rose-950/60 dark:text-rose-300';
    adviceText = 'Significant delta between tabular ML and computer vision models. Automatic routing triggered to Human Adjudication Queue.';
  } else if (delta > 0.20 || comparisonCategory === 'Weak') {
    badgeType = 'Weak Match';
    badgeColor = 'bg-amber-50 text-amber-700 border-amber-300 dark:bg-amber-950/60 dark:text-amber-300';
    adviceText = 'Moderate score divergence detected. Secondary rule checks and supervisor sign-off recommended.';
  } else if (delta > 0.10 || comparisonCategory === 'Acceptable') {
    badgeType = 'Acceptable Delta';
    badgeColor = 'bg-blue-50 text-blue-700 border-blue-300 dark:bg-blue-950/60 dark:text-blue-300';
    adviceText = 'Minor divergence within acceptable operational bounds. Standard policy rules applied.';
  }

  return (
    <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400">
            <ArrowRightLeft className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Model Prediction and Confidence Comparison
            </h3>
            <p className="text-xs text-slate-500">
              Python Classification Model & Google Teachable Machine Model
            </p>
          </div>
        </div>

        <Badge type="comparison" value={badgeType} size="md" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* ML Score */}
        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 text-center">
          <p className="text-xs font-semibold text-slate-500 dark:text-slate-400">
            Python Classification Model
          </p>
          <p className="text-2xl font-extrabold text-slate-900 dark:text-white mt-1">
            {formatPercent(pythonMLScore)}
          </p>
          <span className="text-[10px] font-medium text-slate-400">Confidence Score</span>
        </div>

        {/* Delta Gauge */}
        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 text-center">
          <p className="text-xs font-semibold text-slate-500 dark:text-slate-400">
            Confidence Difference
          </p>
          <p className="text-2xl font-extrabold text-brand-600 dark:text-brand-400 mt-1">
            {formatPercent(delta)}
          </p>
          <span className="text-[10px] font-medium text-slate-400">
            Model Consistency Status: {formatPercent(agreementScore)}
          </span>
        </div>

        {/* TM Score */}
        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 text-center">
          <p className="text-xs font-semibold text-slate-500 dark:text-slate-400">
            Google Teachable Machine Model
          </p>
          <p className="text-2xl font-extrabold text-brand-600 dark:text-brand-400 mt-1">
            {formatPercent(teachableMachineScore)}
          </p>
          <span className="text-[10px] font-medium text-slate-400">Confidence Score</span>
        </div>
      </div>

      {/* Consensus Insight Callout */}
      <div className={`p-4 rounded-2xl border text-xs leading-relaxed ${badgeColor}`}>
        <div className="flex items-start gap-2.5">
          <GitCompare className="w-4 h-4 shrink-0 mt-0.5" />
          <div>
            <strong className="font-bold">Adjudication Engine Routing Analysis: </strong>
            <span>{adviceText}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonPanel;
