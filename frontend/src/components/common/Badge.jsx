import React from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  ShieldCheck, 
  ShieldAlert, 
  HelpCircle,
  FileCheck2,
  Sparkles
} from 'lucide-react';

export const Badge = ({ 
  type = 'status', // 'status', 'decision', 'category', 'fraud', 'comparison'
  value, 
  size = 'md', // 'sm', 'md', 'lg'
  showIcon = true,
  className = '' 
}) => {
  if (!value) return null;

  const normalizedVal = String(value).toUpperCase();

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 font-medium gap-1',
    md: 'text-xs px-2.5 py-1 font-semibold gap-1.5',
    lg: 'text-sm px-3.5 py-1.5 font-semibold gap-2',
  }[size] || 'text-xs px-2.5 py-1 font-semibold gap-1.5';

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  }[size] || 'w-3.5 h-3.5';

  let styleClasses = 'bg-slate-100 text-slate-700 border border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700';
  let IconComponent = null;

  if (type === 'status') {
    switch (normalizedVal) {
      case 'APPROVED':
      case 'ACTIVE':
      case 'RESOLVED':
        styleClasses = 'bg-[#A1CCA5]/30 text-[#097C87] border border-[#A1CCA5] dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800';
        IconComponent = CheckCircle2;
        break;
      case 'REJECTED':
      case 'EXPIRED':
      case 'VOIDED':
        styleClasses = 'bg-[#FCA47C]/30 text-[#097C87] border border-[#FCA47C] dark:bg-rose-950/50 dark:text-rose-300 dark:border-rose-800';
        IconComponent = XCircle;
        break;
      case 'UNDER_REVIEW':
      case 'PENDING':
      case 'MANUAL_REVIEW':
        styleClasses = 'bg-[#F9D779]/40 text-[#097C87] border border-[#F9D779] dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800';
        IconComponent = Clock;
        break;
      case 'ESCALATED':
        styleClasses = 'bg-[#097C87]/10 text-[#097C87] border border-[#097C87] dark:bg-purple-950/50 dark:text-purple-300 dark:border-purple-800';
        IconComponent = AlertTriangle;
        break;
      case 'SUBMITTED':
      case 'CLAIMED':
      default:
        styleClasses = 'bg-[#23CED9]/20 text-[#097C87] border border-[#23CED9] dark:bg-blue-950/50 dark:text-blue-300 dark:border-blue-800';
        IconComponent = FileCheck2;
        break;
    }
  }

  if (type === 'decision') {
    switch (normalizedVal) {
      case 'APPROVE':
        styleClasses = 'bg-[#A1CCA5]/30 text-[#097C87] border border-[#A1CCA5] dark:bg-emerald-900/60 dark:text-emerald-200 dark:border-emerald-700';
        IconComponent = ShieldCheck;
        break;
      case 'REJECT':
        styleClasses = 'bg-[#FCA47C]/30 text-[#097C87] border border-[#FCA47C] dark:bg-rose-900/60 dark:text-rose-200 dark:border-rose-700';
        IconComponent = ShieldAlert;
        break;
      case 'MANUAL_REVIEW':
        styleClasses = 'bg-[#F9D779]/40 text-[#097C87] border border-[#F9D779] dark:bg-amber-900/60 dark:text-amber-200 dark:border-amber-700';
        IconComponent = Clock;
        break;
      case 'ESCALATE':
        styleClasses = 'bg-[#097C87]/10 text-[#097C87] border border-[#097C87] dark:bg-purple-900/60 dark:text-purple-200 dark:border-purple-700';
        IconComponent = AlertTriangle;
        break;
      default:
        styleClasses = 'bg-slate-100 text-slate-700 border border-slate-300 dark:bg-slate-800 dark:text-slate-300';
        IconComponent = Sparkles;
    }
  }

  if (type === 'comparison') {
    switch (normalizedVal) {
      case 'STRONG_MATCH':
      case 'STRONG MATCH':
        styleClasses = 'bg-[#A1CCA5]/30 text-[#097C87] border border-[#A1CCA5] dark:bg-emerald-950 dark:text-emerald-300';
        IconComponent = CheckCircle2;
        break;
      case 'ACCEPTABLE':
      case 'ACCEPTABLE DELTA':
        styleClasses = 'bg-[#23CED9]/20 text-[#097C87] border border-[#23CED9] dark:bg-blue-950 dark:text-blue-300';
        IconComponent = CheckCircle2;
        break;
      case 'WEAK':
      case 'WEAK MATCH':
        styleClasses = 'bg-[#F9D779]/40 text-[#097C87] border border-[#F9D779] dark:bg-amber-950 dark:text-amber-300';
        IconComponent = AlertTriangle;
        break;
      case 'DISAGREEMENT':
      case 'MODEL DISAGREEMENT':
        styleClasses = 'bg-[#FCA47C]/30 text-[#097C87] border border-[#FCA47C] dark:bg-rose-950 dark:text-rose-300';
        IconComponent = XCircle;
        break;
    }
  }

  if (type === 'fraud') {
    const score = Number(value);
    if (score >= 0.7) {
      styleClasses = 'bg-[#FCA47C]/30 text-[#097C87] border border-[#FCA47C] dark:bg-rose-950 dark:text-rose-200';
      IconComponent = ShieldAlert;
    } else if (score >= 0.3) {
      styleClasses = 'bg-[#F9D779]/40 text-[#097C87] border border-[#F9D779] dark:bg-amber-950 dark:text-amber-200';
      IconComponent = AlertTriangle;
    } else {
      styleClasses = 'bg-[#A1CCA5]/30 text-[#097C87] border border-[#A1CCA5] dark:bg-emerald-950 dark:text-emerald-200';
      IconComponent = ShieldCheck;
    }
  }

  return (
    <span
      className={`inline-flex items-center rounded-full tracking-wide transition-colors ${sizeClasses} ${styleClasses} ${className}`}
    >
      {showIcon && IconComponent && <IconComponent className={iconSizes} />}
      <span>{String(value).replace(/_/g, ' ')}</span>
    </span>
  );
};

export default Badge;

