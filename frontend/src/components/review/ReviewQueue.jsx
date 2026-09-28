import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  CheckSquare, ArrowRight, PartyPopper 
} from 'lucide-react';
import { formatDate, formatCurrency, formatPercent } from '../../utils/formatters';

export const ReviewQueue = ({
  queueItems = [],
  onSelectClaim = null,
}) => {
  const navigate = useNavigate();
  const [filter, setFilter] = useState('All');

  const tabs = ['All', 'Pending', 'Escalated', 'Overridden'];

  const filtered = queueItems.filter((item) => {
    if (filter === 'All') return true;
    if (filter === 'Pending') return item.status === 'PENDING' || !item.status;
    if (filter === 'Escalated') return item.fraud_score > 0.5 || item.status === 'ESCALATED';
    if (filter === 'Overridden') return item.status === 'OVERRIDDEN';
    return true;
  });

  const getPriorityColor = (row) => {
    const fraud = row.fraud_score || 0;
    if (fraud > 0.7) return 'border-l-rose-500';
    if (fraud > 0.3) return 'border-l-amber-500';
    return 'border-l-blue-500';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-brand-100 dark:bg-brand-900/50 rounded-xl text-brand-600 dark:text-brand-400">
            <CheckSquare className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              Review Queue
              <span className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 text-sm py-0.5 px-2.5 rounded-full font-semibold">
                {filtered.length}
              </span>
            </h2>
          </div>
        </div>
        
        <div className="flex items-center p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
          {tabs.map(tab => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`px-4 py-1.5 text-sm font-semibold rounded-lg transition-all ${
                filter === tab 
                  ? 'bg-white dark:bg-slate-900 text-brand-600 dark:text-brand-400 shadow-sm' 
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="w-16 h-16 bg-emerald-100 dark:bg-emerald-900/50 text-emerald-600 dark:text-emerald-400 rounded-full flex items-center justify-center mb-4">
            <PartyPopper className="w-8 h-8" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">All caught up!</h3>
          <p className="text-slate-500 dark:text-slate-400">There are no claims pending your review.</p>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800 text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">
                  <th className="p-4 pl-6">Claim Details</th>
                  <th className="p-4">Fault & Product</th>
                  <th className="p-4">Amount</th>
                  <th className="p-4">AI Decision</th>
                  <th className="p-4 text-right pr-6">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {filtered.map((row, i) => (
                  <tr 
                    key={row.id || i} 
                    className={`hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors border-l-4 ${getPriorityColor(row)}`}
                  >
                    <td className="p-4 pl-5">
                      <div className="font-semibold text-slate-900 dark:text-white text-sm">
                        {row.claim_number}
                      </div>
                      <div className="text-xs text-slate-500">
                        {row.user?.full_name || 'Customer'} • {formatDate(row.submitted_at || row.created_at)}
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="text-sm font-medium text-slate-900 dark:text-white">
                        {row.fault_type || 'Unknown'}
                      </div>
                      <div className="text-xs text-slate-500">
                        {row.warranty?.product?.brand} {row.warranty?.product?.model_name || 'Device'}
                      </div>
                    </td>
                    <td className="p-4 font-bold text-slate-900 dark:text-white text-sm">
                      {formatCurrency(row.claim_amount)}
                    </td>
                    <td className="p-4">
                      <div className="flex flex-col gap-1 items-start">
                        {row.ai_decision && (
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold ${
                            row.ai_decision.includes('Valid')
                              ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                              : row.ai_decision.includes('Invalid')
                              ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                              : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                          }`}>
                            {row.ai_decision}
                          </span>
                        )}
                        <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                          {row.ai_confidence ? `${(row.ai_confidence * 100).toFixed(1)}% ML Conf.` : 'Pending Analysis'}
                        </span>
                      </div>
                    </td>

                    <td className="p-4 pr-6">
                      <div className="flex items-center justify-end">
                        <button
                          onClick={() => onSelectClaim ? onSelectClaim(row) : navigate(`/claims/${row.id}`)}
                          className="flex items-center gap-1.5 px-3 py-1.5 bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold rounded-lg shadow-sm transition-all"
                        >
                          Review
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReviewQueue;