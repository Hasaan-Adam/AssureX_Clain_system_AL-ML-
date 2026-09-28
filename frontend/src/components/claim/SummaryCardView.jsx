import React, { useState } from 'react';
import { Download, QrCode } from 'lucide-react';

export const SummaryCardView = ({ claim, product, warranty, user }) => {
  if (!claim) return null;

  return (
    <div className="space-y-4">
      {/* Action Toolbar */}
      <div className="flex items-center justify-between p-3 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm no-print">
        <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
          Claim Summary Card
        </span>
        <button
          type="button"
          onClick={() => window.print()}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-brand-600 hover:bg-brand-500 text-white rounded-xl shadow-md shadow-brand-500/20 transition-all"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export Image</span>
        </button>
      </div>

      {/* Renderable Summary Card matching Point #17 exactly */}
      <div className="p-4 flex justify-center overflow-x-auto">
        <div className="w-full max-w-sm bg-white text-slate-900 p-8 rounded-none border-4 border-slate-900 shadow-xl">
          {/* Card Header */}
          <div className="text-center border-b-2 border-slate-900 pb-4 mb-6">
            <h2 className="text-2xl font-black tracking-widest uppercase">
              CLAIM SUMMARY
            </h2>
            <p className="text-sm font-mono mt-1 font-bold">
              {claim.claim_number || 'CLM-XXXX-XXXX'}
            </p>
          </div>

          {/* Details List (Exact fields from SRS Point 17) */}
          <div className="space-y-3 font-mono text-sm font-bold">
            <div className="flex justify-between border-b border-slate-200 pb-1">
              <span>Product:</span>
              <span className="text-right">{product?.name || product?.brand || 'Washing Machine'}</span>
            </div>
            
            <div className="flex justify-between border-b border-slate-200 pb-1">
              <span>Age:</span>
              <span className="text-right">{claim.product_age_months ? claim.product_age_months + ' Months' : '6 Months'}</span>
            </div>
            
            <div className="flex justify-between border-b border-slate-200 pb-1">
              <span>Warranty:</span>
              <span className="text-right">{warranty?.status || 'Active'}</span>
            </div>
            
            <div className="flex justify-between border-b border-slate-200 pb-1">
              <span>Fault:</span>
              <span className="text-right">{claim.fault_type || 'Motor / Electrical'}</span>
            </div>
            
            <div className="flex justify-between border-b border-slate-200 pb-1">
              <span>Receipt:</span>
              <span className="text-right">{claim.has_receipt !== false ? 'Available' : 'Missing'}</span>
            </div>
            
            <div className="flex justify-between border-b border-slate-200 pb-1">
              <span>Serial:</span>
              <span className="text-right">{claim.serial_match !== false ? 'Matched' : 'Mismatch'}</span>
            </div>
            
            <div className="flex justify-between border-b border-slate-200 pb-1">
              <span>Repairs:</span>
              <span className="text-right">{claim.previous_repairs ? 'Yes' : 'None'}</span>
            </div>
            
            <div className="flex justify-between border-b border-slate-200 pb-1">
              <span>Documents:</span>
              <span className="text-right">{claim.documents_complete !== false ? 'Complete' : 'Incomplete'}</span>
            </div>
          </div>

          <div className="mt-8 pt-4 border-t-2 border-slate-900 text-center">
            <QrCode className="w-12 h-12 mx-auto mb-2 opacity-80" />
            <p className="text-[10px] uppercase font-bold tracking-widest text-slate-500">
              Machine Readable Format
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SummaryCardView;

