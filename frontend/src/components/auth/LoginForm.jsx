import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import { Mail, Lock, ArrowRight, Eye, EyeOff, KeyRound, ShieldCheck, UserCheck, Scale, Briefcase, X, Sparkles } from 'lucide-react';
import Loader from '../common/Loader';

const DEMO_ACCOUNTS = [
  {
    role: 'Customer',
    badgeColor: 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300 border-blue-200 dark:border-blue-800',
    icon: UserCheck,
    email: 'customer@assurex.com',
    password: 'customer123',
    description: 'Submit equipment warranties, file claims & track live status',
  },
  {
    role: 'Reviewer / Adjudicator',
    badgeColor: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
    icon: Scale,
    email: 'reviewer@assurex.com',
    password: 'reviewer123',
    description: 'Adjudicate queue, arbitrate AI disagreement & manual overrides',
  },
  {
    role: 'Administrator',
    badgeColor: 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300 border-purple-200 dark:border-purple-800',
    icon: ShieldCheck,
    email: 'admin@assurex.com',
    password: 'admin123',
    description: 'System metrics, ML model versions, policies & audit logs',
  },
  {
    role: 'Staff Support',
    badgeColor: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300 border-amber-200 dark:border-amber-800',
    icon: Briefcase,
    email: 'staff@assurex.com',
    password: 'staff123',
    description: 'Customer claim support, document verification & operations',
  },
];

export const LoginForm = ({ onSuccess = null }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  const { login } = useAuth();
  const { toastSuccess, toastError } = useNotification();
  const navigate = useNavigate();

  const handleAutoFill = (acc) => {
    setEmail(acc.email);
    setPassword(acc.password);
    setIsHelpOpen(false);
    toastSuccess(`Auto-filled credentials for ${acc.role}!`);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMsg('Please enter both email and password.');
      return;
    }

    setLoading(true);
    setErrorMsg('');

    try {
      const res = await login({ email: email.trim(), password });
      if (res.success) {
        toastSuccess(`Welcome back, ${res.user?.full_name || 'User'}!`);
        if (onSuccess) {
          onSuccess(res.user);
        } else {
          const role = (res.user?.role || '').toLowerCase();
          if (role === 'admin') navigate('/admin');
          else if (role === 'reviewer' || role === 'staff' || role === 'service_staff') navigate('/claims');
          else navigate('/dashboard');
        }
      } else {
        setErrorMsg(res.error || 'Invalid credentials');
        toastError(res.error || 'Login failed');
      }
    } catch (err) {
      setErrorMsg(err.message || 'An error occurred during login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full relative">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
            Welcome back
          </h2>
          <p className="text-slate-500 dark:text-slate-400 mt-1 text-sm sm:text-base">
            Please enter your details to sign in.
          </p>
        </div>

        {/* Login Help & Pass Button */}
        <button
          type="button"
          onClick={() => setIsHelpOpen(true)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-brand-50 hover:bg-brand-100 dark:bg-brand-950/80 dark:hover:bg-brand-900/80 border border-brand-200 dark:border-brand-800 text-xs font-bold text-brand-700 dark:text-brand-300 shadow-xs transition-all hover:scale-102"
        >
          <KeyRound className="w-3.5 h-3.5 text-brand-600" />
          <span>Login Help / Pass</span>
        </button>
      </div>

      {errorMsg && (
        <div className="mb-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/60 text-sm text-rose-700 dark:text-rose-300 flex items-start gap-2">
          {errorMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            Email Address
          </label>
          <div className="relative">
            <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              className="w-full pl-10 pr-4 py-2.5 sm:py-3 text-sm sm:text-base bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white placeholder:text-slate-400"
            />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Password
            </label>
            <a href="#" className="text-xs sm:text-sm font-medium text-brand-600 hover:text-brand-500 dark:text-brand-400 transition-colors">
              Forgot password?
            </a>
          </div>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type={showPassword ? "text" : "password"}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full pl-10 pr-10 py-2.5 sm:py-3 text-sm sm:text-base bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white placeholder:text-slate-400"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-600 dark:border-slate-700 dark:bg-slate-900"
            />
            <label htmlFor="remember-me" className="ml-2.5 block text-xs sm:text-sm text-slate-600 dark:text-slate-400">
              Remember me
            </label>
          </div>

          <button
            type="button"
            onClick={() => setIsHelpOpen(true)}
            className="text-xs text-brand-600 dark:text-brand-400 font-semibold hover:underline"
          >
            Auto-fill credentials?
          </button>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 sm:py-3 px-4 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-medium rounded-xl text-sm sm:text-base flex items-center justify-center gap-2 transition-all shadow-sm"
        >
          {loading ? (
            <Loader size="sm" text="" />
          ) : (
            <>
              <span>Sign In</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Don't have an account?{' '}
          <Link
            to="/register"
            className="font-medium text-brand-600 hover:text-brand-500 dark:text-brand-400 transition-colors"
          >
            Create an Account
          </Link>
        </p>
      </div>

      {/* Login Help & Passwords Modal */}
      {isHelpOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-fade-in">
          <div className="bg-white dark:bg-slate-900 w-full max-w-lg rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden animate-scale-in">
            {/* Modal Header */}
            <div className="p-5 sm:p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-brand-100 dark:bg-brand-950 text-brand-600 dark:text-brand-400">
                  <KeyRound className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                    Login Help & Demo Passwords
                  </h3>
                  <p className="text-xs text-slate-500">
                    Click any role below to 1-click auto-fill credentials
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setIsHelpOpen(false)}
                className="p-2 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body - Role Accounts List */}
            <div className="p-5 sm:p-6 space-y-3 max-h-[60vh] overflow-y-auto">
              {DEMO_ACCOUNTS.map((acc, idx) => {
                const Icon = acc.icon;
                return (
                  <div
                    key={idx}
                    onClick={() => handleAutoFill(acc)}
                    className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 hover:border-brand-500 dark:hover:border-brand-500 bg-slate-50/60 dark:bg-slate-800/40 hover:bg-brand-50/40 dark:hover:bg-brand-950/40 transition-all cursor-pointer group flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs"
                  >
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-xl bg-white dark:bg-slate-800 shadow-xs text-slate-700 dark:text-slate-300 mt-0.5">
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-sm text-slate-900 dark:text-white">
                            {acc.role}
                          </span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${acc.badgeColor}`}>
                            Demo
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {acc.description}
                        </p>
                        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs font-mono">
                          <span className="text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 px-2 py-0.5 rounded-md border border-slate-200 dark:border-slate-700">
                            ✉️ {acc.email}
                          </span>
                          <span className="text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 px-2 py-0.5 rounded-md border border-slate-200 dark:border-slate-700">
                            🔑 {acc.password}
                          </span>
                        </div>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAutoFill(acc);
                      }}
                      className="px-3.5 py-1.5 rounded-xl bg-white dark:bg-slate-900 group-hover:bg-brand-600 text-slate-700 dark:text-slate-300 group-hover:text-white border border-slate-200 dark:border-slate-700 group-hover:border-brand-600 text-xs font-bold transition-colors shrink-0 shadow-xs flex items-center justify-center gap-1.5"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Auto Fill</span>
                    </button>
                  </div>
                );
              })}
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-slate-50 dark:bg-slate-800/60 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
              <span>All accounts verified and active</span>
              <button
                type="button"
                onClick={() => setIsHelpOpen(false)}
                className="px-4 py-1.5 bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 font-semibold rounded-xl hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LoginForm;

