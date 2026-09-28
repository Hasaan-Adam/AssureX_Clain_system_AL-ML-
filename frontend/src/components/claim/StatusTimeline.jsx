import React from 'react';
import { Check, Clock, AlertTriangle, X, ShieldCheck, FileText, Cpu, CheckCircle, User } from 'lucide-react';
import { formatDateTime } from '../../utils/formatters';

/* ─── helpers ──────────────────────────────────────── */
const fmtRelTime = (ts) => {
  if (!ts) return '';
  try {
    const d = new Date(ts);
    const diff = Date.now() - d.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  } catch { return ''; }
};

/* ─── status step config ───────────────────────────── */
const STEPS = [
  { key: 'submitted',   label: 'Claim Submitted',           icon: FileText    },
  { key: 'under_review',label: 'AI Adjudication & OCR',    icon: Cpu         },
  { key: 'decision',    label: 'Adjudication Decision',     icon: ShieldCheck },
  { key: 'resolved',    label: 'Settlement / Closed',       icon: CheckCircle },
];

const getStepState = (stepIndex, statusNorm) => {
  if (statusNorm === 'rejected') {
    if (stepIndex < 2) return 'completed';
    if (stepIndex === 2) return 'rejected';
    return 'pending';
  }
  if (statusNorm === 'manual_review' || statusNorm === 'escalated') {
    if (stepIndex <= 1) return 'completed';
    if (stepIndex === 2) return 'escalated';
    return 'pending';
  }
  if (statusNorm === 'approved' || statusNorm === 'resolved' || statusNorm === 'closed' || statusNorm === 'settled') {
    return 'completed';
  }
  if (statusNorm === 'under_review') {
    if (stepIndex === 0) return 'completed';
    if (stepIndex === 1) return 'current';
    return 'pending';
  }
  if (stepIndex === 0) return 'completed';
  if (stepIndex === 1) return 'current';
  return 'pending';
};

const circleClasses = {
  completed: 'bg-emerald-500 text-white border-emerald-500 ring-4 ring-emerald-500/20',
  current:   'bg-brand-600 text-white border-brand-600 ring-4 ring-brand-500/20 animate-pulse',
  rejected:  'bg-rose-500 text-white border-rose-500 ring-4 ring-rose-500/20',
  escalated: 'bg-violet-500 text-white border-violet-500 ring-4 ring-violet-500/20',
  pending:   'bg-slate-100 dark:bg-slate-800 text-slate-400 border-slate-300 dark:border-slate-600',
};

const stateLabel = {
  completed: 'Completed',
  current:   'In Progress',
  rejected:  'Rejected',
  escalated: 'Escalated / Manual',
  pending:   'Pending',
};

/* ─── history entry type badge ─────────────────────── */
const HistoryBadge = ({ action }) => {
  const a = (action || '').toLowerCase();
  if (a.includes('approv')) return <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/30 px-2 py-0.5 rounded-full">Approved</span>;
  if (a.includes('reject')) return <span className="text-[10px] font-bold text-rose-700 dark:text-rose-400 bg-rose-50 dark:bg-rose-900/30 px-2 py-0.5 rounded-full">Rejected</span>;
  if (a.includes('review') || a.includes('escalat')) return <span className="text-[10px] font-bold text-violet-700 dark:text-violet-400 bg-violet-50 dark:bg-violet-900/30 px-2 py-0.5 rounded-full">Escalated</span>;
  if (a.includes('submit')) return <span className="text-[10px] font-bold text-brand-700 dark:text-brand-400 bg-brand-50 dark:bg-brand-900/30 px-2 py-0.5 rounded-full">Submitted</span>;
  if (a.includes('ocr') || a.includes('ai')) return <span className="text-[10px] font-bold text-blue-700 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 rounded-full">AI Processed</span>;
  return <span className="text-[10px] font-bold text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full capitalize">{action || 'Update'}</span>;
};

/* ─── main component ───────────────────────────────── */
export const StatusTimeline = ({
  status = 'submitted',
  history = [],
  showHistory = false,
}) => {
  const statusNorm = (status || 'submitted').toLowerCase();

  return (
    <div className="space-y-6">
      {/* ── Lifecycle progress steps ──────────────────── */}
      <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-6">
          Claim Adjudication Lifecycle
        </h3>
        <div className="relative flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          {/* connecting line (desktop) */}
          <div className="hidden md:block absolute top-6 left-6 right-6 h-0.5 bg-slate-200 dark:bg-slate-700 -z-0" />

          {STEPS.map((step, idx) => {
            const state = getStepState(idx, statusNorm);
            const Icon = step.icon;
            return (
              <div key={step.key} className="flex-1 flex items-center gap-4 md:flex-col md:text-center w-full relative z-10">
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center border-2 transition-all shrink-0 ${circleClasses[state]}`}>
                  {state === 'completed' ? <Check className="w-5 h-5" /> : <Icon className="w-5 h-5" />}
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-900 dark:text-white">{step.label}</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">{stateLabel[state]}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── History audit trail (only if showHistory is true or history has items) ── */}
      {showHistory && history.length > 0 && (
        <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
            <Clock className="w-4 h-4 text-brand-500" />
            Audit Trail
            <span className="text-xs font-normal text-slate-400">({history.length} events)</span>
          </h3>
          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-100 dark:bg-slate-800" />
            <div className="space-y-4 pl-10">
              {history.map((entry, i) => (
                <div key={i} className="relative">
                  <div className="absolute -left-6 top-1 w-3 h-3 rounded-full bg-brand-500 border-2 border-white dark:border-slate-900 shadow-sm" />
                  <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-100 dark:border-slate-700">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <HistoryBadge action={entry.action || entry.status || entry.event} />
                        {(entry.actor_name || entry.performed_by || entry.user) && (
                          <span className="inline-flex items-center gap-1 text-[11px] text-slate-500 dark:text-slate-400">
                            <User className="w-3 h-3" />
                            {entry.actor_name || entry.performed_by || entry.user}
                          </span>
                        )}
                      </div>
                      <span className="text-[11px] text-slate-400 shrink-0 font-medium">
                        {fmtRelTime(entry.created_at || entry.timestamp || entry.at)}
                      </span>
                    </div>
                    {(entry.note || entry.description || entry.reason) && (
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">
                        {entry.note || entry.description || entry.reason}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatusTimeline;
