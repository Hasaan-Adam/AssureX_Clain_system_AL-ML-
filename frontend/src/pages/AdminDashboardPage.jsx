import React, { useState, useEffect } from 'react';
import dashboardAPI from '../api/dashboardAPI';
import reviewAPI from '../api/reviewAPI';
import AdminDashboard from '../components/dashboard/AdminDashboard';
import Loader from '../components/common/Loader';
import { useNotification } from '../context/NotificationContext';

export const AdminDashboardPage = () => {
  const [stats, setStats] = useState({});
  const [queueItems, setQueueItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const { toastError } = useNotification();

  const loadAdminData = async () => {
    try {
      const [sRes, qRes] = await Promise.allSettled([
        dashboardAPI.getAdminDashboard(),
        reviewAPI.getReviewQueue(),
      ]);

      if (sRes.status === 'fulfilled') {
        setStats(sRes.value.data || sRes.value || {});
      }
      if (qRes.status === 'fulfilled') {
        const list = qRes.value?.items || qRes.value?.data || (Array.isArray(qRes.value) ? qRes.value : []);
        setQueueItems(list);
      }
    } catch (err) {
      toastError(err.message || 'Failed to load operational telemetry');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  if (loading) {
    return <Loader isFullPage text="Connecting to AssureX Telemetry stream..." />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <AdminDashboard
        stats={stats}
        queueItems={queueItems}
        onRefresh={() => {
          setLoading(true);
          loadAdminData();
        }}
        loading={loading}
      />
    </div>
  );
};

export default AdminDashboardPage;