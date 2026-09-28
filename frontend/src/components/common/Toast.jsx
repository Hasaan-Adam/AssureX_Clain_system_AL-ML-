import React from 'react';
import { useNotification } from '../../context/NotificationContext';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

export const Toast = () => {
  const { toasts, removeToast } = useNotification();

  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => {
        const { id, type, message } = toast;

        let icon = <Info className="w-5 h-5 text-blue-500" />;
        let borderClasses = 'border-blue-200 dark:border-blue-900 bg-white dark:bg-slate-900';

        if (type === 'success') {
          icon = <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
          borderClasses = 'border-emerald-200 dark:border-emerald-900 bg-white dark:bg-slate-900';
        } else if (type === 'error') {
          icon = <AlertCircle className="w-5 h-5 text-rose-500" />;
          borderClasses = 'border-rose-200 dark:border-rose-900 bg-white dark:bg-slate-900';
        } else if (type === 'warning') {
          icon = <AlertTriangle className="w-5 h-5 text-amber-500" />;
          borderClasses = 'border-amber-200 dark:border-amber-900 bg-white dark:bg-slate-900';
        }

        return (
          <div
            key={id}
            className={`pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-xl border ${borderClasses} animate-slide-up transition-all`}
          >
            <div className="shrink-0 pt-0.5">{icon}</div>
            <div className="flex-1 text-sm text-slate-800 dark:text-slate-200 font-medium">
              {message}
            </div>
            <button
              type="button"
              onClick={() => removeToast(id)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 p-0.5"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
};

export default Toast;