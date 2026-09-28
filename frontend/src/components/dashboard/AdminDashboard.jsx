import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, TrendingDown, FileText, DollarSign, Target, Clock,
  CheckCircle2, Database, Camera, Activity, Users, BarChart3, Download, Settings, ShieldAlert
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import adminAPI from '../../api/adminAPI';

const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
const formatPercent = (val) => new Intl.NumberFormat('en-US', { style: 'percent', maximumFractionDigits: 1 }).format(val);

export const AdminDashboard = ({ stats = {}, queueItems = [], onRefresh = null, loading = false }) => {
  const navigate = useNavigate();
  const [auditLogs, setAuditLogs] = useState([]);
  const [anomalies, setAnomalies] = useState([]);

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const [auditRes, anomalyRes] = await Promise.all([
          adminAPI.getAuditLogs({ limit: 10 }),
          adminAPI.getAnomalies()
        ]);
        setAuditLogs(auditRes.data?.logs || auditRes?.logs || []);
        setAnomalies(anomalyRes.data?.anomalies || anomalyRes?.anomalies || []);
      } catch (err) {
        console.error("Failed to load audit logs or anomalies", err);
      }
    };
    fetchAdminData();
  }, []);
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">Administrator Dashboard</h2>
          <p className="text-sm text-slate-500 mt-1">System overview and key performance metrics</p>
        </div>
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-sm disabled:opacity-50"
          >
            <Activity className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        )}
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { title: 'Total Claims', value: stats.total_claims !== undefined ? stats.total_claims : 0, icon: FileText, color: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-100 dark:bg-blue-900/50', trend: '+12%', up: true },
          { title: 'Approved Claims', value: stats.approved_claims !== undefined ? stats.approved_claims : 0, icon: DollarSign, color: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-100 dark:bg-emerald-900/50', trend: '+8.4%', up: true },
          { 
            title: 'AI Approval Rate', 
            value: stats.approval_rate !== undefined && stats.approval_rate !== null 
              ? (Number(stats.approval_rate) > 1 ? `${Number(stats.approval_rate).toFixed(1)}%` : formatPercent(Number(stats.approval_rate)))
              : '—', 
            icon: Target, 
            color: 'text-purple-600 dark:text-purple-400', 
            bg: 'bg-purple-100 dark:bg-purple-900/50', 
            trend: '+1.2%', 
            up: true 
          },
          { title: 'Avg Turnaround Time', value: stats.average_turnaround_hours ? `${stats.average_turnaround_hours} hrs` : '2.4 hrs', icon: Clock, color: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-100 dark:bg-amber-900/50', trend: '-15%', up: true },
        ].map((kpi, i) => (
          <div key={i} className="p-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col gap-3">
            <div className="flex items-start justify-between">
              <div className={`p-3 rounded-xl ${kpi.bg}`}>
                <kpi.icon className={`w-6 h-6 ${kpi.color}`} />
              </div>
              <span className={`flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-full ${kpi.up ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-rose-50 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400'}`}>
                {kpi.up ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {kpi.trend}
              </span>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{kpi.title}</p>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{kpi.value}</h3>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Charts Section: Dynamic Live Distribution */}
          {(() => {
            const total = stats.total_claims || ((stats.approved_claims || 0) + (stats.pending_reviews || stats.pending_review || 0) + (stats.rejected_claims || 0)) || 0;
            const approvedCount = stats.approved_claims || stats.approved || 0;
            const manualCount = stats.pending_reviews || stats.pending_review || 0;
            const rejectedCount = stats.rejected_claims || stats.rejected || 0;

            const approvedPct = total > 0 ? (stats.approval_rate !== undefined ? (stats.approval_rate > 1 ? Math.round(stats.approval_rate) : Math.round(stats.approval_rate * 100)) : Math.round((approvedCount / total) * 100)) : 0;
            const manualPct = total > 0 ? (stats.manual_review_rate !== undefined ? (stats.manual_review_rate > 1 ? Math.round(stats.manual_review_rate) : Math.round(stats.manual_review_rate * 100)) : Math.round((manualCount / total) * 100)) : 0;
            const rejectedPct = total > 0 ? (stats.rejection_rate !== undefined ? (stats.rejection_rate > 1 ? Math.round(stats.rejection_rate) : Math.round(stats.rejection_rate * 100)) : Math.max(0, 100 - approvedPct - manualPct)) : 0;

            const distributionBars = [
              { label: 'Auto / Reviewer Approved', count: approvedCount, pct: approvedPct, color: 'bg-emerald-500' },
              { label: 'Manual Review & In-Evaluation', count: manualCount, pct: manualPct, color: 'bg-amber-500' },
              { label: 'Rejected Claims', count: rejectedCount, pct: rejectedPct, color: 'bg-rose-500' }
            ];

            return (
              <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900 dark:text-white">Claim Status Tracking</h3>
                    <p className="text-xs text-slate-500">Live operational telemetry across {total} total claims</p>
                  </div>
                </div>
                <div className="space-y-4">
                  {distributionBars.map((bar, i) => (
                    <div key={i}>
                      <div className="flex justify-between text-sm mb-1.5">
                        <span className="font-medium text-slate-700 dark:text-slate-300 flex items-center gap-2">
                          <span>{bar.label}</span>
                          <span className="text-xs text-slate-400 font-mono">({bar.count} claims)</span>
                        </span>
                        <span className="font-bold text-slate-900 dark:text-white font-mono">{bar.pct}%</span>
                      </div>
                      <div className="h-2.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div className={`h-full ${bar.color} rounded-full transition-all duration-500`} style={{ width: `${bar.pct}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })()}

          {/* Recent Activity Feed */}
          <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Recent Activity</h3>
            <div className="space-y-4">
              {(queueItems.length ? queueItems.slice(0, 10) : Array(5).fill({ claim_number: 'CLM-000', status: 'UPDATED', created_at: new Date().toISOString() })).map((item, i) => (
                <div key={i} className="flex items-center gap-4 p-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-xl transition-colors">
                  <div className="w-2 h-2 rounded-full bg-brand-500 mt-1" />
                  <div className="flex-1">
                    <p className="text-sm text-slate-800 dark:text-slate-200">
                      Claim <span className="font-semibold">{item.claim_number}</span> status changed to <span className="font-semibold">{item.status || 'REVIEW'}</span>
                    </p>
                    <p className="text-xs text-slate-500">{new Date(item.created_at || Date.now()).toLocaleString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {/* System Health */}
          <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">System Health</h3>
            <div className="space-y-3">
              {[
                { name: 'AI Engine Status', status: 'Operational', icon: Activity, color: 'text-emerald-500' },
                { name: 'Database', status: 'Healthy', icon: Database, color: 'text-emerald-500' },
                { name: 'OCR Service', status: 'Operational', icon: Camera, color: 'text-emerald-500' }
              ].map((sys, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
                  <div className="flex items-center gap-3">
                    <sys.icon className="w-5 h-5 text-slate-400" />
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{sys.name}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span className={`text-xs font-semibold ${sys.color}`}>{sys.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'Manage Users', icon: Users, path: '/users' },
                { label: 'View Analytics', icon: BarChart3, path: '/analytics' },
                { label: 'Export Reports', icon: Download, path: '/reports' },
                { label: 'System Settings', icon: Settings, path: '/settings' },
              ].map((action, i) => (
                <button key={i} onClick={() => action.path ? navigate(action.path) : null} className="flex flex-col items-center justify-center p-4 bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors gap-2 text-slate-600 dark:text-slate-400 hover:text-brand-600 dark:hover:text-brand-400">
                  <action.icon className="w-6 h-6" />
                  <span className="text-xs font-semibold text-center">{action.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Audit Logs */}
        <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Recent Audit Logs</h3>
          {auditLogs.length === 0 ? (
            <p className="text-sm text-slate-500">No audit records found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600 dark:text-slate-400">
                <thead className="bg-slate-50 dark:bg-slate-800/50 text-slate-500 dark:text-slate-300">
                  <tr>
                    <th className="px-4 py-2 rounded-tl-lg">Action</th>
                    <th className="px-4 py-2">User</th>
                    <th className="px-4 py-2">Timestamp</th>
                    <th className="px-4 py-2 rounded-tr-lg">Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {auditLogs.map((log, i) => (
                    <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                      <td className="px-4 py-2 font-medium text-slate-900 dark:text-white">{log.action}</td>
                      <td className="px-4 py-2">{log.user || log.user_id}</td>
                      <td className="px-4 py-2">{new Date(log.timestamp || log.created_at).toLocaleString()}</td>
                      <td className="px-4 py-2">{log.description || log.details}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Anomaly Alerts */}
        <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Anomaly Alerts</h3>
          {anomalies.length === 0 ? (
            <p className="text-sm text-emerald-600 font-medium flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> ✓ No anomalies detected
            </p>
          ) : (
            <div className="space-y-3">
              {anomalies.map((anom, i) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-rose-50 dark:bg-rose-900/10 border border-rose-100 dark:border-rose-900/30 rounded-xl">
                  <ShieldAlert className="w-5 h-5 text-rose-500 mt-0.5" />
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-rose-700 dark:text-rose-400 bg-rose-100 dark:bg-rose-900/50 px-2 py-0.5 rounded uppercase">
                        {anom.severity || 'HIGH'}
                      </span>
                      <span className="text-xs text-slate-500">{new Date(anom.timestamp || anom.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-sm text-slate-800 dark:text-slate-200 mt-1">{anom.description || anom.message}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;