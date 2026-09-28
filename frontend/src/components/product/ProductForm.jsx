import React, { useState } from 'react';
import { PRODUCT_CATEGORIES } from '../../utils/constants';
import Loader from '../common/Loader';

export const ProductForm = ({ initialData = {}, onSubmit, onCancel, loading = false }) => {
  const [formData, setFormData] = useState({
    model_name: initialData.model_name || '',
    brand: initialData.brand || '',
    category: initialData.category || PRODUCT_CATEGORIES[0].id,
    model_number: initialData.model_number || '',
    serial_number: initialData.serial_number || '',
    purchase_date: initialData.purchase_date || new Date().toISOString().split('T')[0],
    purchase_price: initialData.purchase_price || initialData.msrp || '',
    retailer: initialData.retailer || '',
    warranty_months: initialData.warranty_months || initialData.warranty_duration_months || 12,
    description: initialData.description || '',
    is_active: initialData.is_active !== undefined ? initialData.is_active : true,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      purchase_price: parseFloat(formData.purchase_price) || 0,
      msrp: parseFloat(formData.purchase_price) || 0,
      warranty_months: parseInt(formData.warranty_months, 10) || 12,
    });
  };

  const inputClass = "w-full px-3.5 py-2.5 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-500 transition-all dark:text-white placeholder-slate-400";
  const labelClass = "block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5";

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-h-[78vh] overflow-y-auto pr-1">

      {/* Row 1: Brand + Model Name */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Brand Name *</label>
          <input
            type="text"
            required
            name="brand"
            value={formData.brand}
            onChange={handleChange}
            placeholder="e.g. Apple, Samsung, Sony"
            className={inputClass}
          />
        </div>
        <div>
          <label className={labelClass}>Product / Model Name *</label>
          <input
            type="text"
            required
            name="model_name"
            value={formData.model_name}
            onChange={handleChange}
            placeholder="e.g. iPhone 15 Pro Max 256GB"
            className={inputClass}
          />
        </div>
      </div>

      {/* Row 2: Category + Model Number */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Category *</label>
          <select
            name="category"
            value={formData.category}
            onChange={handleChange}
            className={inputClass}
          >
            {PRODUCT_CATEGORIES.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>Model Number *</label>
          <input
            type="text"
            required
            name="model_number"
            value={formData.model_number}
            onChange={handleChange}
            placeholder="e.g. MQAW3LL/A"
            className={inputClass}
          />
        </div>
      </div>

      {/* Row 3: Serial Number (full width - it's important) */}
      <div>
        <label className={labelClass}>Serial Number *</label>
        <input
          type="text"
          required
          name="serial_number"
          value={formData.serial_number}
          onChange={handleChange}
          placeholder="e.g. C8GH3K2BQX9V — used for warranty verification & OCR matching"
          className={inputClass}
        />
        <p className="text-[10px] text-slate-400 mt-1">
          ⚠ Must be exact — used for serial number verification during claim processing
        </p>
      </div>

      {/* Row 4: Purchase Date + Purchase Price */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Purchase Date *</label>
          <input
            type="date"
            required
            name="purchase_date"
            max={new Date().toISOString().split('T')[0]}
            value={formData.purchase_date}
            onChange={handleChange}
            className={inputClass}
          />
        </div>
        <div>
          <label className={labelClass}>Purchase Price ($) *</label>
          <input
            type="number"
            step="0.01"
            min="0"
            required
            name="purchase_price"
            value={formData.purchase_price}
            onChange={handleChange}
            placeholder="1299.99"
            className={inputClass}
          />
        </div>
      </div>

      {/* Row 5: Retailer + Warranty Duration */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Retailer / Store Name *</label>
          <input
            type="text"
            required
            name="retailer"
            value={formData.retailer}
            onChange={handleChange}
            placeholder="e.g. Apple Store, Best Buy, Amazon"
            className={inputClass}
          />
        </div>
        <div>
          <label className={labelClass}>Warranty Duration (Months) *</label>
          <input
            type="number"
            required
            min="1"
            max="120"
            name="warranty_months"
            value={formData.warranty_months}
            onChange={handleChange}
            placeholder="12"
            className={inputClass}
          />
        </div>
      </div>

      {/* Row 6: Description + Active toggle */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className={labelClass}>Description / Notes</label>
          <textarea
            rows={2}
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Model specifications, coverage conditions..."
            className={inputClass}
          />
        </div>
        <div className="flex items-center pt-6">
          <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-700 dark:text-slate-300">
            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 border-slate-300"
            />
            Product is Active & Available
          </label>
        </div>
      </div>

      {/* Unique Product ID notice */}
      <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
        <p className="text-[10px] text-slate-500 dark:text-slate-400">
          🔑 A unique <strong>Product ID</strong> (e.g. <code className="font-mono bg-slate-200 dark:bg-slate-700 px-1 rounded">PRD-XXXXX</code>) will be auto-assigned upon registration.
        </p>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2.5 text-xs font-bold text-white bg-brand-600 hover:bg-brand-500 disabled:opacity-50 rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center gap-2"
        >
          {loading && <Loader size="sm" text="" />}
          <span>{initialData.id ? 'Update Product' : 'Register Product'}</span>
        </button>
      </div>
    </form>
  );
};

export default ProductForm;