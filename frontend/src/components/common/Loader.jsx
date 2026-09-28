import React from 'react';
import { Loader2, Sparkles } from 'lucide-react';

export const Loader = ({ 
  size = 'md', // 'sm', 'md', 'lg', 'full'
  text = 'Loading...', 
  isFullPage = false,
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4 text-brand-600',
    md: 'w-8 h-8 text-brand-600',
    lg: 'w-12 h-12 text-brand-600',
  }[size] || 'w-8 h-8 text-brand-600';

  const spinnerContent = (
    <div className={`flex flex-col items-center justify-center p-6 gap-3 ${className}`}>
      <div className="relative flex items-center justify-center">
        <Loader2 className={`animate-spin ${sizeClasses}`} />
        <Sparkles className="w-3 h-3 text-brand-400 absolute animate-ping" />
      </div>
      {text && (
        <p className="text-sm font-medium text-slate-600 dark:text-slate-400 animate-pulse">
          {text}
        </p>
      )}
    </div>
  );

  if (isFullPage) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm">
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-8 shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col items-center max-w-xs text-center">
          <Loader2 className="w-12 h-12 text-brand-500 animate-spin mb-3" />
          <h4 className="text-base font-semibold text-slate-900 dark:text-white mb-1">
            AssureX Engine
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400">{text}</p>
        </div>
      </div>
    );
  }

  return spinnerContent;
};

export const SkeletonLoader = ({ count = 3, className = 'h-12 w-full' }) => {
  return (
    <div className="space-y-3 w-full animate-pulse">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`bg-slate-200 dark:bg-slate-800 rounded-lg ${className}`}
        />
      ))}
    </div>
  );
};

export default Loader;