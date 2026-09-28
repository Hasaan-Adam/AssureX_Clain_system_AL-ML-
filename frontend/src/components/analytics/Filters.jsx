import React from 'react';
import { Filter, Calendar, Layers, CheckCircle } from 'lucide-react';
import { PRODUCT_CATEGORIES } from '../../utils/constants';

export const Filters = ({
  timeRange = '30d',
  onTimeRangeChange,
  category = 'ALL',
  onCategoryChange,
  decision = 'ALL',
  onDecisionChange,
}) => {
  return (
    <div className="p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-2 text-xs font-bold text-slate-700 dark:text-slate-300">
        <Filter className="w-4 h-4 text-brand-600" />
        <span>Analytics Filter Matrix</span>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        {/* Time Range Filter */}
        <div className="flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={timeRange}
            onChange={(e) => onTimeRangeChange && onTimeRangeChange(e.target.value)}
            className="text-xs font-semibold px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none dark:text-white"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last 1 Year</option>
          </select>
        </div>

        {/* Category Filter */}
        <div className="flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={category}
            onChange={(e) => onCategoryChange && onCategoryChange(e.target.value)}
            className="text-xs font-semibold px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none dark:text-white"
          >
            <option value="ALL">All Categories</option>
            {PRODUCT_CATEGORIES.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>

        {/* Decision Filter */}
        <div className="flex items-center gap-1.5">
          <CheckCircle className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={decision}
            onChange={(e) => onDecisionChange && onDecisionChange(e.target.value)}
            className="text-xs font-semibold px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none dark:text-white"
          >
            <option value="ALL">All Decisions</option>
            <option value="APPROVE">Approved</option>
            <option value="REJECT">Rejected</option>
            <option value="MANUAL_REVIEW">Manual Review</option>
            <option value="ESCALATE">Escalated</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default Filters;