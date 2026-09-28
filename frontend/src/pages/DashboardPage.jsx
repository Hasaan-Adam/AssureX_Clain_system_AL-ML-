import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import warrantyAPI from '../api/warrantyAPI';
import claimAPI from '../api/claimAPI';
import dashboardAPI from '../api/dashboardAPI';
import UserDashboard from '../components/dashboard/UserDashboard';
import Loader from '../components/common/Loader';

export const DashboardPage = () => {
  const { user, isAdmin, isReviewer, isStaff } = useAuth();
  const [warranties, setWarranties] = useState([]);
  const [claims, setClaims] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [wRes, cRes, sRes] = await Promise.allSettled([
          warrantyAPI.getWarranties(),
          claimAPI.getClaims(),
          dashboardAPI.getCustomerDashboard(),
        ]);

        if (wRes.status === 'fulfilled') {
          const list = wRes.value?.warranties || wRes.value?.data || (Array.isArray(wRes.value) ? wRes.value : []);
          setWarranties(list);
        }
        if (cRes.status === 'fulfilled') {
          const list = cRes.value?.claims || cRes.value?.data || (Array.isArray(cRes.value) ? cRes.value : []);
          setClaims(list);
        }
        if (sRes.status === 'fulfilled') {
          setStats(sRes.value.data || sRes.value || {});
        }
      } catch (err) {
        console.error('Error fetching dashboard info', err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  if (loading) {
    return <Loader isFullPage text="Loading your dashboard..." />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <UserDashboard
        user={user}
        warranties={warranties}
        claims={claims}
        stats={stats}
      />
    </div>
  );
};

export default DashboardPage;