import React, { useState } from 'react';
import Modal from '../common/Modal';
import { ShieldAlert, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';
import Loader from '../common/Loader';

export const OverrideModal = ({
  isOpen,
  onClose,
  onConfirmOverride,
  currentDecision = 'REJECT',
  claimNumber = 'CLM-2026-0001',
  loading = false,
}) => {
  const [newDecision, setNewDecision] = useState('APPROVE');
  const [justification, setJustification] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!justification || justification.trim().length < 15) {
      setError('A comprehensive justification (at least 15 characters) is mandatory to override an automated AI decision.');
      return;
    }
    setError('');
    onConfirmOverride({
      decision: newDecision,
      justification: justification.trim(),
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Override Automated AI Decision"
      maxWidth="max-w-lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="p-3.5 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 flex items-start gap-2.5">
          <ShieldAlert className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
          <div className="text-xs text-amber-900 dark:text-amber-200">
            <span className="font-bold">Supervisory Audit Notice:</span> Manual overrides are permanently recorded in the system audit log and reportable under compliance policies.
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Claim Reference
          </label>
          <div className="font-mono text-xs font-bold text-slate-900 dark:text-white p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800">
            {claimNumber} (Current AI Result: {currentDecision})
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            New Adjudication Decision *
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setNewDecision('APPROVE')}
              className={`p-3 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 transition-all ${
                newDecision === 'APPROVE'
                  ? 'bg-emerald-500 text-white border-emerald-500 shadow-md shadow-emerald-500/20'
                  : 'bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300'
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Override: APPROVE</span>
            </button>

            <button
              type="button"
              onClick={() => setNewDecision('REJECT')}
              className={`p-3 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 transition-all ${
                newDecision === 'REJECT'
                  ? 'bg-rose-500 text-white border-rose-500 shadow-md shadow-rose-500/20'
                  : 'bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300'
              }`}
            >
              <XCircle className="w-4 h-4" />
              <span>Override: REJECT</span>
            </button>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Mandatory Override Justification & Reasoning *
          </label>
          <textarea
            rows={4}
            required
            value={justification}
            onChange={(e) => {
              setJustification(e.target.value);
              setError('');
            }}
            placeholder="State policy clause, secondary inspection results, or customer goodwill basis justifying this override..."
            className="w-full px-3.5 py-2 text-xs bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
          />
          {error && <p className="text-xs text-rose-500 mt-1">{error}</p>}
        </div>

        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-500 disabled:opacity-50 rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center gap-2"
          >
            {loading && <Loader size="sm" text="" />}
            <span>Sign & Record Override</span>
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default OverrideModal;