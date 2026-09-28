import React, { useState } from 'react';
import { MessageSquare, Send, User, Clock } from 'lucide-react';
import { formatDateTime } from '../../utils/formatters';
import Loader from '../common/Loader';

export const CommentBox = ({
  comments = [],
  onAddComment,
  loading = false,
  isStaff = false,
  title = null,
  placeholder = null,
}) => {
  const [newComment, setNewComment] = useState('');

  const defaultTitle = isStaff 
    ? `Reviewer Audit Trail & Internal Comments (${comments.length})`
    : `Claim Notes & Discussion (${comments.length})`;

  const defaultPlaceholder = isStaff
    ? 'Add an internal review comment or adjudication note...'
    : 'Add a question or note regarding this claim...';

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    onAddComment(newComment.trim());
    setNewComment('');
  };

  return (
    <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
      <div className="flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
        <MessageSquare className="w-4 h-4 text-brand-500" />
        <h4 className="text-sm font-bold text-slate-900 dark:text-white">
          {title || defaultTitle}
        </h4>
      </div>

      {/* Existing Comments List */}
      <div className="space-y-3 max-h-56 overflow-y-auto pr-1">
        {comments.length > 0 ? (
          comments.map((c, idx) => (
            <div
              key={c.id || idx}
              className="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 space-y-1"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5 text-brand-500" />
                  {c.author_name || c.author || 'User'}
                </span>
                <span className="text-[10px] text-slate-400 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {formatDateTime(c.created_at || c.timestamp)}
                </span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-300 whitespace-pre-wrap">
                {c.text || c.comment || c.message}
              </p>
            </div>
          ))
        ) : (
          <p className="text-xs text-slate-400 italic py-1">
            No notes or messages attached to this claim yet.
          </p>
        )}
      </div>

      {/* Clean Full-Width Input Box */}
      <form onSubmit={handleSubmit} className="space-y-2 pt-1">
        <textarea
          rows={3}
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder={placeholder || defaultPlaceholder}
          className="w-full px-3.5 py-2.5 text-xs bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 dark:text-white transition-all resize-none leading-relaxed"
        />
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || !newComment.trim()}
            className="px-4 py-2 bg-brand-600 hover:bg-brand-500 disabled:opacity-40 text-white font-semibold rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-sm transition-all"
          >
            {loading ? <Loader size="sm" text="" /> : <Send className="w-3.5 h-3.5" />}
            <span>Post Note</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default CommentBox;