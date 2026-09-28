import React, { useState, useEffect } from 'react';
import warrantyAPI from '../api/warrantyAPI';
import { useNotification } from '../context/NotificationContext';
import WarrantyList from '../components/warranty/WarrantyList';
import WarrantyForm from '../components/warranty/WarrantyForm';
import WarrantyDetailModal from '../components/warranty/WarrantyDetailModal';
import Modal from '../components/common/Modal';
import Loader from '../components/common/Loader';
import { Plus } from 'lucide-react';

export const WarrantiesPage = () => {
  const [warranties, setWarranties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedWarranty, setSelectedWarranty] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { toastSuccess, toastError } = useNotification();

  const fetchWarranties = async () => {
    try {
      const res = await warrantyAPI.getWarranties();
      const list = res.warranties || res.data || (Array.isArray(res) ? res : []);
      setWarranties(list);
    } catch (err) {
      toastError(err.message || 'Failed to load warranties');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWarranties();
  }, []);

  const handleCreateWarranty = async (formData) => {
    setSubmitting(true);
    try {
      await warrantyAPI.createWarranty(formData);
      toastSuccess('Product warranty successfully registered!');
      setModalOpen(false);
      fetchWarranties();
    } catch (err) {
      toastError(err.message || 'Failed to register warranty');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSelectWarranty = (warranty) => {
    setSelectedWarranty(warranty);
    setDetailModalOpen(true);
  };

  if (loading) {
    return <Loader isFullPage text="Loading registered warranties..." />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white">
            My Warranties
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
            Active equipment coverage records, serial numbers, and expiry alerts
          </p>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-slate-800 dark:bg-brand-600 dark:hover:bg-brand-500 text-white text-sm font-bold rounded-xl shadow-lg transition-all transform hover:-translate-y-0.5"
        >
          <Plus className="w-5 h-5" />
          <span>Register New Warranty</span>
        </button>
      </div>

      <WarrantyList
        warranties={warranties}
        onAddNew={() => setModalOpen(true)}
        onSelect={handleSelectWarranty}
      />

      {/* Register Warranty Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Register Product Warranty"
      >
        <WarrantyForm
          onSubmit={handleCreateWarranty}
          onCancel={() => setModalOpen(false)}
          loading={submitting}
        />
      </Modal>

      {/* Warranty Details Modal */}
      <Modal
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        title="Warranty & Coverage Specifications"
      >
        <WarrantyDetailModal
          warranty={selectedWarranty}
          onClose={() => setDetailModalOpen(false)}
        />
      </Modal>
    </div>
  );
};

export default WarrantiesPage;