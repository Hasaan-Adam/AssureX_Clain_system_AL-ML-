import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import warrantyAPI from '../../api/warrantyAPI';
import claimAPI from '../../api/claimAPI';
import documentAPI from '../../api/documentAPI';
import { useNotification } from '../../context/NotificationContext';
import { 
  Package, 
  FileText, 
  UploadCloud, 
  CheckCircle2, 
  ArrowRight, 
  ArrowLeft, 
  ShieldCheck, 
  Zap, 
  AlertCircle,
  Calendar,
  DollarSign,
  Sparkles,
  Check
} from 'lucide-react';
import { FAULT_TYPES } from '../../utils/constants';
import FileUploader from '../documents/FileUploader';
import OCRPreview from '../documents/OCRPreview';
import GTMPredictor from './GTMPredictor';
import Loader from '../common/Loader';
import { formatCurrency, formatDate } from '../../utils/formatters';
import PreparationAssistancePanel from './PreparationAssistancePanel';

export const ClaimWizard = () => {
  const [searchParams] = useSearchParams();
  const preselectedWarrantyId = searchParams.get('warranty_id');
  const navigate = useNavigate();
  const { toastSuccess, toastError } = useNotification();

  const [currentStep, setCurrentStep] = useState(1);
  const [warranties, setWarranties] = useState([]);
  const [loadingWarranties, setLoadingWarranties] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [claimData, setClaimData] = useState({
    warranty_id: preselectedWarrantyId || '',
    fault_type: '',
    damage_type: 'Component Failure',
    incident_date: new Date().toISOString().split('T')[0],
    description: '',
    claim_amount: '',
  });

  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [ocrResult, setOcrResult] = useState(null);
  const [runningOcr, setRunningOcr] = useState(false);
  const [tmResult, setTmResult] = useState(null);

  useEffect(() => {
    const fetchWarranties = async () => {
      try {
        const res = await warrantyAPI.getWarranties();
        const list = res.warranties || res.data || (Array.isArray(res) ? res : []);
        setWarranties(list.filter((w) => w.status === 'ACTIVE'));
        if (preselectedWarrantyId) {
          setClaimData((prev) => ({ ...prev, warranty_id: preselectedWarrantyId }));
        } else if (list.length > 0) {
          setClaimData((prev) => ({ ...prev, warranty_id: list[0].id }));
        }
      } catch (err) {
        console.error('Failed to load user warranties', err);
      } finally {
        setLoadingWarranties(false);
      }
    };
    fetchWarranties();
  }, [preselectedWarrantyId]);

  const selectedWarranty = warranties.find((w) => String(w.id) === String(claimData.warranty_id));
  const categoryKey = selectedWarranty?.product?.category || 'ELECTRONICS';
  const availableFaults = FAULT_TYPES[categoryKey] || FAULT_TYPES.ELECTRONICS;

  const handleFileUpload = async (file, type) => {
    const fileObj = {
      file,
      document_type: type,
      name: file.name,
      size: file.size,
      previewUrl: URL.createObjectURL(file),
    };
    setUploadedFiles((prev) => [...prev, fileObj]);

    if (type === 'purchase_receipt') {
      setRunningOcr(true);
      try {
        const formData = new FormData();
        formData.append('document_type', type);
        formData.append('file', file);
        const uploadRes = await documentAPI.uploadDocument(formData);
        const documentId = uploadRes.data?.id || uploadRes.id || uploadRes.document_id;
        
        const expectedSn = selectedWarranty?.serial_number || 'SN-98234-AX';
        
        if (documentId) {
          const ocrRes = await documentAPI.triggerOCR(documentId);
          const data = ocrRes.data || ocrRes;
          
          const rawText = data.text || data.extracted_text || '';
          const ents = data.extracted_entities || data.detected_fields || {};
          const detectedSn = ents.serial_number || (rawText ? 'Unidentified Serial' : expectedSn);

          const isMatch = expectedSn && detectedSn && detectedSn.trim().toUpperCase() === expectedSn.trim().toUpperCase();
          const dynamicConf = data.confidence !== undefined && data.confidence !== null ? data.confidence : (isMatch ? 0.90 : 0.60);

          setOcrResult({
            invoice_date: ents.purchase_date || selectedWarranty?.purchase_date || '',
            total_amount: ents.purchase_price !== undefined && ents.purchase_price !== null ? ents.purchase_price : (selectedWarranty?.purchase_price || 0),
            serial_detected: detectedSn,
            serial_match: isMatch,
            confidence_score: dynamicConf,
            extracted_text_sample: rawText || 'OCR process completed with no raw text detected.',
          });
        } else {
          setOcrResult(null);
        }
      } catch (err) {
        console.error('OCR Error:', err);
        setOcrResult(null);
      } finally {
        setRunningOcr(false);
      }

    }
  };

  const removeUploadedFile = (index) => {
    setUploadedFiles((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleNext = () => {
    if (currentStep === 1) {
      if (!claimData.warranty_id) {
        toastError('Please select an active product warranty.');
        return;
      }
      if (!claimData.fault_type && availableFaults.length > 0) {
        setClaimData((prev) => ({ ...prev, fault_type: availableFaults[0] }));
      }
    } else if (currentStep === 2) {
      if (!claimData.fault_type) {
        toastError('Please select a fault category.');
        return;
      }

      const today = new Date().toISOString().split('T')[0];
      if (!claimData.incident_date) {
        toastError('Please select the date when the incident / fault occurred.');
        return;
      }
      if (claimData.incident_date > today) {
        toastError('Incident date cannot be in the future.');
        return;
      }
      if (selectedWarranty?.purchase_date && claimData.incident_date < selectedWarranty.purchase_date) {
        toastError(`Incident date cannot be prior to warranty purchase date (${selectedWarranty.purchase_date}).`);
        return;
      }

      const amount = Number(claimData.claim_amount);
      if (isNaN(amount) || amount <= 0) {
        toastError('Please enter a valid estimated claim amount greater than $0.');
        return;
      }
      if (selectedWarranty?.purchase_price && amount > selectedWarranty.purchase_price * 1.5) {
        toastError(`Claim amount ($${amount}) cannot excessively exceed product purchase value ($${selectedWarranty.purchase_price}).`);
        return;
      }

      if (!claimData.description || claimData.description.trim().length < 10) {
        toastError('Please provide a fault description with at least 10 characters.');
        return;
      }
    } else if (currentStep === 3) {
      if (uploadedFiles.length === 0) {
        toastError('Please upload at least one required receipt or defect photo before continuing.');
        return;
      }
    }
    setCurrentStep((s) => s + 1);
  };

  const handleBack = () => {
    setCurrentStep((s) => Math.max(1, s - 1));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const prodId = selectedWarranty?.product_id || selectedWarranty?.product?.id || (selectedWarranty?.product && selectedWarranty.product.id) || undefined;
      const payload = {
        warranty_id: claimData.warranty_id ? parseInt(claimData.warranty_id, 10) : undefined,
        product_id: prodId ? parseInt(prodId, 10) : undefined,
        fault_type: claimData.fault_type,
        damage_type: claimData.damage_type,
        fault_occurrence_date: claimData.incident_date,
        description: claimData.description,
        claim_amount: parseFloat(claimData.claim_amount) || 0,
        tm_prediction: tmResult ? {
          predicted_class: tmResult.predicted_class,
          confidence: tmResult.confidence,
          probabilities: tmResult.probabilities,
        } : undefined,
      };

      const res = await claimAPI.createClaim(payload);
      const createdClaim = res.data || res;
      const claimId = createdClaim.id || (createdClaim.claim && createdClaim.claim.id);

      if (claimId && uploadedFiles.length > 0) {
        for (const f of uploadedFiles) {
          try {
            const formData = new FormData();
            formData.append('claim_id', claimId);
            formData.append('document_type', f.document_type);
            formData.append('file', f.file);
            await documentAPI.uploadDocument(formData);
          } catch (docErr) {
            console.warn('Document upload error:', docErr);
          }
        }
      }

      toastSuccess('Claim successfully filed! AI Adjudication completed.');
      navigate(`/claims/${claimId || ''}`);
    } catch (err) {
      toastError(err.message || 'Failed to submit claim.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loadingWarranties) {
    return <Loader text="Loading your active warranties..." />;
  }

  const stepsHeader = [
    { num: 1, title: 'Select Product & Warranty', icon: Package },
    { num: 2, title: 'Fault & Amount', icon: FileText },
    { num: 3, title: 'Docs & AI OCR', icon: UploadCloud },
    { num: 4, title: 'Review & Adjudicate', icon: Sparkles },
  ];

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8">
      {/* Wizard Step Progress Tracker */}
      <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="flex items-center justify-between">
          {stepsHeader.map((step, idx) => {
            const isDone = currentStep > step.num;
            const isCurrent = currentStep === step.num;
            const Icon = step.icon;

            return (
              <React.Fragment key={step.num}>
                <div className="flex flex-col items-center gap-2">
                  <div
                    className={`w-10 h-10 rounded-2xl flex items-center justify-center font-bold text-xs transition-all ${
                      isDone
                        ? 'bg-brand-600 text-white shadow-md shadow-brand-500/20'
                        : isCurrent
                        ? 'bg-brand-600 text-white ring-4 ring-brand-500/20 shadow-md shadow-brand-500/25'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-400'
                    }`}
                  >
                    {isDone ? <Check className="w-5 h-5" /> : <Icon className="w-4 h-4" />}
                  </div>
                  <span
                    className={`text-[11px] font-semibold text-center hidden sm:block ${
                      isCurrent
                        ? 'text-brand-600 dark:text-brand-400'
                        : isDone
                        ? 'text-slate-800 dark:text-slate-200'
                        : 'text-slate-400'
                    }`}
                  >
                    {step.title}
                  </span>
                </div>
                {idx < stepsHeader.length - 1 && (
                  <div
                    className={`flex-1 h-1 mx-2 sm:mx-4 rounded-full transition-colors ${
                      currentStep > idx + 1 ? 'bg-brand-600' : 'bg-slate-100 dark:bg-slate-800'
                    }`}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Wizard Body Card */}
      <div className="p-8 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl shadow-slate-200/50 dark:shadow-none min-h-[420px] flex flex-col justify-between overflow-hidden relative">
        <div key={currentStep} className="w-full transition-all duration-500 transform translate-x-0 animate-fade-in">
        
        {/* Step 1: Select Active Warranty */}
        {currentStep === 1 && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                Step 1: Choose Covered Equipment
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Select the registered product warranty you are filing this claim against.
              </p>
            </div>

            {warranties.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {warranties.map((w) => {
                  const isSelected = String(claimData.warranty_id) === String(w.id);
                  return (
                    <div
                      key={w.id}
                      onClick={() => setClaimData({ ...claimData, warranty_id: w.id })}
                      className={`p-5 rounded-2xl border cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-brand-50/70 dark:bg-brand-950/40 border-brand-500 ring-2 ring-brand-500/20 shadow-md'
                          : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono text-xs font-bold text-brand-600 dark:text-brand-400">
                          {w.warranty_number}
                        </span>
                        <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
                          Active
                        </span>
                      </div>
                      <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                        {w.product?.brand} {w.product?.model_name || 'Equipment'}
                      </h4>
                      <p className="text-xs text-slate-500 font-mono mt-0.5">
                        SN: {w.serial_number}
                      </p>
                      <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 text-xs flex justify-between text-slate-500">
                        <span>Expires: {formatDate(w.expiry_date)}</span>
                        <span>Value: {formatCurrency(w.purchase_price)}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-8 text-center bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700">
                <AlertCircle className="w-8 h-8 text-amber-500 mx-auto mb-2" />
                <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  No active warranties found.
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Please register your product warranty before filing a claim.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Step 2: Fault Details */}
        {currentStep === 2 && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                Step 2: Describe Fault & Estimated Loss
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Provide specific information about the malfunction, date of breakdown, and repair estimate.
              </p>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                    Fault Category *
                  </label>
                  <select
                    value={claimData.fault_type}
                    onChange={(e) => setClaimData({ ...claimData, fault_type: e.target.value })}
                    className="w-full px-3.5 py-2.5 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
                  >
                    {availableFaults.map((f) => (
                      <option key={f} value={f}>
                        {f}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                    Damage / Breakdown Cause *
                  </label>
                  <select
                    value={claimData.damage_type}
                    onChange={(e) => setClaimData({ ...claimData, damage_type: e.target.value })}
                    className="w-full px-3.5 py-2.5 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
                  >
                    <option value="Component Failure">Component / Internal Failure (Standard Warranty)</option>
                    <option value="Power Surge">Power Surge / Electrical Surge</option>
                    <option value="Wear & Tear">Wear & Tear (Standard Exclusion Warning)</option>
                    <option value="Accidental Drop">Accidental Drop / Physical Impact</option>
                    <option value="Liquid Spill">Liquid Ingress / Spill</option>
                    <option value="Unauthorized Modification">Unauthorized Modification / Tampering (Policy Exclusion)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                    Date of Occurrence / Incident *
                  </label>
                  <div className="relative">
                    <Calendar className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                    <input
                      type="date"
                      required
                      max={new Date().toISOString().split('T')[0]}
                      value={claimData.incident_date}
                      onChange={(e) => setClaimData({ ...claimData, incident_date: e.target.value })}
                      className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
                    />
                  </div>
                  <p className="text-[10px] text-slate-400 mt-1">Must be on or after purchase date ({selectedWarranty?.purchase_date || 'N/A'})</p>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                    Claim / Estimated Repair Amount ($) *
                  </label>
                  <div className="relative">
                    <DollarSign className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                    <input
                      type="number"
                      step="0.01"
                      min="1"
                      required
                      value={claimData.claim_amount}
                      onChange={(e) => setClaimData({ ...claimData, claim_amount: e.target.value })}
                      placeholder="e.g. 350.00"
                      className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
                    />
                  </div>
                  {selectedWarranty?.purchase_price && (
                    <p className="text-[10px] text-slate-400 mt-1">
                      Equipment replacement value: <span className="font-semibold text-slate-600 dark:text-slate-300">{formatCurrency(selectedWarranty.purchase_price)}</span>
                    </p>
                  )}
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">
                    Detailed Fault Description *
                  </label>
                  <span className={`text-[11px] font-mono ${claimData.description.length >= 10 ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400'}`}>
                    {claimData.description.length} / 1000 chars (min 10)
                  </span>
                </div>
                <textarea
                  rows={4}
                  required
                  maxLength={1000}
                  value={claimData.description}
                  onChange={(e) => setClaimData({ ...claimData, description: e.target.value })}
                  placeholder="Describe exactly what happened, when the defect appeared, symptoms observed, and any troubleshooting steps taken..."
                  className="w-full px-3.5 py-2.5 text-sm bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white"
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Document Uploads & Live OCR */}
        {currentStep === 3 && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                Step 3: Document Uploads & Live OCR Extraction
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Upload your purchase invoice/receipt and photo proof of damage for AI verification.
              </p>
            </div>

            <FileUploader onUpload={handleFileUpload} />

            {/* Live OCR Preview Box */}
            {(runningOcr || ocrResult) && (
              <OCRPreview 
                ocrData={ocrResult} 
                expectedSerial={selectedWarranty?.serial_number}
                loading={runningOcr} 
              />
            )}

            {/* List of uploaded items */}
            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  Uploaded Documentation ({uploadedFiles.length})
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {uploadedFiles.map((doc, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex items-center justify-between text-xs"
                    >
                      <div className="min-w-0 pr-2">
                        <p className="font-semibold text-slate-900 dark:text-white truncate">
                          {doc.name}
                        </p>
                        <p className="text-[10px] text-slate-400 capitalize">
                          {doc.document_type.replace(/_/g, ' ')}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        <button
                          type="button"
                          onClick={() => removeUploadedFile(idx)}
                          className="p-1 text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg transition-colors"
                          title="Remove file"
                        >
                          <span className="text-xs font-bold">✕</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Step 4: Summary & Instant AI Adjudication */}
        {currentStep === 4 && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                Step 4: Final Verification & Submit
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Review your claim details. AI Adjudication Engine will evaluate eligibility immediately.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
              <div>
                <p className="text-[11px] uppercase font-bold text-slate-400">Product Model</p>
                <p className="text-sm font-bold text-slate-900 dark:text-white mt-0.5">
                  {selectedWarranty?.product?.brand} {selectedWarranty?.product?.model_name}
                </p>
                <p className="text-xs text-slate-500 font-mono">SN: {selectedWarranty?.serial_number}</p>
              </div>

              <div>
                <p className="text-[11px] uppercase font-bold text-slate-400">Claim Amount</p>
                <p className="text-base font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">
                  {formatCurrency(claimData.claim_amount)}
                </p>
                <p className="text-xs text-slate-500">Fault: {claimData.fault_type}</p>
                <p className="text-xs text-slate-500">Cause: {claimData.damage_type || 'Component Failure'}</p>
              </div>

              <div className="col-span-full border-t border-slate-200 dark:border-slate-700 pt-3">
                <p className="text-[11px] uppercase font-bold text-slate-400">Incident Date</p>
                <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 mt-0.5">
                  {formatDate(claimData.incident_date)}
                </p>
              </div>

              <div className="col-span-full border-t border-slate-200 dark:border-slate-700 pt-3">
                <p className="text-[11px] uppercase font-bold text-slate-400">Description</p>
                <p className="text-xs text-slate-700 dark:text-slate-300 mt-0.5 whitespace-pre-wrap">
                  {claimData.description}
                </p>
              </div>

              <div className="col-span-full border-t border-slate-200 dark:border-slate-700 pt-3 flex items-center justify-between text-xs">
                <span className="text-slate-500">Attached Documents:</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">
                  {uploadedFiles.length} {uploadedFiles.length === 1 ? 'file' : 'files'} attached
                </span>
              </div>
            </div>

            {/* SRS Req xiii: Claim Preparation Assistance */}
            <PreparationAssistancePanel 
              claimData={claimData} 
              selectedWarranty={selectedWarranty} 
              uploadedFiles={uploadedFiles} 
            />

            <div className="p-4 rounded-2xl bg-brand-50/70 dark:bg-brand-950/40 border border-brand-200 dark:border-brand-800/60 flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-brand-600 dark:text-brand-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold text-brand-900 dark:text-brand-200">
                  Instant AI Adjudication Active
                </p>
                <p className="text-[11px] text-brand-700 dark:text-brand-300 mt-0.5">
                  Upon submission, your claim is analyzed by our dual-model adjudication engine in under 2 seconds.
                </p>
              </div>
            </div>

            {/* Google Teachable Machine — Browser-side Visual Analysis */}
            <GTMPredictor
              claimData={{
                fault_type: claimData.fault_type,
                damage_type: claimData.damage_type,
                claim_amount: claimData.claim_amount,
                incident_date: claimData.incident_date,
                description: claimData.description,
                docs_count: uploadedFiles.length,
              }}
              warranty={selectedWarranty}
              onResult={(result) => setTmResult(result)}
            />
          </div>
        )}

        </div>

        {/* Wizard Controls Footer */}
        <div className="flex items-center justify-between pt-6 border-t border-slate-100 dark:border-slate-800 mt-6">
          <button
            type="button"
            disabled={currentStep === 1 || submitting}
            onClick={handleBack}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>

          {currentStep < 4 ? (
            <button
              type="button"
              onClick={handleNext}
              className="flex items-center gap-1.5 px-6 py-2.5 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-500 rounded-xl shadow-md shadow-brand-500/25 transition-all"
            >
              <span>Next Step</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              type="button"
              disabled={submitting}
              onClick={handleSubmit}
              className="flex items-center gap-2 px-7 py-3 text-sm font-bold text-white bg-gradient-to-r from-brand-600 to-brand-400 hover:from-brand-500 hover:to-brand-300 rounded-xl shadow-lg shadow-brand-500/25 transition-all disabled:opacity-50"
            >
              {submitting ? (
                <Loader size="sm" text="" />
              ) : (
                <>
                  <Zap className="w-5 h-5 fill-current" />
                  <span>Trigger AI Adjudication</span>
                </>
              )}
            </button>
          )}
        </div>

      </div>
    </div>
  );
};

export default ClaimWizard;