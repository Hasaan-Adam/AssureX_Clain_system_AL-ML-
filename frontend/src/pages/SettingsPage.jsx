import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import { Settings, Sliders, Shield, Bell, Save } from 'lucide-react';
import Loader from '../components/common/Loader';
import adminAPI from '../api/adminAPI';

export const SettingsPage = () => {
  const { user, isAdmin } = useAuth();
  const { toastSuccess, toastError } = useNotification();
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const defaultThresholds = {
    autoApprovalMinConfidence: 0.85,
    maxFraudRiskScore: 0.15,
    maxClaimAmountRatio: 0.75,
    ocrFuzzyMatchThreshold: 0.85,
    emailAlertsEnabled: true,
    inAppAlertsEnabled: true,
    warrantyExpiryAlertDays: 30,
  };

  const [thresholds, setThresholds] = useState(defaultThresholds);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await adminAPI.getSettings();
        const settingsList = response.data?.settings || response.data || [];
        if (Array.isArray(settingsList)) {
          const mapped = { ...defaultThresholds };
          settingsList.forEach((item) => {
            if (item.key && item.value !== undefined) {
              mapped[item.key] = item.value;
            }
          });
          setThresholds(mapped);
        } else if (typeof response.data === 'object' && response.data !== null) {
          setThresholds({ ...defaultThresholds, ...response.data });
        }
      } catch (error) {
        toastError('Failed to load settings');
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, [toastError]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await Promise.all(
        Object.entries(thresholds).map(([key, value]) => adminAPI.updateSetting(key, value))
      );
      toastSuccess('Engine threshold parameters updated successfully.');
    } catch (error) {
      toastError('Failed to update settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <Loader isFullPage text="Loading settings..." />;
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white flex items-center gap-2.5">
          <Settings className="w-6 h-6 text-brand-600" />
          <span>System & Adjudication Settings</span>
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Configure automated approval thresholds, OCR fuzziness tolerance, and notification channels
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Thresholds Card */}
        <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Sliders className="w-5 h-5 text-brand-500" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              AI Decision Rule Thresholds
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Auto-Approval Min Confidence (0.0 - 1.0)
              </label>
              <input
                type="number"
                step="0.01"
                min="0.5"
                max="1.0"
                disabled={!isAdmin}
                value={thresholds.autoApprovalMinConfidence}
                onChange={(e) =>
                  setThresholds({
                    ...thresholds,
                    autoApprovalMinConfidence: parseFloat(e.target.value),
                  })
                }
                className="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none dark:text-white disabled:opacity-60"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Max Allowed Fraud Risk Score (0.0 - 1.0)
              </label>
              <input
                type="number"
                step="0.01"
                min="0.0"
                max="0.5"
                disabled={!isAdmin}
                value={thresholds.maxFraudRiskScore}
                onChange={(e) =>
                  setThresholds({
                    ...thresholds,
                    maxFraudRiskScore: parseFloat(e.target.value),
                  })
                }
                className="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none dark:text-white disabled:opacity-60"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Max Claim Amount / MSRP Ratio
              </label>
              <input
                type="number"
                step="0.01"
                min="0.1"
                max="1.0"
                disabled={!isAdmin}
                value={thresholds.maxClaimAmountRatio}
                onChange={(e) =>
                  setThresholds({
                    ...thresholds,
                    maxClaimAmountRatio: parseFloat(e.target.value),
                  })
                }
                className="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none dark:text-white disabled:opacity-60"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                OCR Serial Fuzzy Match Tolerance
              </label>
              <input
                type="number"
                step="0.01"
                min="0.5"
                max="1.0"
                disabled={!isAdmin}
                value={thresholds.ocrFuzzyMatchThreshold}
                onChange={(e) =>
                  setThresholds({
                    ...thresholds,
                    ocrFuzzyMatchThreshold: parseFloat(e.target.value),
                  })
                }
                className="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none dark:text-white disabled:opacity-60"
              />
            </div>
            
            {/* New Warranty Expiry Settings */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  Warranty Expiry Alert Threshold (Days)
                </label>
                <span className="text-xs font-bold text-brand-600 dark:text-brand-400">
                  {thresholds.warrantyExpiryAlertDays} Days
                </span>
              </div>
              <p className="text-[10px] text-slate-500 mb-2">
                Generate automated alerts when a warranty is within this many days of expiration.
              </p>
              <input
                type="range"
                className="w-full accent-brand-600 cursor-pointer"
                min="7"
                max="90"
                step="1"
                disabled={!isAdmin}
                value={thresholds.warrantyExpiryAlertDays}
                onChange={(e) =>
                  setThresholds({
                    ...thresholds,
                    warrantyExpiryAlertDays: parseInt(e.target.value, 10),
                  })
                }
              />
            </div>
            
          </div>
        </div>

        {/* Notifications & Channels */}
        <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Bell className="w-5 h-5 text-brand-500" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              Notification & Alert Channels
            </h3>
          </div>

          <div className="space-y-3">
            <label className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 text-xs font-semibold cursor-pointer">
              <span className="text-slate-700 dark:text-slate-300">
                In-App Warranty Expiry Reminders (30d, 15d, 7d alerts)
              </span>
              <input
                type="checkbox"
                checked={thresholds.inAppAlertsEnabled}
                onChange={(e) =>
                  setThresholds({ ...thresholds, inAppAlertsEnabled: e.target.checked })
                }
                className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 text-xs font-semibold cursor-pointer">
              <span className="text-slate-700 dark:text-slate-300">
                Email Notifications for Claim Status Changes
              </span>
              <input
                type="checkbox"
                checked={thresholds.emailAlertsEnabled}
                onChange={(e) =>
                  setThresholds({ ...thresholds, emailAlertsEnabled: e.target.checked })
                }
                className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500"
              />
            </label>
          </div>
        </div>

        {isAdmin && (
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-6 py-2.5 bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold rounded-xl shadow-md shadow-brand-500/20 transition-all disabled:opacity-50"
            >
              {saving ? <Loader size="sm" text="" /> : <Save className="w-4 h-4" />}
              <span>Save System Settings</span>
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

export default SettingsPage;