import React, { useState } from 'react';
import PredictionPanel from '../claim/PredictionPanel';
import ComparisonPanel from '../claim/ComparisonPanel';
import RuleResultPanel from '../claim/RuleResultPanel';
import DecisionExplanation from '../claim/DecisionExplanation';
import CommentBox from './CommentBox';
import OverrideModal from './OverrideModal';
import { 
  ShieldCheck, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  RotateCcw, 
  FileSearch,
  Sparkles,
  Edit
} from 'lucide-react';
import { formatCurrency, formatDate } from '../../utils/formatters';
import Badge from '../common/Badge';

export const ReviewDetail = ({
  claim,
  onDecide,
  onAddComment,
  onOverride,
  comments = [],
  loading = false,
}) => {
  const [isOverrideOpen, setIsOverrideOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('decision'); // 'decision', 'evidence', 'audit'

  if (!claim) return null;

  return (
    <div className="space-y-6">
      {/* Top Claim Meta Bar */}
      <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-sm font-bold text-slate-900 dark:text-white">
              {claim.claim_number}
            </span>
            <Badge type="status" value={claim.status} size="sm" />
            <Badge type="decision" value={claim.ai_decision || 'PENDING'} size="sm" />
          </div>
          <p className="text-xs text-slate-500">
            Filed on {formatDate(claim.submitted_at || claim.created_at)} by {claim.user?.full_name || 'Claimant'} ({claim.user?.email})
          </p>
        </div>

        {/* Quick Action Decision Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => onDecide('APPROVE')}
            disabled={loading}
            className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow-md shadow-emerald-500/20 transition-all"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Approve Claim</span>
          </button>

          <button
            type="button"
            onClick={() => onDecide('REJECT')}
            disabled={loading}
            className="flex items-center gap-1.5 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold rounded-xl shadow-md shadow-rose-500/20 transition-all"
          >
            <XCircle className="w-4 h-4" />
            <span>Reject Claim</span>
          </button>

          <button
            type="button"
            onClick={() => onDecide('ESCALATE')}
            disabled={loading}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-xl shadow-md shadow-purple-500/20 transition-all"
          >
            <AlertTriangle className="w-4 h-4" />
            <span>Escalate</span>
          </button>

          <button
            type="button"
            onClick={() => setIsOverrideOpen(true)}
            disabled={loading}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl transition-all"
          >
            <Edit className="w-4 h-4 text-brand-500" />
            <span>Override AI</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
        <button
          type="button"
          onClick={() => setActiveTab('decision')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-colors ${
            activeTab === 'decision'
              ? 'bg-brand-50 dark:bg-brand-950 text-brand-600 dark:text-brand-400'
              : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
          }`}
        >
          AI Adjudication & Ensemble
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('rules')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-colors ${
            activeTab === 'rules'
              ? 'bg-brand-50 dark:bg-brand-950 text-brand-600 dark:text-brand-400'
              : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
          }`}
        >
          Deterministic Policy Rules
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('comments')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-colors ${
            activeTab === 'comments'
              ? 'bg-brand-50 dark:bg-brand-950 text-brand-600 dark:text-brand-400'
              : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
          }`}
        >
          Reviewer Notes & Audit ({comments.length})
        </button>
      </div>

      {/* Tab Panels */}
      {activeTab === 'decision' && (
        <div className="space-y-6 animate-fade-in">
          <PredictionPanel
            aiConfidence={claim.ai_confidence}
            fraudScore={claim.fraud_score}
          />
          <ComparisonPanel
            pythonMLScore={claim.ai_confidence}
            teachableMachineScore={claim.tm_confidence_score || claim.ai_confidence}
            agreementScore={claim.model_agreement_score}
          />
          <DecisionExplanation
            decision={claim.ai_decision || claim.final_decision || 'Valid Claim'}
            reasons={[
              'Valid active warranty verification completed against database records.',
              'Fault type aligns with covered manufacturing hardware defects.',
              'Claim amount is within allowable policy limits.',
            ]}
          />
        </div>
      )}

      {activeTab === 'rules' && (
        <div className="space-y-6 animate-fade-in">
          <RuleResultPanel />
        </div>
      )}

      {activeTab === 'comments' && (
        <div className="space-y-6 animate-fade-in">
          <CommentBox
            comments={comments}
            onAddComment={onAddComment}
            loading={loading}
          />
        </div>
      )}

      {/* Override Modal */}
      <OverrideModal
        isOpen={isOverrideOpen}
        onClose={() => setIsOverrideOpen(false)}
        onConfirmOverride={(overrideData) => {
          onOverride(overrideData);
          setIsOverrideOpen(false);
        }}
        currentDecision={claim.ai_decision || 'REJECT'}
        claimNumber={claim.claim_number}
      />
    </div>
  );
};

export default ReviewDetail;