import React from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  FileText, 
  CheckCircle2, 
  Clock, 
  ShieldAlert, 
  ShieldCheck, 
  DollarSign, 
  Cpu 
} from 'lucide-react';
import { formatCurrency, formatPercent } from '../../utils/formatters';

export const StatCard = ({
  title,
  value,
  subtitle,
  icon: Icon = FileText,
  change = null, // e.g. +12.4%
  isPositive = true,
  colorScheme = 'brand', // 'brand', 'emerald', 'amber', 'rose', 'brand'
}) => {
  const colorMap = {
    brand: { bg: 'bg-[#23CED9]/20', text: 'text-[#097C87]', border: 'border-[#23CED9]' },
    emerald: { bg: 'bg-[#A1CCA5]/20', text: 'text-[#097C87]', border: 'border-[#A1CCA5]' },
    amber: { bg: 'bg-[#F9D779]/30', text: 'text-[#097C87]', border: 'border-[#F9D779]' },
    rose: { bg: 'bg-[#FCA47C]/30', text: 'text-[#097C87]', border: 'border-[#FCA47C]' },
    brand: { bg: 'bg-[#23CED9]/20', text: 'text-[#097C87]', border: 'border-[#23CED9]' },
  }[colorScheme] || {
    bg: 'bg-brand-50 bg-[#23CED9]/20',
    text: 'text-brand-600 text-[#097C87]',
    border: 'border-brand-100 border-[#23CED9]',
  };

  return (
    <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
            {title}
          </p>
          <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white mt-1">
            {value}
          </h3>
        </div>

        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center border ${colorMap.bg} ${colorMap.text} ${colorMap.border}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
        <span className="text-slate-500 dark:text-slate-400">{subtitle}</span>
        {change !== null && (
          <span
            className={`flex items-center gap-0.5 font-bold ${
              isPositive ? 'text-[#A1CCA5] dark:text-emerald-400' : 'text-[#FCA47C] dark:text-rose-400'
            }`}
          >
            {isPositive ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
            {change}
          </span>
        )}
      </div>
    </div>
  );
};

export const StatCards = ({ stats = {} }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total Adjudicated Claims"
        value={stats.total_claims ?? '—'}
        subtitle="Across all channels"
        icon={FileText}
        change="+14.2%"
        isPositive={true}
        colorScheme="brand"
      />

      <StatCard
        title="AI Auto-Approval Rate"
        value={stats.auto_approval_rate ? formatPercent(stats.auto_approval_rate) : '—'}
        subtitle="Confidence >= 85%"
        icon={ShieldCheck}
        change="+3.1%"
        isPositive={true}
        colorScheme="emerald"
      />

      <StatCard
        title="Pending Manual Review"
        value={stats.pending_reviews ?? '—'}
        subtitle="Avg SLA: 2.4 hrs"
        icon={Clock}
        change="-8.5%"
        isPositive={true}
        colorScheme="amber"
      />

      <StatCard
        title="Disbursed Value"
        value={stats.disbursed_value ? formatCurrency(stats.disbursed_value) : '—'}
        subtitle="Current fiscal cycle"
        icon={DollarSign}
        change="+18.7%"
        isPositive={true}
        colorScheme="brand"
      />
    </div>
  );
};

export default StatCards;

