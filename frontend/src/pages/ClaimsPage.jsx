import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus } from 'lucide-react';
import claimAPI from '../api/claimAPI';
import ClaimList from '../components/claim/ClaimList';
import Loader from '../components/common/Loader';
import { useNotification } from '../context/NotificationContext';

export const ClaimsPage = () => {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const { toastError } = useNotification();

  useEffect(() => {
    const fetchClaims = async () => {
      try {
        const res = await claimAPI.getClaims();
        const list = res.claims || res.data || (Array.isArray(res) ? res : []);
        setClaims(list);
      } catch (err) {
        toastError(err.message || 'Failed to load claims');
      } finally {
        setLoading(false);
      }
    };
    fetchClaims();
  }, []);

  if (loading) {
    return <Loader isFullPage text="Loading claims dossier..." />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Hero Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white">
            Warranty Claims Dossier
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
            Review real-time AI adjudication status, decisions, and appeal history.
          </p>
        </div>
        <Link
          to="/claims/new"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white text-sm font-bold rounded-xl shadow-lg shadow-brand-500/30 transition-all transform hover:-translate-y-0.5"
        >
          <Plus className="w-5 h-5" />
          <span>Submit New Claim</span>
        </Link>
      </div>

      <ClaimList claims={claims} showCreateButton={false} />
    </div>
  );
};

export default ClaimsPage;
