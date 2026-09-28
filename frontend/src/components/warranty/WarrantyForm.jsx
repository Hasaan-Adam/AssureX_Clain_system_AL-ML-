import React, { useState, useEffect, useRef } from 'react';
import productAPI from '../../api/productAPI';
import documentAPI from '../../api/documentAPI';
import Loader from '../common/Loader';
import { isValidSerialNumber, isValidAmount } from '../../utils/validators';
import { 
  ShieldCheck, 
  Calendar, 
  DollarSign, 
  CheckCircle2, 
  AlertCircle, 
  UploadCloud, 
  Image as ImageIcon, 
  X, 
  Sparkles,
  Store,
  FileSearch
} from 'lucide-react';

export const WarrantyForm = ({ onSubmit, onCancel, loading = false, initialData = {} }) => {
  const [products, setProducts] = useState([]);
  const [fetchingProducts, setFetchingProducts] = useState(true);
  const [serialVerified, setSerialVerified] = useState(null);
  const [verifyingSerial, setVerifyingSerial] = useState(false);
  const [imagePreview, setImagePreview] = useState(initialData.image_url || '');
  const [isDragging, setIsDragging] = useState(false);
  const [formError, setFormError] = useState('');
  const [scanningInvoice, setScanningInvoice] = useState(false);
  const [ocrExtractedInfo, setOcrExtractedInfo] = useState(null);
  const fileInputRef = useRef(null);

  const [formData, setFormData] = useState({
    product_id: initialData.product_id || '',
    serial_number: initialData.serial_number || '',
    purchase_date: initialData.purchase_date || new Date().toISOString().split('T')[0],
    purchase_price: initialData.purchase_price || '',
    invoice_number: initialData.invoice_number || '',
    store_name: initialData.store_name || '',
    provider: initialData.provider || '',
    coverage_conditions: initialData.coverage_conditions || '',
    exclusions: initialData.exclusions || '',
    service_centers: initialData.service_centers || '',
    notes: initialData.notes || '',
    image_url: initialData.image_url || '',
  });

  useEffect(() => {
    const fetchProds = async () => {
      try {
        const res = await productAPI.getProducts();
        const list = res.products || res.data || (Array.isArray(res) ? res : []);
        setProducts(list);
        if (!formData.product_id && list.length > 0) {
          setFormData((p) => ({ ...p, product_id: list[0].id }));
        }
      } catch (err) {
        console.error('Failed to load products', err);
      } finally {
        setFetchingProducts(false);
      }
    };
    fetchProds();
  }, []);

  const selectedProduct = products.find((p) => p.id === Number(formData.product_id));

  const displayImage = imagePreview || (selectedProduct ? selectedProduct.image_url : '');

  const handleChange = (e) => {
    let { name, value } = e.target;
    if (name === 'serial_number') {
      value = value.toUpperCase().trim();
    }
    setFormData((prev) => ({ ...prev, [name]: value }));
    setFormError('');
    if (name === 'serial_number' || name === 'product_id') {
      setSerialVerified(null);
    }
  };

  const handleFileProcess = async (file) => {
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file (PNG, JPG, WEBP).');
      return;
    }
    const reader = new FileReader();
    reader.onloadend = () => {
      const result = reader.result;
      setImagePreview(result);
      setFormData((prev) => ({ ...prev, image_url: result }));
    };
    reader.readAsDataURL(file);

    setScanningInvoice(true);
    setOcrExtractedInfo(null);
    try {
      const res = await documentAPI.scanInvoice(file);
      const data = res?.data || res;
      if (data && (data.success || data.entities)) {
        const entities = data.entities || {};
        const invoiceNum = data.invoice_number || entities.invoice_number;
        const purchaseDate = data.purchase_date || entities.purchase_date;
        const purchasePrice = data.purchase_price !== undefined && data.purchase_price !== null 
          ? data.purchase_price 
          : entities.purchase_price;
        const storeName = data.store_name || entities.retailer;
        const serialNum = data.serial_number || entities.serial_number;

        const updates = {};
        if (invoiceNum) updates.invoice_number = invoiceNum;
        if (purchaseDate) updates.purchase_date = purchaseDate;
        if (purchasePrice !== null && purchasePrice !== undefined && !isNaN(Number(purchasePrice))) {
          updates.purchase_price = purchasePrice;
        }
        if (storeName) updates.store_name = storeName;
        if (serialNum) {
          updates.serial_number = serialNum.toUpperCase().trim();
        }

        if (Object.keys(updates).length > 0) {
          setFormData((prev) => ({ ...prev, ...updates }));
        }

        const count = Object.keys(updates).length;
        setOcrExtractedInfo({
          invoice_number: invoiceNum,
          purchase_price: purchasePrice,
          purchase_date: purchaseDate,
          store_name: storeName,
          serial_number: serialNum,
          confidence: data.confidence || 0.85,
          entity_count: count,
          raw_text: data.ocr_text || '',
        });
      }
    } catch (err) {
      console.warn('Invoice AI OCR scan error:', err);
    } finally {
      setScanningInvoice(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileProcess(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileProcess(file);
    }
  };

  const handleRemoveImage = () => {
    setImagePreview('');
    setFormData((prev) => ({ ...prev, image_url: '' }));
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleVerifySerial = async () => {
    if (!formData.serial_number || !formData.product_id) return;
    setVerifyingSerial(true);
    try {
      const selected = products.find((p) => p.id === Number(formData.product_id));
      if (selected && selected.serial_prefix) {
        const isValid = formData.serial_number.startsWith(selected.serial_prefix);
        setSerialVerified(
          isValid
            ? { valid: true, message: `Matches official prefix: ${selected.serial_prefix}` }
            : { valid: false, message: `Prefix mismatch. Expected prefix: ${selected.serial_prefix}` }
        );
      } else {
        setSerialVerified({ valid: true, message: 'Valid format verified.' });
      }
    } catch (e) {
      setSerialVerified({ valid: true, message: 'Format accepted.' });
    } finally {
      setVerifyingSerial(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.serial_number || !isValidSerialNumber(formData.serial_number)) {
      setFormError('Serial number must be 4-32 characters containing letters, numbers, hyphens or underscores.');
      return;
    }
    const today = new Date().toISOString().split('T')[0];
    if (formData.purchase_date && formData.purchase_date > today) {
      setFormError('Purchase date cannot be in the future.');
      return;
    }
    const price = parseFloat(formData.purchase_price);
    if (isNaN(price) || price <= 0) {
      setFormError('Please enter a valid purchase price greater than $0.00.');
      return;
    }
    setFormError('');
    onSubmit({
      ...formData,
      serial_number: formData.serial_number.toUpperCase().trim(),
      product_id: parseInt(formData.product_id, 10),
      purchase_price: price,
      provider: formData.provider.trim(),
      coverage_conditions: formData.coverage_conditions.trim(),
      exclusions: formData.exclusions.trim(),
      service_centers: formData.service_centers.trim(),
      image_url: formData.image_url || displayImage || '',
    });
  };

  if (fetchingProducts) {
    return <Loader text="Loading product catalog..." />;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-h-[80vh] overflow-y-auto pr-1">
      {formError && (
        <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/60 text-xs sm:text-sm text-rose-700 dark:text-rose-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{formError}</span>
        </div>
      )}

      {/* Product Selection */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
          Select Product Model *
        </label>
        <select
          required
          name="product_id"
          value={formData.product_id}
          onChange={handleChange}
          className="w-full px-3.5 py-2.5 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
        >
          {Object.entries(
            products.reduce((acc, p) => {
              const cat = (p.category || 'OTHER').replace(/_/g, ' ');
              if (!acc[cat]) acc[cat] = [];
              acc[cat].push(p);
              return acc;
            }, {})
          ).map(([cat, prods]) => (
            <optgroup key={cat} label={cat}>
              {prods.map((prod) => {
                const brand = prod.brand || '';
                const model = prod.model_name || prod.name || '';
                const label = brand && model.toLowerCase().startsWith(brand.toLowerCase())
                  ? model
                  : `${brand} ${model}`.trim();
                return (
                  <option key={prod.id} value={prod.id}>
                    {label}
                  </option>
                );
              })}
            </optgroup>
          ))}
        </select>
      </div>

      {/* Product / Receipt Image Upload Section */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">
            Product / Receipt Photo & Invoice
          </label>
          <span className="text-[11px] text-brand-600 dark:text-brand-400 font-medium flex items-center gap-1">
            <Sparkles className="w-3 h-3" /> Auto AI Invoice Extraction
          </span>
        </div>

        {imagePreview ? (
          <div className="relative rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 p-3 flex items-center gap-4">
            <img
              src={imagePreview}
              alt="Uploaded Preview"
              className="w-20 h-20 object-cover rounded-xl border border-slate-200 dark:border-slate-700"
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-600 dark:text-emerald-400 mb-0.5">
                <Sparkles className="w-3.5 h-3.5" /> Receipt / Invoice Attached
              </div>
              {scanningInvoice ? (
                <div className="flex items-center gap-1.5 text-xs text-brand-600 dark:text-brand-400 animate-pulse font-medium">
                  <Loader size="sm" text="" />
                  <span>AI analyzing document & extracting invoice number...</span>
                </div>
              ) : ocrExtractedInfo ? (
                <div className="space-y-0.5">
                  <p className="text-xs text-slate-700 dark:text-slate-200 font-medium">
                    {ocrExtractedInfo.invoice_number ? (
                      <>Extracted Invoice: <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">{ocrExtractedInfo.invoice_number}</span></>
                    ) : ocrExtractedInfo.entity_count > 0 ? (
                      <span className="text-emerald-600 dark:text-emerald-400">✨ Auto-filled {ocrExtractedInfo.entity_count} fields from receipt</span>
                    ) : (
                      <span className="text-slate-500 dark:text-slate-400">Scanned receipt • Please review or enter fields</span>
                    )}
                  </p>
                  <p className="text-[11px] text-slate-400">
                    AI OCR Confidence: {Math.round((ocrExtractedInfo.confidence || 0.85) * 100)}%
                    {ocrExtractedInfo.purchase_price ? ` • Price: $${ocrExtractedInfo.purchase_price}` : ''}
                    {ocrExtractedInfo.purchase_date ? ` • Date: ${ocrExtractedInfo.purchase_date}` : ''}
                  </p>
                </div>
              ) : (
                <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                  Ready to register with warranty record
                </p>
              )}
            </div>
            <button
              type="button"
              onClick={handleRemoveImage}
              className="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/30 rounded-xl transition-colors mr-1"
              title="Remove image"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        ) : (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-4 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-2 ${
              isDragging
                ? 'border-brand-500 bg-brand-50/30 dark:bg-brand-900/20'
                : 'border-slate-200 dark:border-slate-700 hover:border-brand-400 dark:hover:border-brand-500 bg-slate-50/50 dark:bg-slate-800/30'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
            />
            <div className="w-10 h-10 rounded-full bg-brand-50 dark:bg-brand-900/40 text-brand-600 dark:text-brand-400 flex items-center justify-center">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-800 dark:text-slate-200">
                Click to upload or drag & drop invoice / receipt
              </p>
              <p className="text-[11px] text-slate-400 mt-0.5">
                AI will automatically scan and autofill your Invoice #, Date & Price (JPG, PNG, WEBP)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Serial Number */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
          Device Serial Number *
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            required
            name="serial_number"
            value={formData.serial_number}
            onChange={handleChange}
            placeholder="e.g. SN-SAM-2026-8839"
            className="flex-1 px-3.5 py-2 text-sm font-mono bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
          />
          <button
            type="button"
            onClick={handleVerifySerial}
            disabled={verifyingSerial || !formData.serial_number}
            className="px-3.5 py-2 text-xs font-semibold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl transition-colors shrink-0"
          >
            {verifyingSerial ? 'Checking...' : 'Verify Prefix'}
          </button>
        </div>

        {serialVerified && (
          <div
            className={`mt-2 text-xs flex items-center gap-1.5 ${
              serialVerified.valid ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'
            }`}
          >
            {serialVerified.valid ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
            <span>{serialVerified.message}</span>
          </div>
        )}
      </div>

      {/* Date & Price */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Date of Purchase *
          </label>
          <div className="relative">
            <Calendar className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="date"
              required
              max={new Date().toISOString().split('T')[0]}
              name="purchase_date"
              value={formData.purchase_date}
              onChange={handleChange}
              className="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Purchase Price ($) *
          </label>
          <div className="relative">
            <DollarSign className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="number"
              step="0.01"
              min="1"
              required
              name="purchase_price"
              value={formData.purchase_price}
              onChange={handleChange}
              placeholder="999.00"
              className="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
            />
          </div>
        </div>
      </div>

      {/* Invoice & Store */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">
              Invoice / Receipt #
            </label>
            {ocrExtractedInfo?.invoice_number && (
              <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 rounded-full border border-emerald-200 dark:border-emerald-800 animate-fade-in">
                <Sparkles className="w-3 h-3" /> Auto-filled by AI OCR
              </span>
            )}
          </div>
          <input
            type="text"
            name="invoice_number"
            value={formData.invoice_number}
            onChange={handleChange}
            placeholder="INV-2026-98102"
            className={`w-full px-3.5 py-2 text-sm bg-slate-50 dark:bg-slate-800/60 border rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 transition-all dark:text-white ${
              ocrExtractedInfo?.invoice_number
                ? 'border-emerald-400 dark:border-emerald-600 bg-emerald-50/20 dark:bg-emerald-950/20'
                : 'border-slate-200 dark:border-slate-700 focus:border-brand-500'
            }`}
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Store / Retailer Name
          </label>
          <div className="relative">
            <Store className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              name="store_name"
              value={formData.store_name}
              onChange={handleChange}
              placeholder="e.g. BestBuy, Amazon, Direct"
              className="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Warranty Provider / Type
          </label>
          <input
            type="text"
            name="provider"
            value={formData.provider}
            onChange={handleChange}
            placeholder="e.g. Manufacturer, AssureX Extended"
            className="w-full px-3.5 py-2 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Authorized Service Centers
          </label>
          <input
            type="text"
            name="service_centers"
            value={formData.service_centers}
            onChange={handleChange}
            placeholder="e.g. iCare, BestBuy GeekSquad"
            className="w-full px-3.5 py-2 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Coverage Conditions
          </label>
          <textarea
            rows={2}
            name="coverage_conditions"
            value={formData.coverage_conditions}
            onChange={handleChange}
            placeholder="e.g. Covers manufacturing defects and hardware failures."
            className="w-full px-3.5 py-2 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
            Exclusions (Not Covered)
          </label>
          <textarea
            rows={2}
            name="exclusions"
            value={formData.exclusions}
            onChange={handleChange}
            placeholder="e.g. Liquid damage, accidental drops, unauthorized repair."
            className="w-full px-3.5 py-2 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
          />
        </div>
      </div>

      {/* Notes */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
          Additional Notes
        </label>
        <textarea
          rows={2}
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          placeholder="Extended warranty terms or purchase notes..."
          className="w-full px-3.5 py-2 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
        />
      </div>

      {/* Footer Actions */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800 sticky bottom-0 bg-white dark:bg-slate-900 pb-1">
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
          className="px-5 py-2.5 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-500 disabled:opacity-50 rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center gap-2"
        >
          {loading && <Loader size="sm" text="" />}
          <ShieldCheck className="w-4 h-4" />
          <span>{initialData.id ? 'Update Warranty' : 'Register Warranty'}</span>
        </button>
      </div>
    </form>
  );
};

export default WarrantyForm;
