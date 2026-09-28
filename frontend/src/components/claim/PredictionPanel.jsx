import React from 'react';
import { Cpu, Brain, ShieldAlert, CheckCircle2, AlertTriangle, Sparkles } from 'lucide-react';
import { formatPercent } from '../../utils/formatters';
import Badge from '../common/Badge';

export const PredictionPanel = ({
  pythonML = { name: 'Python Classification Model', decision: 'Valid Claim', confidence: null, fraudRisk: null },
  teachableMachine = { name: 'Google Teachable Machine Model', decision: 'Valid Claim', confidence: null, category: 'Hardware Defect' },
  aiConfidence = null,
  fraudScore = null,
}) => {
  const mlConf = pythonML?.confidence ?? aiConfidence;
  const tmConf = teachableMachine?.confidence;
  const fraud = fraudScore !== null && fraudScore !== undefined ? fraudScore : (pythonML?.fraudRisk ?? 0.0);

  return (
    <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Model Predictions and Confidence Scores
            </h3>
            <p className="text-xs text-slate-500">
              Python Classification Model & Google Teachable Machine Model
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge type="decision" value={pythonML?.decision || 'APPROVE'} size="md" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Model 1: Python Classification Model */}
        <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/60 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="w-4 h-4 text-brand-600 dark:text-brand-400" />
              <span className="text-xs font-bold text-slate-900 dark:text-white">
                Python Classification Model
              </span>
            </div>
            <span className="text-xs font-mono font-bold text-brand-600 dark:text-brand-400">
              {mlConf !== null && mlConf !== undefined ? formatPercent(mlConf) : '—'}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-slate-200 dark:bg-slate-700 h-2.5 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                mlConf >= 0.8
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                  : mlConf >= 0.6
                  ? 'bg-gradient-to-r from-blue-500 to-brand-400'
                  : mlConf !== null && mlConf !== undefined ? 'bg-gradient-to-r from-amber-500 to-rose-500' : 'bg-transparent'
              }`}
              style={{ width: `${mlConf !== null && mlConf !== undefined ? Math.min(100, Math.max(0, mlConf * 100)) : 0}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 pt-1">
            <span>Decision: <strong className="text-slate-700 dark:text-slate-200">{pythonML?.decision || 'APPROVE'}</strong></span>
          </div>
        </div>

        {/* Google Teachable Machine Model */}
        <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/60 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-brand-600 dark:text-brand-400" />
              <span className="text-xs font-bold text-slate-900 dark:text-white">
                Google Teachable Machine Model
              </span>
            </div>
            <span className="text-xs font-mono font-bold text-brand-600 dark:text-brand-400">
              {tmConf !== null && tmConf !== undefined ? formatPercent(tmConf) : '—'}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-slate-200 dark:bg-slate-700 h-2.5 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                tmConf >= 0.8
                  ? 'bg-gradient-to-r from-brand-500 to-cyan-400'
                  : tmConf >= 0.6
                  ? 'bg-gradient-to-r from-blue-500 to-amber-400'
                  : tmConf !== null && tmConf !== undefined ? 'bg-gradient-to-r from-amber-500 to-rose-500' : 'bg-transparent'
              }`}
              style={{ width: `${tmConf !== null && tmConf !== undefined ? Math.min(100, Math.max(0, tmConf * 100)) : 0}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 pt-1">
            <span>Visual Defect: <strong className="text-slate-700 dark:text-slate-200">{teachableMachine?.category || 'Hardware Defect'}</strong></span>
          </div>
        </div>

      </div>

      {/* Fraud Risk Indicator Bar */}
      <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 flex flex-col sm:flex-row items-center justify-between gap-4 border border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Anomaly & Fraud Probability Score
            </p>
            <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">
              {fraud < 0.2 ? 'Low Risk (Clean Verification)' : fraud < 0.6 ? 'Moderate Risk (Requires Review)' : 'High Risk Alert (Audit Required)'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-48">
          <div className="flex-1 bg-slate-200 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
            <div
              className={`h-full ${
                fraud < 0.2 ? 'bg-emerald-500' : fraud < 0.6 ? 'bg-amber-500' : 'bg-rose-500'
              }`}
              style={{ width: `${fraud * 100}%` }}
            />
          </div>
          <span className="text-xs font-mono font-bold text-slate-700 dark:text-slate-300">
            {formatPercent(fraud)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default PredictionPanel;
