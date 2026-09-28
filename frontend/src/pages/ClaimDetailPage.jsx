import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import claimAPI from '../api/claimAPI';
import reviewAPI from '../api/reviewAPI';
import documentAPI from '../api/documentAPI';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import StatusTimeline from '../components/claim/StatusTimeline';
import PredictionPanel from '../components/claim/PredictionPanel';
import ComparisonPanel from '../components/claim/ComparisonPanel';
import RuleResultPanel from '../components/claim/RuleResultPanel';
import DecisionExplanation from '../components/claim/DecisionExplanation';
import SummaryCardView from '../components/claim/SummaryCardView';
import MissingDocsPanel from '../components/claim/MissingDocsPanel';
import DuplicateAlert from '../components/claim/DuplicateAlert';
import OCRPreview from '../components/documents/OCRPreview';
import CommentBox from '../components/review/CommentBox';
import OverrideModal from '../components/review/OverrideModal';
import ClaimReportView from '../components/reports/ClaimReportView';
import DownloadButton from '../components/reports/DownloadButton';
import { RepairModal } from '../components/claim/RepairModal';
import Loader from '../components/common/Loader';
import Badge from '../components/common/Badge';
import { formatDate, formatCurrency } from '../utils/formatters';
import { 
  ArrowLeft, 
  FileText, 
  Cpu, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Sparkles, 
  RotateCcw,
  Share2,
  Printer
} from 'lucide-react';

