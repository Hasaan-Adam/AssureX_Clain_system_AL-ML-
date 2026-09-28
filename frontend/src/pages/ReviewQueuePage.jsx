import React, { useState, useEffect } from 'react';
import reviewAPI from '../api/reviewAPI';
import ReviewQueue from '../components/review/ReviewQueue';
import Loader from '../components/common/Loader';
import { useNotification } from '../context/NotificationContext';
import { CheckSquare, RefreshCw } from 'lucide-react';

export const ReviewQueuePage = () => {
  const [queueItems, setQueueItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const { toastError, toastSuccess } = useNotification();

  const fetchQueue = async () => {
    try {
      const res = await reviewAPI.getReviewQueue();
      const list = res.items || res.data || (Array.isArray(res) ? res : []);
      setQueueItems(list);
    } catch (err) {
      toastError(err.message || 'Failed to load review queue');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  if (loading) {
    return <Loader isFullPage text="Loading manual adjudication queue..." />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white flex items-center gap-2.5">
            <CheckSquare className="w-6 h-6 text-brand-600" />
            <span>Adjudicator Review Queue</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Evaluate claims requiring human oversight, model divergence arbitration, and policy exception review
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            setLoading(true);
            fetchQueue();
          }}
          className="flex items-center gap-1.5 px-4 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 transition-colors shadow-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Queue</span>
        </button>
      </div>

      <ReviewQueue queueItems={queueItems} />
    </div>
  );
};

export default ReviewQueuePage;