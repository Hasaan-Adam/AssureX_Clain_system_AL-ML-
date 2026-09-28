import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import Toast from './components/common/Toast';
import Modal from './components/common/Modal';
import ErrorBoundary from './components/common/ErrorBoundary';
import { useNotification } from './context/NotificationContext';
import { useAuth } from './context/AuthContext';
import AppRoutes from './routes';
import { ShieldAlert, Calendar } from 'lucide-react';
import { formatDate } from './utils/formatters';

export const App = () => {
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const { isAlertModalOpen, closeWarrantyAlerts, warrantyAlerts } = useNotification();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isStandalone =
    location.pathname === '/' ||
    location.pathname === '/login' ||
    location.pathname === '/register';

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors duration-200 selection:bg-brand-500 selection:text-white">
      {/* Toast Notifications Layer */}
      <Toast />

      {/* Warranty Expiration Alerts Popup Modal */}
      <Modal
        isOpen={isAlertModalOpen}
        onClose={closeWarrantyAlerts}
        title="Warranty Expiration Alerts"
      >
        <div className="space-y-4">
          <div className="p-3.5 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 flex items-start gap-2.5">
            <ShieldAlert className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-900 dark:text-amber-200">
              The following products have warranties expiring soon. File a claim or request extended coverage prior to expiration.
            </div>
          </div>

          <div className="space-y-2">
            {warrantyAlerts.map((w) => (
              <div
                key={w.id}
                className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex items-center justify-between text-xs"
              >
                <div>
                  <p className="font-semibold text-slate-900 dark:text-white">
                    {w.product?.brand} {w.product?.model_name || 'Equipment'}
                  </p>
                  <p className="text-[11px] text-slate-400 font-mono">
                    SN: {w.serial_number}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-amber-600 font-bold">
                    Expires {formatDate(w.expiry_date)}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="button"
              onClick={closeWarrantyAlerts}
              className="px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold rounded-xl"
            >
              Acknowledge
            </button>
          </div>
        </div>
      </Modal>

      {/* Conditional Layout */}
      {isStandalone ? (
        <main className="flex-1">
          <AppRoutes />
        </main>
      ) : (
        <div className="h-screen flex w-full overflow-hidden bg-slate-50">
          {/* Sidebar - Full Height Left */}
          {isAuthenticated && (
            <Sidebar
              isOpen={sidebarOpen}
              onClose={() => setSidebarOpen(false)}
            />
          )}

          {/* Main Content - Right Side */}
          <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
            <Navbar
              onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
              isSidebarOpen={sidebarOpen}
            />
            <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-full">
              <AppRoutes />
            </main>
          </div>
        </div>
      )}
    </div>
    </ErrorBoundary>
  );
};

export default App;
