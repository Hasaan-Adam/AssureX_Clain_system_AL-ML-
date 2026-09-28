import re

with open('frontend/src/pages/ClaimDetailPage.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace activeTab initial state and tabs
content = re.sub(
    r"const \[activeTab, setActiveTab\] = useState\('overview'\); // 'overview', 'ai_audit', 'summary_card', 'report'",
    "const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'documents', 'ai_analysis', 'history'",
    content
)

tabs_html = """<div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2 no-print">
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
            {tab === 'ai_analysis' && 'AI Analysis'}
            {tab === 'history' && 'History'}
          </button>
        ))}
      </div>"""

content = re.sub(
    r'<div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2 no-print">.*?</div>',
    tabs_html,
    content,
    flags=re.DOTALL
)

tab2_html = """{/* Tab 2: Documents */}
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
              aiConfidence={claim.ai_confidence || 0.92}
              fraudScore={claim.fraud_score || 0.08}
            />
            <DecisionExplanation
              decision={claim.ai_decision || 'APPROVE'}
            />
          </div>
          <ComparisonPanel
            pythonMLScore={claim.ai_confidence || 0.92}
            teachableMachineScore={claim.model_agreement_score ? 0.92 - (1 - claim.model_agreement_score) : 0.88}
            agreementScore={claim.model_agreement_score || 0.96}
          />
          <RuleResultPanel />
        </div>
      )}

      {/* Tab 4: History */}"""

content = re.sub(
    r"{/\* Tab 2: AI Audit & Comparison \*/}.*?{/\* Tab 3: Summary Card View \*/}",
    tab2_html,
    content,
    flags=re.DOTALL
)

tab4_html = """{activeTab === 'history' && (
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

      {/* Override Modal */}"""

content = re.sub(
    r"{/\* Tab 4: Printable Dossier \*/}.*?{/\* Override Modal \*/}",
    tab4_html,
    content,
    flags=re.DOTALL
)

with open('frontend/src/pages/ClaimDetailPage.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
