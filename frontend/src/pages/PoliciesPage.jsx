import React, { useState, useEffect } from 'react';
import adminAPI from '../api/adminAPI';
import { useNotification } from '../context/NotificationContext';
import { Settings, Save, AlertTriangle } from 'lucide-react';
import Loader from '../components/common/Loader';

export const PoliciesPage = () => {
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activePolicy, setActivePolicy] = useState(null);
  const [editorContent, setEditorContent] = useState('');
  const { toastSuccess, toastError } = useNotification();

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      const res = await adminAPI.getPolicies();
      setPolicies(res.data?.policies || []);
      if (res.data?.policies?.length > 0) {
        selectPolicy(res.data.policies[0]);
      }
    } catch (err) {
      toastError("Failed to fetch policies");
    } finally {
      setLoading(false);
    }
  };

  const selectPolicy = (policy) => {
    setActivePolicy(policy);
    setEditorContent(JSON.stringify(policy.data, null, 2));
  };

  const handleSave = async () => {
    if (!activePolicy) return;
    
    let parsed;
    try {
      parsed = JSON.parse(editorContent);
    } catch (err) {
      toastError("Invalid JSON format. Please correct it before saving.");
      return;
    }

    setSaving(true);
    try {
      await adminAPI.updatePolicy(activePolicy.filename, parsed);
      toastSuccess(`Policy ${activePolicy.filename} updated successfully!`);
      fetchPolicies();
    } catch (err) {
      toastError("Failed to update policy");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
          <Settings className="w-6 h-6 text-brand-600" />
          Warranty Policy Configuration
        </h2>
        <p className="text-slate-500 dark:text-slate-400 mt-1 text-sm">
          Dynamic rule-engine configuration. Edit category-specific warranty rules.
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center p-12"><Loader /></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="md:col-span-1 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-4">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-3 text-sm">Available Policies</h3>
            <div className="space-y-2">
              {policies.map(p => (
                <button
                  key={p.filename}
                  onClick={() => selectPolicy(p)}
                  className={`w-full text-left px-3 py-2 rounded-xl text-sm transition-colors ${activePolicy?.filename === p.filename ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/50 dark:text-brand-300 font-medium' : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800'}`}
                >
                  {p.filename}
                </button>
              ))}
            </div>
          </div>
          
          <div className="md:col-span-3 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col h-[600px]">
            <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-800/50">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                {activePolicy?.filename || 'No file selected'}
              </span>
              <button
                onClick={handleSave}
                disabled={saving || !activePolicy}
                className="inline-flex items-center gap-2 px-4 py-1.5 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white text-xs font-bold rounded-lg transition-colors"
              >
                {saving ? <Loader /> : <Save className="w-3.5 h-3.5" />}
                Save Changes
              </button>
            </div>
            
            <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border-b border-amber-100 dark:border-amber-900/50 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
              <p className="text-xs text-amber-700 dark:text-amber-400 leading-relaxed">
                <strong>Warning:</strong> These rules directly control the AI Adjudication engine. 
                Invalid JSON or missing fields may cause the evaluation pipeline to fail. 
                Changes take effect immediately on new claims.
              </p>
            </div>

            <textarea
              value={editorContent}
              onChange={(e) => setEditorContent(e.target.value)}
              className="flex-1 p-4 w-full bg-slate-950 text-emerald-400 font-mono text-sm resize-none focus:outline-none"
              spellCheck="false"
            />
          </div>
        </div>
      )}
    </div>
  );
};
