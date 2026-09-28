import React, { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, Eye, Search, Calendar, ShieldAlert, ChevronLeft, ChevronRight } from 'lucide-react';
import { formatDate, formatCurrency } from '../../utils/formatters';

const getStatusColor = (status) => {
  const s = (status || '').toUpperCase();
  if (s === 'PENDING') return 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200 dark:border-amber-800';
  if (s === 'APPROVED') return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800';
  if (s === 'REJECTED') return 'bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-400 border-rose-200 dark:border-rose-800';
  if (s === 'MANUAL_REVIEW') return 'bg-violet-100 text-violet-800 dark:bg-violet-900/30 dark:text-violet-400 border-violet-200 dark:border-violet-800';
  if (s === 'UNDER_REVIEW') return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800';
  return 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700';
};

const ITEMS_PER_PAGE = 10;

export const ClaimList = ({
  claims = [],
  onSelectClaim = null,
  showCreateButton = true,
}) => {
  const navigate = useNavigate();
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const stats = useMemo(() => {
    const counts = { ALL: claims.length, PENDING: 0, APPROVED: 0, REJECTED: 0, UNDER_REVIEW: 0 };
    claims.forEach(c => {
      const s = (c.status || '').toUpperCase();
      if (counts[s] !== undefined) counts[s]++;
    });
    return counts;
  }, [claims]);

  const filtered = useMemo(() => {
    return claims.filter((c) => {
      if (filterStatus !== 'ALL' && (c.status || '').toUpperCase() !== filterStatus) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const match =
          (c.claim_number || '').toLowerCase().includes(q) ||
          (c.fault_type || '').toLowerCase().includes(q) ||
          (c.warranty?.product?.brand || '').toLowerCase().includes(q) ||
          (c.warranty?.product?.model_name || '').toLowerCase().includes(q);
        if (!match) return false;
      }
      if (startDate) {
        const claimDate = new Date(c.created_at || c.submitted_at);
        if (!isNaN(claimDate) && claimDate < new Date(startDate)) return false;
      }
      if (endDate) {
        const claimDate = new Date(c.created_at || c.submitted_at);
        if (!isNaN(claimDate) && claimDate > new Date(endDate + 'T23:59:59')) return false;
      }
      return true;
    });
  }, [claims, filterStatus, searchQuery, startDate, endDate]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / ITEMS_PER_PAGE));
  const safePage = Math.min(currentPage, totalPages);
  const startIdx = (safePage - 1) * ITEMS_PER_PAGE;
  const pageItems = filtered.slice(startIdx, startIdx + ITEMS_PER_PAGE);

  const handleFilterChange = (key) => {
    setFilterStatus(key);
    setCurrentPage(1);
  };

  const handleSearch = (val) => {
    setSearchQuery(val);
    setCurrentPage(1);
  };

  const handleRowClick = (row) => {
    if (onSelectClaim) onSelectClaim(row);
    else navigate(`/claims/${row.id}`);
  };

  return (
    <div className="space-y-6">
      {/* Stats Summary Row */}
      <div className="flex flex-wrap gap-3">
        {Object.entries(stats).map(([key, count]) => (
          <button
            key={key}
            onClick={() => handleFilterChange(key)}
            className={`px-4 py-2 rounded-xl text-sm font-bold border transition-all ${
              filterStatus === key
                ? 'bg-brand-50 border-brand-200 text-brand-700 dark:bg-brand-900/30 dark:border-brand-800 dark:text-brand-400'
                : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-400 dark:hover:bg-slate-800'
            }`}
          >
            {key.replace('_', ' ')} <span className="ml-2 px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-xs">{count}</span>
          </button>
        ))}
      </div>

      {/* Filter Bar */}
      <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row gap-4 items-center">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by claim #, fault type, brand..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 dark:text-white placeholder-slate-400"
          />
        </div>
        <div className="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto">
          <select
            value={filterStatus}
            onChange={(e) => handleFilterChange(e.target.value)}
            className="w-full sm:w-auto px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-brand-500 dark:text-white"
          >
            <option value="ALL">All Statuses</option>
            <option value="PENDING">Pending</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
          </select>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Calendar className="w-4 h-4 text-slate-400 hidden sm:block" />
            <input
              type="date"
              value={startDate}
              onChange={(e) => { setStartDate(e.target.value); setCurrentPage(1); }}
              className="flex-1 sm:w-auto px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none dark:text-white"
            />
            <span className="text-slate-400">–</span>
            <input
              type="date"
              value={endDate}
              onChange={(e) => { setEndDate(e.target.value); setCurrentPage(1); }}
              className="flex-1 sm:w-auto px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none dark:text-white"
            />
          </div>
        </div>
      </div>

      {/* Claims Table */}
      {filtered.length > 0 ? (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden flex flex-col">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Claim</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Product & Fault</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Amount</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status & AI</th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {pageItems.map((row) => (
                  <tr
                    key={row.id}
                    onClick={() => handleRowClick(row)}
                    className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer group"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="inline-flex items-center px-2.5 py-1 rounded-md bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-400 font-mono text-xs font-bold border border-brand-100 dark:border-brand-800">
                        {row.claim_number || `CLM-${String(row.id).padStart(4,'0')}`}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">
                        {formatDate(row.submitted_at || row.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-900 dark:text-white">
                        {row.warranty?.product?.brand} {row.warranty?.product?.model_name || 'Equipment'}
                      </div>
                      <div className="text-sm text-slate-500 dark:text-slate-400">{row.fault_type}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="font-bold text-slate-900 dark:text-white">{formatCurrency(row.claim_amount)}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col gap-2 items-start">
                        <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold border ${getStatusColor(row.status)}`}>
                          {(row.status || 'PENDING').replace('_', ' ')}
                        </span>
                        {row.ai_decision && (
                          <div className="flex items-center gap-1.5 px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded text-[10px] font-bold text-slate-600 dark:text-slate-300">
                            AI: {row.ai_decision} {row.ai_confidence && `(${Math.round(row.ai_confidence * 100)}%)`}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <button className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-brand-300 dark:hover:border-brand-600 hover:text-brand-600 dark:hover:text-brand-400 text-slate-600 dark:text-slate-300 text-xs font-bold rounded-lg transition-colors">
                        <Eye className="w-4 h-4" />
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer — FIXED */}
          <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 flex justify-between items-center text-sm text-slate-500">
            <span>
              Showing <span className="font-semibold text-slate-700 dark:text-slate-300">{startIdx + 1}–{Math.min(startIdx + ITEMS_PER_PAGE, filtered.length)}</span>{' '}
              of <span className="font-semibold text-slate-700 dark:text-slate-300">{filtered.length}</span> claims
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={safePage <= 1}
                className="inline-flex items-center gap-1 px-3 py-1.5 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="w-3.5 h-3.5" /> Prev
              </button>
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">
                {safePage} / {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={safePage >= totalPages}
                className="inline-flex items-center gap-1 px-3 py-1.5 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Next <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 p-12 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 bg-slate-50 dark:bg-slate-800 rounded-full flex items-center justify-center mb-4">
            <ShieldAlert className="w-8 h-8 text-slate-400" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">No claims found</h3>
          <p className="text-slate-500 dark:text-slate-400 max-w-sm mb-6">
            There are no claims matching your current filters. Clear filters or submit a new claim to get started.
          </p>
          {showCreateButton && (
            <Link
              to="/claims/new"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white text-sm font-bold rounded-xl shadow-lg shadow-brand-500/30 transition-all"
            >
              <Plus className="w-5 h-5" />
              <span>Submit New Claim</span>
            </Link>
          )}
        </div>
      )}
    </div>
  );
};

export default ClaimList;
