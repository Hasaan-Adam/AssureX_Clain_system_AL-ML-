import React from 'react';
import { Link } from 'react-router-dom';
import {
  PlusCircle, ShieldCheck, FileText, ArrowRight, Sparkles,
  Package, TrendingUp, Clock, CheckCircle2, AlertTriangle,
  ChevronRight, Inbox, Shield, Zap, BarChart3, Bell,
} from 'lucide-react';

/* ─── helpers ─────────────────────────────────────── */
const greeting = () => {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
};

const fmtDate = (d) =>
  d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '—';

const daysLeft = (expiry) => {
  if (!expiry) return null;
  const diff = Math.ceil((new Date(expiry) - new Date()) / 86400000);
  return diff;
};

const STATUS_CONFIG = {
  pending:       { label: 'Pending',       bg: 'bg-amber-100 dark:bg-amber-900/30',   text: 'text-amber-700 dark:text-amber-300',   dot: 'bg-amber-500' },
  approved:      { label: 'Approved',      bg: 'bg-emerald-100 dark:bg-emerald-900/30', text: 'text-emerald-700 dark:text-emerald-300', dot: 'bg-emerald-500' },
  rejected:      { label: 'Rejected',      bg: 'bg-rose-100 dark:bg-rose-900/30',     text: 'text-rose-700 dark:text-rose-300',     dot: 'bg-rose-500' },
  manual_review: { label: 'Manual Review', bg: 'bg-violet-100 dark:bg-violet-900/30', text: 'text-violet-700 dark:text-violet-300', dot: 'bg-violet-500' },
  under_review:  { label: 'Under Review',  bg: 'bg-blue-100 dark:bg-blue-900/30',     text: 'text-blue-700 dark:text-blue-300',     dot: 'bg-blue-500' },
};

const StatusBadge = ({ status }) => {
  const cfg = STATUS_CONFIG[(status || '').toLowerCase()] || STATUS_CONFIG.pending;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold ${cfg.bg} ${cfg.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  );
};

/* ─── mini stat card ──────────────────────────────── */
const MiniStat = ({ icon: Icon, label, value, color, sub }) => (
  <div className="group p-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 flex flex-col gap-3">
    <div className="flex items-center justify-between">
      <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">{label}</p>
      <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${color}`}>
        <Icon className="w-4.5 h-4.5 w-[18px] h-[18px]" />
      </div>
    </div>
    <p className="text-3xl font-extrabold text-slate-900 dark:text-white leading-none">{value}</p>
    {sub && <p className="text-[11px] text-slate-500 dark:text-slate-400">{sub}</p>}
  </div>
);

/* ─── quick action card ───────────────────────────── */
const ActionCard = ({ to, icon: Icon, iconColor, title, desc }) => (
  <Link
    to={to}
    className="group flex items-center gap-4 p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md hover:border-brand-300 dark:hover:border-brand-700 hover:-translate-y-0.5 transition-all duration-200"
  >
    <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${iconColor}`}>
      <Icon className="w-5 h-5" />
    </div>
    <div className="flex-1 min-w-0">
      <p className="text-sm font-bold text-slate-900 dark:text-white">{title}</p>
      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 truncate">{desc}</p>
    </div>
    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-brand-500 transition-colors shrink-0" />
  </Link>
);

