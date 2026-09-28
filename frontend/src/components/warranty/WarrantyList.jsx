import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Package, Plus, FileText, Image as ImageIcon, Clock, ShieldCheck, AlertTriangle } from 'lucide-react';
import { formatDate } from '../../utils/formatters';

export const WarrantyList = ({
  warranties = [],
  onAddNew = null,
  onSelect = null,
}) => {
  const navigate = useNavigate();

  if (!warranties || warranties.length === 0) {
    return (
      <div className="bg-white dark:bg-slate-900 p-12 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center text-center">
        <div className="w-16 h-16 bg-slate-50 dark:bg-slate-800 rounded-full flex items-center justify-center mb-4">
          <Package className="w-8 h-8 text-slate-400" />
        </div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">No warranties found</h3>
        <p className="text-slate-500 dark:text-slate-400 max-w-sm mb-6">
          You haven't registered any warranties yet. Add your first product to get started.
        </p>
        {onAddNew && (
          <button
            onClick={onAddNew}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-slate-800 dark:bg-brand-600 dark:hover:bg-brand-500 text-white text-sm font-bold rounded-xl shadow-lg transition-all"
          >
            <Plus className="w-5 h-5" />
            <span>Register New Warranty</span>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      {warranties.map((row) => {
        const expiryDate = new Date(row.expiry_date);
        const now = new Date();
        const daysLeft = Math.ceil((expiryDate - now) / (1000 * 60 * 60 * 24));
        const isExpired = row.status === 'EXPIRED' || daysLeft < 0;
        const isExpiringSoon = !isExpired && daysLeft <= 30;
        const isActive = !isExpired && !isExpiringSoon;

        let cardStyle = "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900";
        if (isActive) cardStyle = "border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.1)] bg-white dark:bg-slate-900";
        else if (isExpiringSoon) cardStyle = "border-amber-500/50 shadow-[0_0_15px_rgba(245,158,11,0.1)] bg-white dark:bg-slate-900";
        else if (isExpired) cardStyle = "border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 opacity-75";

        return (
          <div
            key={row.id}
            onClick={() => onSelect && onSelect(row)}
            className={`relative rounded-2xl border overflow-hidden transition-all hover:-translate-y-1 hover:shadow-lg cursor-pointer ${cardStyle}`}
          >
            {/* Status Banner */}
            <div className="absolute top-4 right-4 z-10">
              {isActive && (
                <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-400 text-[10px] font-bold rounded-full border border-emerald-200 dark:border-emerald-800">
                  <ShieldCheck className="w-3 h-3" /> ACTIVE
                </span>
              )}
              {isExpiringSoon && (
                <span className="flex items-center gap-1.5 px-2.5 py-1 bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-400 text-[10px] font-bold rounded-full border border-amber-200 dark:border-amber-800 animate-pulse">
                  <AlertTriangle className="w-3 h-3" /> EXPIRING SOON
                </span>
              )}
              {isExpired && (
                <span className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 text-[10px] font-bold rounded-full border border-slate-200 dark:border-slate-700">
                  <Clock className="w-3 h-3" /> EXPIRED
                </span>
              )}
            </div>

            <div className="p-5">
              {/* Product Image */}
              <div className="w-full h-40 bg-slate-100 dark:bg-slate-800 rounded-xl mb-4 overflow-hidden relative border border-slate-200/50 dark:border-slate-700/50 group">
                <img
                  src={row.image_url || row.product?.image_url || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80'}
                  alt={row.product?.model_name || 'Product'}
                  className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                  onError={(e) => {
                    e.currentTarget.onerror = null;
                    e.currentTarget.src = 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80';
                  }}
                />
              </div>

              {/* Product Info */}
              <h4 className="text-lg font-black text-slate-900 dark:text-white mb-1 leading-tight pr-24">
                {(() => {
                  const brand = row.product?.brand || '';
                  const model = row.product?.model_name || row.product_name || 'Device';
                  if (brand && model.toLowerCase().startsWith(brand.toLowerCase())) {
                    return model;
                  }
                  return `${brand} ${model}`.trim();
                })()}
              </h4>
              <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-4 font-mono">
                <span>Model: {row.product?.model_number || 'N/A'}</span>
                <span>•</span>
                <span>SN: {row.serial_number}</span>
              </div>

              {/* Warranty Details */}
              <div className="space-y-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl p-3 border border-slate-100 dark:border-slate-700/50">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-500 dark:text-slate-400 font-medium text-xs">Coverage Type</span>
                  <span className="font-bold text-slate-900 dark:text-white text-xs">{row.warranty_type || 'Standard'}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-500 dark:text-slate-400 font-medium text-xs">Expires On</span>
                  <div className="text-right">
                    <div className="font-bold text-slate-900 dark:text-white text-xs">{formatDate(row.expiry_date)}</div>
                    {!isExpired && (
                      <div className={`text-[10px] font-bold ${isExpiringSoon ? 'text-amber-600 dark:text-amber-400' : 'text-slate-400'}`}>
                        {daysLeft} days left
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Actions Footer */}
            <div className="p-4 bg-slate-50/80 dark:bg-slate-800/30 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2">
              <button 
                onClick={(e) => { e.stopPropagation(); onSelect && onSelect(row); }}
                className="px-3 py-1.5 text-xs font-bold text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
              >
                View Details
              </button>
              {!isExpired && (
                <Link
                  to={`/claims/new?warranty_id=${row.id}`}
                  onClick={(e) => e.stopPropagation()}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-brand-50 text-brand-700 hover:bg-brand-100 dark:bg-brand-900/30 dark:text-brand-400 dark:hover:bg-brand-900/50 text-xs font-bold rounded-lg transition-colors border border-brand-200 dark:border-brand-800/50"
                >
                  <FileText className="w-3.5 h-3.5" />
                  File Claim
                </Link>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default WarrantyList;
