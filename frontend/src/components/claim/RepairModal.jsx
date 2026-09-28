import React, { useState } from 'react';
import apiClient from '../../api/client';
import { useNotification } from '../../context/NotificationContext';
import { X, Wrench } from 'lucide-react';
import Loader from '../common/Loader';

export const RepairModal = ({ isOpen, onClose, claim, onSuccess }) => {
  const { toastSuccess, toastError } = useNotification();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    repair_date: new Date().toISOString().split('T')[0],
    repair_center: '',
    parts_replaced: '',
    repair_cost: 0,
    authorized_status: 'yes',
  });

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.post('/repairs', {
        ...formData,
        product_id: claim.product_id || (claim.warranty && claim.warranty.product_id),
        claim_id: claim.id,
      });
      toastSuccess('Repair history logged successfully');
      onSuccess();
      onClose();
    } catch (err) {
      toastError(err.response?.data?.detail || err.message || 'Failed to log repair');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-slate-900 w-full max-w-md rounded-2xl shadow-2xl overflow-hidden border border-slate-200 dark:border-slate-800">
        <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Wrench className="w-4 h-4 text-brand-500" /> Repair History Management
          </h3>
          <button onClick={onClose} className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <X className="w-4 h-4 text-slate-500" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Repair Center *</label>
            <input required type="text" value={formData.repair_center} onChange={e => setFormData({...formData, repair_center: e.target.value})} className="w-full p-2 text-sm border rounded-lg dark:bg-slate-800 dark:border-slate-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500/20" placeholder="e.g. Official Samsung Care" />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Repair Date *</label>
              <input required type="date" value={formData.repair_date} onChange={e => setFormData({...formData, repair_date: e.target.value})} className="w-full p-2 text-sm border rounded-lg dark:bg-slate-800 dark:border-slate-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500/20" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Cost (PKR) *</label>
              <input required type="number" min="0" value={formData.repair_cost} onChange={e => setFormData({...formData, repair_cost: Number(e.target.value)})} className="w-full p-2 text-sm border rounded-lg dark:bg-slate-800 dark:border-slate-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500/20" />
            </div>
          </div>
          
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Parts Replaced</label>
            <input type="text" value={formData.parts_replaced} onChange={e => setFormData({...formData, parts_replaced: e.target.value})} className="w-full p-2 text-sm border rounded-lg dark:bg-slate-800 dark:border-slate-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500/20" placeholder="e.g. Compressor, Fan" />
          </div>
          
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Authorized Status</label>
            <select value={formData.authorized_status} onChange={e => setFormData({...formData, authorized_status: e.target.value})} className="w-full p-2 text-sm border rounded-lg dark:bg-slate-800 dark:border-slate-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500/20">
              <option value="yes">Authorized Repair Center</option>
              <option value="no">Unauthorized 3rd Party</option>
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t border-slate-100 dark:border-slate-800">
            <button type="button" onClick={onClose} className="px-4 py-2 text-xs font-bold text-slate-600 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 rounded-xl transition-colors">Cancel</button>
            <button type="submit" disabled={loading} className="px-4 py-2 text-xs font-bold text-white bg-brand-600 hover:bg-brand-500 rounded-xl shadow-lg transition-all flex items-center gap-2">
              {loading ? <Loader /> : <Wrench className="w-3.5 h-3.5" />} Repair History Management
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