/* ─── main component ──────────────────────────────── */
export const UserDashboard = ({ user, warranties = [], claims = [], stats = {} }) => {
  const activeWarranties = warranties.filter((w) => (w.status || '').toUpperCase() === 'ACTIVE');
  const approvedClaims   = claims.filter((c) => (c.status || '').toLowerCase() === 'approved');
  const pendingClaims    = claims.filter((c) => ['pending', 'under_review', 'manual_review'].includes((c.status || '').toLowerCase()));
  const recentClaims     = claims.slice(0, 6);

  const expiringWarranties = warranties.filter((w) => {
    const d = daysLeft(w.expiry_date || w.warranty_expiry);
    return d !== null && d >= 0 && d <= 30;
  });

  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

  return (
    <div className="space-y-8 animate-fade-in">

      {/* ── Hero Banner ────────────────────────────────────── */}
      <div className="relative p-8 rounded-3xl bg-gradient-to-br from-brand-600 via-violet-600 to-slate-900 text-white shadow-2xl overflow-hidden">
        {/* decorative blobs */}
        <div className="absolute right-0 top-0 w-96 h-96 translate-x-24 -translate-y-24 bg-violet-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute right-48 bottom-0 w-64 h-64 translate-y-16 bg-brand-500/20 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-[11px] font-semibold mb-4 border border-white/20">
            <Sparkles className="w-3 h-3" />
            <span>AssureX AI v1.0 — Dual-Model Adjudication Active</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            {greeting()}, {user?.full_name?.split(' ')[0] || 'there'} 👋
          </h2>
          <p className="text-brand-200 text-sm mt-1.5">{today}</p>
          <p className="text-brand-100/80 text-sm mt-3 max-w-lg leading-relaxed">
            Manage your warranties, file AI-adjudicated claims, and track real-time decisions — all in one place.
          </p>

          <div className="flex flex-wrap items-center gap-3 mt-6">
            <Link
              to="/claims/new"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-white hover:bg-slate-100 text-brand-700 text-sm font-bold rounded-xl shadow-lg transition-all"
            >
              <PlusCircle className="w-4 h-4" />
              Submit New Claim
            </Link>
            <Link
              to="/warranties"
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-white/10 hover:bg-white/20 border border-white/20 text-white text-sm font-semibold rounded-xl transition-all"
            >
              <ShieldCheck className="w-4 h-4" />
              My Warranties
            </Link>
            <Link
              to="/products"
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-white/10 hover:bg-white/20 border border-white/20 text-white text-sm font-semibold rounded-xl transition-all"
            >
              <Package className="w-4 h-4" />
              Browse Products
            </Link>
          </div>
        </div>
      </div>

      {/* ── KPI Stats Grid ─────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MiniStat
          icon={ShieldCheck}
          label="Active Warranties"
          value={activeWarranties.length}
          color="bg-brand-50 dark:bg-brand-950/50 text-brand-600 dark:text-brand-400"
          sub="Products covered"
        />
        <MiniStat
          icon={FileText}
          label="Total Claims"
          value={claims.length}
          color="bg-violet-50 dark:bg-violet-950/50 text-violet-600 dark:text-violet-400"
          sub="Lifetime submissions"
        />
        <MiniStat
          icon={CheckCircle2}
          label="Approved"
          value={approvedClaims.length}
          color="bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400"
          sub="Successfully resolved"
        />
        <MiniStat
          icon={Clock}
          label="Pending Review"
          value={pendingClaims.length}
          color="bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400"
          sub="Awaiting decision"
        />
      </div>

      {/* ── Quick Actions ──────────────────────────────────── */}
      <div>
        <h3 className="text-base font-bold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-500" />
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <ActionCard
            to="/claims/new"
            icon={PlusCircle}
            iconColor="bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400"
            title="Submit New Claim"
            desc="AI adjudication in under 3 seconds"
          />
          <ActionCard
            to="/warranties"
            icon={Shield}
            iconColor="bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400"
            title="Register Warranty"
            desc="Cover your products with warranty"
          />
          <ActionCard
            to="/analytics"
            icon={BarChart3}
            iconColor="bg-violet-50 dark:bg-violet-950/60 text-violet-600 dark:text-violet-400"
            title="View Analytics"
            desc="Track claim trends & decisions"
          />
        </div>
      </div>

      {/* ── Expiry Alerts ──────────────────────────────────── */}
      {expiringWarranties.length > 0 && (
        <div className="p-5 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50">
          <div className="flex items-center gap-2 mb-3">
            <Bell className="w-4 h-4 text-amber-600 dark:text-amber-400" />
            <h3 className="text-sm font-bold text-amber-800 dark:text-amber-300">
              Warranty Expiry Alerts ({expiringWarranties.length})
            </h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
            {expiringWarranties.slice(0, 3).map((w, i) => {
              const d = daysLeft(w.expiry_date || w.warranty_expiry);
              return (
                <div key={i} className="flex items-center gap-3 p-3 bg-white dark:bg-slate-900 rounded-xl border border-amber-200 dark:border-amber-900/40">
                  <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold text-slate-800 dark:text-white truncate">
                      {w.product_name || w.product?.name || 'Product'}
                    </p>
                    <p className="text-[11px] text-amber-600 dark:text-amber-400 font-medium mt-0.5">
                      {d === 0 ? 'Expires today!' : `${d} day${d !== 1 ? 's' : ''} left`}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Recent Claims Table ────────────────────────────── */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <FileText className="w-4 h-4 text-brand-500" />
            Recent Claims
          </h3>
          <Link
            to="/claims"
            className="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1"
          >
            View All <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {recentClaims.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 bg-white dark:bg-slate-900 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700">
            <Inbox className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
            <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">No claims filed yet</p>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1 mb-5">Submit your first AI-adjudicated warranty claim</p>
            <Link
              to="/claims/new"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold rounded-xl transition-all shadow-lg shadow-brand-500/25"
            >
              <PlusCircle className="w-4 h-4" />
              Submit New Claim
            </Link>
          </div>
        ) : (
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-700">
                    <th className="text-left px-5 py-3 font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Claim #</th>
                    <th className="text-left px-4 py-3 font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Fault</th>
                    <th className="text-left px-4 py-3 font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Amount</th>
                    <th className="text-left px-4 py-3 font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Status</th>
                    <th className="text-left px-4 py-3 font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Date</th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {recentClaims.map((c, i) => (
                    <tr key={c.id || i} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                      <td className="px-5 py-3.5">
                        <span className="font-mono font-semibold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/50 px-2 py-0.5 rounded-md text-[11px]">
                          {c.claim_number || `CLM-${String(c.id || i + 1).padStart(4, '0')}`}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-slate-700 dark:text-slate-300 max-w-[140px] truncate">
                        {c.fault_description || c.fault_type || '—'}
                      </td>
                      <td className="px-4 py-3.5 font-semibold text-slate-900 dark:text-white">
                        {c.claim_amount ? `$${Number(c.claim_amount).toLocaleString()}` : '—'}
                      </td>
                      <td className="px-4 py-3.5">
                        <StatusBadge status={c.status} />
                      </td>
                      <td className="px-4 py-3.5 text-slate-500 dark:text-slate-400">
                        {fmtDate(c.created_at || c.submitted_at)}
                      </td>
                      <td className="px-4 py-3.5">
                        <Link
                          to={`/claims/${c.id}`}
                          className="text-brand-600 dark:text-brand-400 hover:underline font-semibold"
                        >
                          View →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* ── AI Engine Banner ───────────────────────────────── */}
      <div className="flex items-center gap-4 p-4 rounded-2xl bg-slate-900 dark:bg-slate-800 border border-slate-700">
        <div className="w-10 h-10 rounded-xl bg-brand-600 flex items-center justify-center shrink-0">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <p className="text-sm font-bold text-white">AssureX Dual-Model AI Engine Active</p>
          <p className="text-xs text-slate-400 mt-0.5">Python Tabular ML + Teachable Machine Vision</p>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[11px] font-semibold text-emerald-400">Operational</span>
        </div>
      </div>

    </div>
  );
};

export default UserDashboard;
