import React from 'react';
import { AlertCircle, FilePlus, CheckCircle2, Upload } from 'lucide-react';
import { DOCUMENT_TYPES } from '../../utils/constants';

export const MissingDocsPanel = ({
  uploadedDocs = [],
  onUploadMissing = null,
}) => {
  const uploadedTypes = uploadedDocs.map((d) => d.document_type);

  const missingRequired = DOCUMENT_TYPES.filter(
    (type) => type.required && !uploadedTypes.includes(type.id)
  );

  if (missingRequired.length === 0) {
    return (
      <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/60 flex items-center gap-3">
        <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
        <div>
          <p className="text-xs font-bold text-emerald-900 dark:text-emerald-200">
            All Mandatory Documents Uploaded
          </p>
          <p className="text-[11px] text-emerald-700 dark:text-emerald-400">
            Document completeness check passed (100%).
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-5 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/60 space-y-3">
      <div className="flex items-start gap-2.5">
        <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs font-bold text-amber-900 dark:text-amber-200">
            Missing Mandatory Documentation
          </h4>
          <p className="text-[11px] text-amber-700 dark:text-amber-400">
            The following documentation is mandatory under the policy to complete auto-adjudication:
          </p>
        </div>
      </div>

      <div className="space-y-2">
        {missingRequired.map((doc) => (
          <div
            key={doc.id}
            className="flex items-center justify-between p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-amber-200 dark:border-amber-900 text-xs"
          >
            <span className="font-semibold text-slate-800 dark:text-slate-200">
              {doc.label}
            </span>
            {onUploadMissing && (
              <button
                type="button"
                onClick={() => onUploadMissing(doc.id)}
                className="flex items-center gap-1 px-2.5 py-1 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-[11px] font-semibold transition-colors"
              >
                <Upload className="w-3 h-3" />
                Upload
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default MissingDocsPanel;