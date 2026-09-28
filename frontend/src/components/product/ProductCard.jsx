import React from 'react';
import { Package, Shield, Smartphone, Laptop, Tv, Home, ChevronRight } from 'lucide-react';
import { formatCurrency } from '../../utils/formatters';

const getCategoryIcon = (category) => {
  switch (category) {
    case 'MOBILE_PHONES': return <Smartphone className="w-5 h-5" />;
    case 'ELECTRONICS': return <Laptop className="w-5 h-5" />;
    case 'HOME_APPLIANCES': return <Home className="w-5 h-5" />;
    default: return <Package className="w-5 h-5" />;
  }
};

const getCategoryColor = (category) => {
  switch (category) {
    case 'MOBILE_PHONES': return 'bg-blue-100 text-blue-600 dark:bg-blue-900/50 dark:text-blue-400';
    case 'ELECTRONICS': return 'bg-purple-100 text-purple-600 dark:bg-purple-900/50 dark:text-purple-400';
    case 'HOME_APPLIANCES': return 'bg-amber-100 text-amber-600 dark:bg-amber-900/50 dark:text-amber-400';
    default: return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400';
  }
};

export const ProductCard = ({ product, onSelect = null, isSelected = false }) => {
  if (!product) return null;

  return (
    <div
      className={`relative p-5 rounded-2xl border flex flex-col justify-between transition-all duration-300 ease-out group bg-white dark:bg-slate-900 ${
        isSelected
          ? 'border-brand-500 ring-2 ring-brand-500/20 shadow-lg'
          : 'border-slate-200 dark:border-slate-800 hover:border-brand-300 dark:hover:border-brand-700 hover:shadow-xl hover:-translate-y-1'
      }`}
    >
      <div>
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 shadow-sm ${getCategoryColor(product.category)}`}>
            {getCategoryIcon(product.category)}
          </div>
          <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-full bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-100 dark:border-slate-700">
            {product.category?.replace(/_/g, ' ')}
          </span>
        </div>

        <div className="mb-4">
          <p className="text-xs font-semibold text-brand-600 dark:text-brand-400 mb-1 uppercase tracking-wide">
            {product.brand}
          </p>
          <h4 className="font-bold text-lg text-slate-900 dark:text-white leading-tight mb-2 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
            {product.model_name}
          </h4>
          <div className="inline-flex items-center px-2 py-1 rounded-md bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <span className="font-mono text-xs text-slate-600 dark:text-slate-300 font-medium">
              {product.serial_prefix || 'MDL-XXXX'}
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium uppercase tracking-wider mb-0.5">
              Coverage
            </span>
            <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-200 text-sm font-semibold">
              <Shield className="w-4 h-4 text-emerald-500" />
              {product.warranty_months} Months
              {product.warranty_months > 12 && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 ml-1">
                  EXT
                </span>
              )}
            </div>
          </div>
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium uppercase tracking-wider mb-0.5">
              MSRP
            </span>
            <span className="font-black text-slate-900 dark:text-white text-base">
              {formatCurrency(product.msrp)}
            </span>
          </div>
        </div>

        <button
          onClick={(e) => {
            if (onSelect) {
              e.stopPropagation();
              onSelect(product);
            }
          }}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-slate-50 hover:bg-brand-50 dark:bg-slate-800 dark:hover:bg-brand-900/40 text-slate-700 hover:text-brand-700 dark:text-slate-200 dark:hover:text-brand-300 font-semibold text-sm border border-slate-200 dark:border-slate-700 hover:border-brand-200 dark:hover:border-brand-800 transition-all group/btn"
        >
          Register Warranty
          <ChevronRight className="w-4 h-4 transition-transform group-hover/btn:translate-x-1" />
        </button>
      </div>
    </div>
  );
};

export default ProductCard;