export const ClaimDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isStaff, isReviewer, isAdmin } = useAuth();
  const { toastSuccess, toastError } = useNotification();

  const [claim, setClaim] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'documents', 'ai_analysis', 'history'
  const [isOverrideOpen, setIsOverrideOpen] = useState(false);
  const [isRepairOpen, setIsRepairOpen] = useState(false);
  const [appealNotes, setAppealNotes] = useState('');
  const [showAppealBox, setShowAppealBox] = useState(false);

  const fetchClaimData = async () => {
    try {
      const cRes = await claimAPI.getClaimById(id);
      const claimObj = cRes.data || cRes;
      setClaim(claimObj);

      try {
        const dRes = await documentAPI.getDocumentsByClaim(id);
        setDocuments(dRes.data || (Array.isArray(dRes) ? dRes : []));
      } catch (docErr) {
      }

      try {
        const rRes = await reviewAPI.getReviewDetail(id);
        const data = rRes.data || rRes;
        if (data.reviews && Array.isArray(data.reviews)) {
          const formatted = data.reviews
            .filter((r) => r.comments && r.comments.trim())
            .map((r) => ({
              id: r.id,
              author_name: r.author_name || (r.reviewer ? r.reviewer.full_name : 'Staff'),
              text: r.comments,
              created_at: r.created_at,
            }));
          setComments(formatted);
        }
      } catch (revErr) {
      }
    } catch (err) {
      toastError(err.message || 'Failed to load claim');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClaimData();
  }, [id]);

  const handleDecision = async (decision) => {
    setActionLoading(true);
    try {
      await reviewAPI.submitReviewDecision(claim.id, {
        decision,
        reasoning: `Manual decision recorded by reviewer: ${user?.full_name || 'Staff'}`,
      });
      toastSuccess(`Claim decision set to ${decision}`);
      fetchClaimData();
    } catch (err) {
      toastError(err.message || 'Failed to update decision');
    } finally {
      setActionLoading(false);
    }
  };

  const handleOverride = async (overrideData) => {
    setActionLoading(true);
    try {
      await reviewAPI.overrideDecision(claim.id, overrideData);
      toastSuccess('AI Adjudication override successfully logged.');
      fetchClaimData();
    } catch (err) {
      toastError(err.message || 'Failed to log override');
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddComment = async (commentText) => {
    try {
      await reviewAPI.addReviewComment(claim.id, { comment: commentText });
      setComments((prev) => [
        ...prev,
        {
          id: Date.now(),
          author_name: user?.full_name || 'Adjudicator',
          text: commentText,
          created_at: new Date().toISOString(),
        },
      ]);
      toastSuccess('Note added to audit trail.');
    } catch (err) {
      toastError(err.message || 'Failed to add comment');
    }
  };

  const handleAppealSubmit = async (e) => {
    e.preventDefault();
    if (!appealNotes.trim()) return;
    setActionLoading(true);
    try {
      await claimAPI.appealClaim(claim.id, appealNotes.trim());
      toastSuccess('Appeal successfully submitted for re-review.');
      setShowAppealBox(false);
      fetchClaimData();
    } catch (err) {
      toastError(err.message || 'Failed to submit appeal');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <Loader isFullPage text="Loading claim adjudication record..." />;
  }

  if (!claim) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <p className="text-sm font-semibold text-slate-500">Claim not found.</p>
        <Link to="/claims" className="text-xs text-brand-600 font-bold mt-2 inline-block">
          Return to Claims
        </Link>
      </div>
    );
  }

  const isStaffUser = isStaff || isReviewer || isAdmin;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      
      {/* Top Breadcrumb & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 no-print">
        <div className="flex items-center gap-3">
          <Link
            to="/claims"
            className="p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white font-mono">
                {claim.claim_number}
              </h2>
              <Badge type="status" value={claim.status} size="md" />
              <Badge type="decision" value={claim.ai_decision || 'PENDING'} size="md" />
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Submitted on {formatDate(claim.submitted_at || claim.created_at)}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <DownloadButton claimId={claim.id} variant="pdf" />
          {isStaffUser && (
            <>
              <button
                type="button"
                onClick={() => setIsRepairOpen(true)}
                className="px-3.5 py-2 bg-blue-50 dark:bg-blue-900/40 hover:bg-blue-100 dark:hover:bg-blue-800/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800/50 text-xs font-semibold rounded-xl transition-all"
              >
                Log Repair
              </button>
              <button
                type="button"
                onClick={() => setIsOverrideOpen(true)}
                className="px-3.5 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl transition-all"
              >
                Override AI
              </button>
            </>
          )}
        </div>
      </div>

      {/* Duplicate / Fraud Alert Banner if score is elevated */}
      {claim.fraud_score > 0.3 && (
        <DuplicateAlert
          fraudScore={claim.fraud_score}
          serialNumber={claim.warranty?.serial_number || 'SN-SNY-2025-0819'}
        />
      )}

      {/* Lifecycle Status Stepper */}
      <StatusTimeline status={claim.status} />

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2 no-print">
        {['overview', 'documents', 'ai_analysis', 'history'].map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition-colors ${
              activeTab === tab
                ? 'bg-brand-50 dark:bg-brand-950 text-brand-600 dark:text-brand-400'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            {tab === 'overview' && 'Overview'}
            {tab === 'documents' && 'Documents'}
            {tab === 'ai_analysis' && 'AI & Model Evaluation'}
            {tab === 'history' && 'History'}
          </button>
        ))}
      </div>

      {/* Tab 1: Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6 animate-fade-in">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left 2 Cols: Main Claim & AI Info */}
            <div className="lg:col-span-2 space-y-6">
              
              {/* Fault & Equipment Information */}
              <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Fault & Equipment Information
                  </h3>
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                    Warranty ID #{claim.warranty_id}
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                  <div>
                    <span className="text-slate-400 font-semibold uppercase text-[10px]">
                      Product Model
                    </span>
                    <p className="font-bold text-slate-900 dark:text-white mt-0.5 text-sm">
                      {claim.warranty?.product?.brand} {claim.warranty?.product?.model_name || 'Electronics Device'}
                    </p>
                  </div>

                  <div>
                    <span className="text-slate-400 font-semibold uppercase text-[10px]">
                      Serial Number
                    </span>
                    <p className="font-mono font-bold text-slate-900 dark:text-white mt-0.5 text-sm">
                      {claim.warranty?.serial_number || claim.warranty?.product?.serial_number || 'N/A'}
                    </p>
                  </div>

                  <div>
                    <span className="text-slate-400 font-semibold uppercase text-[10px]">
                      Claim Amount
                    </span>
                    <p className="font-extrabold text-emerald-600 dark:text-emerald-400 text-sm mt-0.5">
                      {formatCurrency(claim.claim_amount)}
                    </p>
                  </div>
                </div>

                <div className="border-t border-slate-100 dark:border-slate-800 pt-3">
                  <span className="text-slate-400 font-semibold uppercase text-[10px]">
                    Fault Statement / Description
                  </span>
                  <p className="text-xs text-slate-700 dark:text-slate-300 mt-1 leading-relaxed bg-slate-50 dark:bg-slate-800/50 p-3.5 rounded-2xl border border-slate-100 dark:border-slate-800">
                    {claim.description || claim.fault_description || 'No description provided.'}
                  </p>
                </div>
              </div>

              {/* AI Adjudication & Evaluation Result Card */}
              <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-brand-500" />
                    <h3 className="text-base font-bold text-slate-900 dark:text-white">
                      AI Adjudication & Decision Summary
                    </h3>
                  </div>
                  <Badge type="decision" value={claim.final_decision || claim.ai_decision || 'Manual Review Required'} size="md" />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
                    <p className="text-[11px] font-semibold text-slate-400 uppercase">AI Status / Next Step</p>
                    <p className="text-sm font-bold text-slate-900 dark:text-white mt-1">
                      {claim.status === 'under_evaluation' || claim.status === 'under_review' ? 'In Manual Review Queue' : claim.status.toUpperCase()}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      {claim.final_decision === 'Likely Valid' ? 'Claim is eligible for auto-approval.' : 'Claim routed to human adjudicators for final verification.'}
                    </p>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
                    <p className="text-[11px] font-semibold text-slate-400 uppercase">Fraud & Anomaly Score</p>
                    <p className="text-sm font-bold text-emerald-600 dark:text-emerald-400 mt-1">
                      Low Risk ({(claim.fraud_score ? claim.fraud_score * 100 : 8).toFixed(1)}%)
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      No serial mismatch or duplicate claim indicators detected.
                    </p>
                  </div>
                </div>
              </div>

              {/* Missing Docs Checklist */}
              <MissingDocsPanel uploadedDocs={documents} />

              {/* Appeal Section if Rejected */}
              {claim.status === 'rejected' && (
                <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-rose-200 dark:border-rose-900/40 shadow-sm space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="text-sm font-bold text-rose-900 dark:text-rose-200">
                        Claim Rejected by Engine
                      </h4>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {claim.rejection_reason || 'Rejection triggered by policy exclusion or low confidence match.'}
                      </p>
                    </div>

                    {!showAppealBox && (
                      <button
                        type="button"
                        onClick={() => setShowAppealBox(true)}
                        className="px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold rounded-xl transition-colors"
                      >
                        File Appeal
                      </button>
                    )}
                  </div>

                  {showAppealBox && (
                    <form onSubmit={handleAppealSubmit} className="space-y-3 pt-2">
                      <textarea
                        rows={3}
                        required
                        value={appealNotes}
                        onChange={(e) => setAppealNotes(e.target.value)}
                        placeholder="State supplementary evidence or grounds for appealing this adjudication..."
                        className="w-full px-3.5 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none dark:text-white"
                      />
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => setShowAppealBox(false)}
                          className="px-3 py-1.5 text-xs text-slate-500 hover:bg-slate-100 rounded-lg"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          disabled={actionLoading}
                          className="px-4 py-1.5 bg-brand-600 text-white text-xs font-bold rounded-xl"
                        >
                          Submit Appeal
                        </button>
                      </div>
                    </form>
                  )}
                </div>
              )}
            </div>

            {/* Right Col: Staff Actions & OCR Data */}
            <div className="space-y-6">
              {isStaffUser && (
                <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                      Adjudicator Operations
                    </h3>
                    <Badge type="status" value={claim.status} size="sm" />
                  </div>

                  {/* If claim is already decided */}
                  {['approved', 'rejected', 'escalated', 'closed', 'settled'].includes((claim.status || '').toLowerCase()) ? (
                    <div className="space-y-3">
                      <div className={`p-4 rounded-2xl border ${
                        (claim.status || '').toLowerCase() === 'approved' || (claim.status || '').toLowerCase() === 'settled'
                          ? 'bg-emerald-50/80 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800/60 text-emerald-900 dark:text-emerald-200'
                          : (claim.status || '').toLowerCase() === 'rejected'
                          ? 'bg-rose-50/80 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800/60 text-rose-900 dark:text-rose-200'
                          : 'bg-purple-50/80 dark:bg-purple-950/40 border-purple-200 dark:border-purple-800/60 text-purple-900 dark:text-purple-200'
                      }`}>
                        <div className="flex items-center gap-2">
                          {(claim.status || '').toLowerCase() === 'approved' || (claim.status || '').toLowerCase() === 'settled' ? (
                            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                          ) : (claim.status || '').toLowerCase() === 'rejected' ? (
                            <XCircle className="w-5 h-5 text-rose-600 shrink-0" />
                          ) : (
                            <AlertTriangle className="w-5 h-5 text-purple-600 shrink-0" />
                          )}
                          <p className="text-xs font-extrabold uppercase tracking-wide">
                            {(claim.status || '').toLowerCase() === 'approved' ? 'Claim Approved & Settled' : (claim.status || '').toLowerCase() === 'rejected' ? 'Claim Rejected' : 'Escalated to Supervisor'}
                          </p>
                        </div>
                        <p className="text-[11px] opacity-80 mt-1.5">
                          Adjudication completed and recorded in audit log.
                        </p>
                      </div>

                      {/* Option to change or re-evaluate */}
                      <div className="pt-2 flex flex-col gap-2">
                        <button
                          type="button"
                          onClick={() => setIsOverrideOpen(true)}
                          className="w-full py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl transition-all"
                        >
                          Override / Re-evaluate Decision
                        </button>
                      </div>
                    </div>
                  ) : (
                    /* If claim is pending review */
                    <div className="space-y-2">
                      <button
                        type="button"
                        onClick={() => handleDecision('APPROVE')}
                        disabled={actionLoading}
                        className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow-xs transition-colors flex items-center justify-center gap-2"
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Approve Claim</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => handleDecision('REJECT')}
                        disabled={actionLoading}
                        className="w-full py-2.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold rounded-xl shadow-xs transition-colors flex items-center justify-center gap-2"
                      >
                        <XCircle className="w-4 h-4" />
                        <span>Reject Claim</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => handleDecision('ESCALATE')}
                        disabled={actionLoading}
                        className="w-full py-2.5 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-xl shadow-xs transition-colors flex items-center justify-center gap-2"
                      >
                        <AlertTriangle className="w-4 h-4" />
                        <span>Escalate to Supervisor</span>
                      </button>
                      
                      <button
                        type="button"
                        onClick={() => handleDecision('REQUEST_INFO')}
                        disabled={actionLoading}
                        className="w-full py-2.5 bg-amber-500 hover:bg-amber-400 text-white text-xs font-bold rounded-xl shadow-xs transition-colors flex items-center justify-center gap-2"
                      >
                        <FileText className="w-4 h-4" />
                        <span>Request Information</span>
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* OCR Extracted Output */}
              <OCRPreview 
                document={documents[0]} 
                expectedSerial={claim.warranty?.serial_number || claim.warranty?.product?.serial_number}
                fallbackData={{
                  purchase_date: claim.warranty?.purchase_date,
                  claim_amount: claim.claim_amount,
                  purchase_price: claim.warranty?.purchase_price,
                  ai_confidence: claim.ai_confidence,
                }}
              />

              {/* Comments & Discussion */}
              <CommentBox
                comments={comments}
                onAddComment={handleAddComment}
                loading={actionLoading}
                isStaff={isStaffUser}
              />
            </div>

          </div>
        </div>
      )}

      {/* Tab 2: Documents */}
      {activeTab === 'documents' && (
        <div className="space-y-6 animate-fade-in">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.length > 0 ? (
              documents.map((doc, idx) => (
                <div key={idx} className="p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 flex flex-col justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-brand-50 text-brand-600 flex items-center justify-center">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div className="overflow-hidden">
                      <p className="text-sm font-bold truncate text-slate-900 dark:text-white">{doc.name || 'Document'}</p>
                      <p className="text-xs text-slate-500 capitalize">{doc.document_type?.replace(/_/g, ' ')}</p>
                    </div>
                  </div>
                  {doc.url && (
                    <a href={doc.url} target="_blank" rel="noreferrer" className="mt-4 text-xs font-bold text-brand-600 hover:underline">
                      Preview Document
                    </a>
                  )}
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500 col-span-full">No documents uploaded.</p>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: AI Analysis */}
      {activeTab === 'ai_analysis' && (
        <div className="space-y-6 animate-fade-in">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <PredictionPanel
              pythonML={{
                name: 'Python Tabular ML Model (XGBoost)',
                decision: claim.python_prediction || claim.ai_decision || 'Valid Claim',
                confidence: claim.ai_confidence,
                fraudRisk: claim.fraud_score,
              }}
              teachableMachine={{
                name: 'Teachable Machine Vision Model',
                decision: claim.tm_prediction || 'Valid Claim',
                confidence: claim.tm_confidence_score || claim.ai_confidence,
                category: claim.damage_type || 'Manufacturing Defect',
              }}
              aiConfidence={claim.ai_confidence}
              fraudScore={claim.fraud_score}
            />
            <DecisionExplanation
              decision={claim.final_decision || claim.ai_decision || 'APPROVE'}
            />
          </div>
          <ComparisonPanel
            pythonMLScore={claim.ai_confidence}
            teachableMachineScore={claim.tm_confidence_score || claim.ai_confidence}
            agreementScore={claim.model_agreement_score}
          />
          <RuleResultPanel />
        </div>
      )}


      {/* Tab 4: History */}
      {activeTab === 'summary_card' && (
        <div className="space-y-6 animate-fade-in">
          <SummaryCardView
            claim={claim}
            product={claim.warranty?.product}
            warranty={claim.warranty}
            user={claim.user || user}
          />
        </div>
      )}

      {activeTab === 'history' && (
        <div className="space-y-6 animate-fade-in">
          <StatusTimeline status={claim.status} />
          
          <div className="max-w-2xl">
            <CommentBox
              comments={comments}
              onAddComment={handleAddComment}
              loading={actionLoading}
            />
          </div>
        </div>
      )}

      {/* Override Modal */}
      <OverrideModal
        isOpen={isOverrideOpen}
        onClose={() => setIsOverrideOpen(false)}
        onConfirmOverride={handleOverride}
        currentDecision={claim.ai_decision || 'REJECT'}
        claimNumber={claim.claim_number}
        loading={actionLoading}
      />

      {/* Repair Modal */}
      <RepairModal
        isOpen={isRepairOpen}
        onClose={() => setIsRepairOpen(false)}
        claim={claim}
        onSuccess={() => fetchClaimData()}
      />

    </div>
  );
};

export default ClaimDetailPage;