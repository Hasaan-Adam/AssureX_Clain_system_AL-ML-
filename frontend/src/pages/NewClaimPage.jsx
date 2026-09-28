import React from 'react';
import ClaimWizard from '../components/claim/ClaimWizard';

export const NewClaimPage = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="text-center max-w-xl mx-auto">
        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
          Submit Warranty Claim
        </h2>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Our dual-model AI adjudication engine evaluates fault proof, warranty eligibility, and OCR invoice data in seconds.
        </p>
      </div>

      <ClaimWizard />
    </div>
  );
};

export default NewClaimPage;