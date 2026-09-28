import React, { useState, useRef } from 'react';
import { UploadCloud, File, FileText, Image, CheckCircle, X, AlertCircle } from 'lucide-react';
import { DOCUMENT_TYPES } from '../../utils/constants';
import { formatFileSize } from '../../utils/formatters';

export const FileUploader = ({
  onUpload,
  accept = '.pdf,.png,.jpg,.jpeg,.webp',
  maxSizeMB = 10,
  disabled = false,
  claimId = null,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedType, setSelectedType] = useState(DOCUMENT_TYPES[0].id);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'webp'];
  const ALLOWED_MIME_TYPES = [
    'application/pdf',
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/webp',
  ];

  const validateAndSelectFile = (file) => {
    setError(null);
    if (!file) return;

    const ext = file.name.split('.').pop()?.toLowerCase();
    const isValidExt = ALLOWED_EXTENSIONS.includes(ext);
    const isValidMime = ALLOWED_MIME_TYPES.includes(file.type) || (file.type === '' && isValidExt);

    if (!isValidExt || !isValidMime) {
      setError(`Invalid file format (.${ext || 'unknown'}). Please upload a valid PDF, PNG, JPG, or WEBP file.`);
      return;
    }

    const maxBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxBytes) {
      setError(`File size (${formatFileSize(file.size)}) exceeds maximum limit of ${maxSizeMB}MB.`);
      return;
    }

    setSelectedFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSelectFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSelectFile(e.target.files[0]);
    }
  };

  const handleUploadClick = () => {
    if (!selectedFile) return;
    onUpload(selectedFile, selectedType);
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Document Category
          </label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            disabled={disabled}
            className="text-xs font-semibold px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none dark:text-white"
          >
            {DOCUMENT_TYPES.map((type) => (
              <option key={type.id} value={type.id}>
                {type.label} {type.required ? '*' : ''}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
          dragActive
            ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-950/20 scale-[0.99]'
            : 'border-slate-200 dark:border-slate-800 hover:border-brand-400 bg-slate-50/50 dark:bg-slate-900/50'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          disabled={disabled}
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center gap-2">
          <div className="w-12 h-12 rounded-2xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 flex items-center justify-center">
            <UploadCloud className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              Click to browse or drag & drop files here
            </p>
            <p className="text-xs text-slate-400 mt-0.5">
              Supports PDF, PNG, JPG, WEBP (Max {maxSizeMB}MB)
            </p>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300 text-xs border border-rose-200 dark:border-rose-900">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Staged File Card */}
      {selectedFile && (
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm animate-slide-up">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-brand-100 dark:bg-brand-900/60 text-brand-600 flex items-center justify-center">
              {selectedFile.type.includes('pdf') ? (
                <FileText className="w-5 h-5" />
              ) : (
                <Image className="w-5 h-5" />
              )}
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate max-w-xs">
                {selectedFile.name}
              </p>
              <p className="text-[11px] text-slate-400">
                {formatFileSize(selectedFile.size)} • Type: {selectedType.replace(/_/g, ' ')}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={clearSelection}
              className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={handleUploadClick}
              className="px-3.5 py-1.5 bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold rounded-lg shadow-md shadow-brand-500/20 transition-all"
            >
              Confirm Upload
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUploader;