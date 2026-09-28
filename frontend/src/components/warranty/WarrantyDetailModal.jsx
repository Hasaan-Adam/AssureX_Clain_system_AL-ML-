import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  Calendar, 
  DollarSign, 
  Store, 
  Hash, 
  Clock, 
  AlertTriangle, 
  FileText, 
  Package, 
  CheckCircle2, 
  X,
  ExternalLink
} from 'lucide-react';
import { formatDate, formatCurrency } from '../../utils/formatters';

export const WarrantyDetailModal = ({ warranty, onClose }) => {
  if (!warranty) return null;

  const expiryDate = new Date(warranty.expiry_date);
  const now = new Date();
  const daysLeft = Math.ceil((expiryDate - now) / (1000 * 60 * 60 * 24));
  const isExpired = warranty.status === 'EXPIRED' || daysLeft < 0;
  const isExpiringSoon = !isExpired && daysLeft <= 30;
  const isActive = !isExpired && !isExpiringSoon;

  const brand = warranty.product?.brand || '';
  const model = warranty.product?.model_name || warranty.product_name || 'Device';
  const fullTitle = brand && model.toLowerCase().startsWith(brand.toLowerCase()) ? model : `${brand} ${model}`.trim();
  const imageUrl = warranty.image_url || warranty.product?.image_url || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80';

  return (
    <div className="space-y-6 max-h-[82vh] overflow-y-auto pr-1">
      {/* Product Hero Banner */}
      <div className="relative rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 p-4 sm:p-5 flex flex-col sm:flex-row items-center gap-5">
        <div className="w-28 h-28 shrink-0 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-sm">
          <img
            src={imageUrl}
            alt={fullTitle}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.currentTarget.onerror = null;
              e.currentTarget.src = 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80';
            }}
          />
        </div>

        <div className="flex-1 min-w-0 text-center sm:text-left">
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 mb-1.5">
            <span className="font-mono text-xs font-bold text-slate-500 dark:text-slate-400 bg-slate-200/70 dark:bg-slate-700/60 px-2 py-0.5 rounded-md">
              {warranty.warranty_number || `WAR-${String(warranty.id).padStart(5, '0')}`}
            </span>
            {isActive && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-400 text-xs font-bold rounded-full border border-emerald-200 dark:border-emerald-800">
                <ShieldCheck className="w-3.5 h-3.5" /> ACTIVE ({daysLeft} days left)
              </span>
            )}
            {isExpiringSoon && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-400 text-xs font-bold rounded-full border border-amber-200 dark:border-amber-800 animate-pulse">
                <AlertTriangle className="w-3.5 h-3.5" /> EXPIRING SOON ({daysLeft} days left)
              </span>
            )}
            {isExpired && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-400 text-xs font-bold rounded-full border border-rose-200 dark:border-rose-800">
                <Clock className="w-3.5 h-3.5" /> EXPIRED
              </span>
            )}
          </div>

          <h3 className="text-xl font-black text-slate-900 dark:text-white leading-snug">
            {fullTitle}
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">
            Serial Number: <span className="font-bold text-slate-800 dark:text-slate-200">{warranty.serial_number || 'N/A'}</span>
          </p>
        </div>
      </div>

      {/* Structured Details Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Coverage Card */}
        <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <ShieldCheck className="w-4 h-4 text-brand-600 dark:text-brand-400" />
            <span>Coverage & Dates</span>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center py-1 border-b border-slate-200/60 dark:border-slate-700/60">
              <span className="text-slate-500 dark:text-slate-400">Coverage Type</span>
              <span className="font-bold text-slate-900 dark:text-white">{warranty.warranty_type || 'Standard Manufacturer'}</span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-slate-200/60 dark:border-slate-700/60">
              <span className="text-slate-500 dark:text-slate-400">Start Date</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">{formatDate(warranty.start_date || warranty.purchase_date)}</span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-500 dark:text-slate-400">Expiration Date</span>
              <span className={`font-bold ${isExpired ? 'text-rose-600 dark:text-rose-400' : 'text-slate-900 dark:text-white'}`}>
                {formatDate(warranty.expiry_date)}
              </span>
            </div>
          </div>
        </div>

        {/* Purchase Info Card */}
        <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <Store className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span>Purchase & Invoice</span>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between items-center py-1 border-b border-slate-200/60 dark:border-slate-700/60">
              <span className="text-slate-500 dark:text-slate-400">Purchase Price</span>
              <span className="font-bold text-slate-900 dark:text-white">{formatCurrency(warranty.purchase_price || warranty.product?.purchase_price || 0)}</span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-slate-200/60 dark:border-slate-700/60">
              <span className="text-slate-500 dark:text-slate-400">Store / Retailer</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">{warranty.store_name || warranty.product?.retailer || 'Authorized Retailer'}</span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-500 dark:text-slate-400">Invoice / Receipt #</span>
              <span className="font-mono font-bold text-brand-600 dark:text-brand-400">{warranty.invoice_number || 'INV-VERIFIED'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Coverage Terms / Notes */}
      <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 space-y-4">
        {warranty.provider && (
          <div>
            <p className="text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Warranty Provider / Type:</p>
            <p className="text-xs font-semibold text-brand-600 dark:text-brand-400">{warranty.provider}</p>
          </div>
        )}
        
        {warranty.coverage_conditions && (
          <div>
            <p className="text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Coverage Conditions:</p>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{warranty.coverage_conditions}</p>
          </div>
        )}

        {warranty.exclusions && (
          <div>
            <p className="text-xs font-bold text-rose-700 dark:text-rose-400 mb-1">Exclusions (Not Covered):</p>
            <p className="text-xs text-rose-600/80 dark:text-rose-400/80 leading-relaxed">{warranty.exclusions}</p>
          </div>
        )}

        {warranty.service_centers && (
          <div>
            <p className="text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Authorized Service Centers:</p>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{warranty.service_centers}</p>
          </div>
        )}

        {warranty.notes && (
          <div>
            <p className="text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Additional Notes:</p>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{warranty.notes}</p>
          </div>
        )}
      </div>

      {/* Modal Actions */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
        >
          Close
        </button>
        {!isExpired && (
          <Link
            to={`/claims/new?warranty_id=${warranty.id}`}
            onClick={onClose}
            className="inline-flex items-center gap-1.5 px-5 py-2.5 bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold rounded-xl shadow-md shadow-brand-500/20 transition-all"
          >
            <FileText className="w-4 h-4" />
            <span>File a Claim for this Product</span>
          </Link>
        )}
      </div>
    </div>
  );
};

export default WarrantyDetailModal;
