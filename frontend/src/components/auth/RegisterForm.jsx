import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import { User, Mail, Lock, Phone, ArrowRight, Eye, EyeOff, CheckCircle } from 'lucide-react';
import Loader from '../common/Loader';
import { isValidEmail, isValidPassword, getPasswordStrengthDetails } from '../../utils/validators';

export const RegisterForm = ({ onSuccess = null }) => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    role: 'customer',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const { register } = useAuth();
  const { toastSuccess, toastError } = useNotification();
  const navigate = useNavigate();

  const strengthDetails = getPasswordStrengthDetails(formData.password);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const { full_name, email, phone, password, confirmPassword, role } = formData;

    if (!full_name || !email || !password) {
      setErrorMsg('Please complete all required fields.');
      return;
    }
    if (!isValidEmail(email)) {
      setErrorMsg('Please enter a valid email address.');
      return;
    }
    if (!isValidPassword(password)) {
      setErrorMsg('Password must be at least 8 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setErrorMsg('Passwords do not match.');
      return;
    }
    if (!termsAccepted) {
      setErrorMsg('Please accept the Terms of Service.');
      return;
    }

    setLoading(true);
    setErrorMsg('');

    try {
      const res = await register({
        full_name: full_name.trim(),
        email: email.trim(),
        phone: phone ? phone.trim() : null,
        password,
        role,
      });

      if (res.success) {
        toastSuccess('Registration successful! Welcome to AssureX.');
        if (onSuccess) {
          onSuccess(res.user);
        } else {
          navigate('/dashboard');
        }
      } else {
        setErrorMsg(res.error || 'Registration failed');
        toastError(res.error || 'Registration failed');
      }
    } catch (err) {
      setErrorMsg(err.message || 'Error occurred');
    } finally {
      setLoading(false);
    }
  };

  const reqs = {
    length: formData.password.length >= 8,
    numberOrSpecial: /[0-9!@#$%^&*]/.test(formData.password)
  };

  return (
    <div className="w-full">
      <div className="mb-4">
        <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
          Create an account
        </h2>
        <p className="text-slate-500 dark:text-slate-400 mt-1 text-xs sm:text-sm">
          Join AssureX to start processing claims.
        </p>
      </div>

      {errorMsg && (
        <div className="mb-3 p-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/60 text-xs sm:text-sm text-rose-700 dark:text-rose-300">
          {errorMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Full Name *
          </label>
          <div className="relative">
            <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              name="full_name"
              required
              value={formData.full_name}
              onChange={handleChange}
              placeholder="Jane Doe"
              className="w-full pl-10 pr-4 py-2 text-xs sm:text-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white placeholder:text-slate-400"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Email Address *
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                placeholder="jane@example.com"
                className="w-full pl-10 pr-4 py-2 text-xs sm:text-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white placeholder:text-slate-400"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Phone (Optional)
            </label>
            <div className="relative">
              <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="+1 (555) 000-0000"
                className="w-full pl-10 pr-4 py-2 text-xs sm:text-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white placeholder:text-slate-400"
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Password *
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                required
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full pl-10 pr-9 py-2 text-xs sm:text-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white placeholder:text-slate-400"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
          <div>
            <label className="block text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Confirm *
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type={showConfirmPassword ? "text" : "password"}
                name="confirmPassword"
                required
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full pl-10 pr-9 py-2 text-xs sm:text-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all dark:text-white placeholder:text-slate-400"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
              >
                {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>

        {/* Password Strength Indicator & Live Criteria Checklist */}
        {formData.password.length > 0 && (
          <div className="space-y-2 p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700/60">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                Security Strength:
              </span>
              <span className={`text-xs font-bold ${
                strengthDetails.label === 'Weak' ? 'text-rose-500' :
                strengthDetails.label === 'Fair' ? 'text-amber-500' :
                strengthDetails.label === 'Good' ? 'text-blue-500' :
                'text-emerald-500'
              }`}>
                {strengthDetails.label || 'Evaluating'} ({strengthDetails.score}/5)
              </span>
            </div>
            
            <div className="flex gap-1 h-1.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              {[1, 2, 3, 4, 5].map((level) => (
                <div
                  key={level}
                  className={`h-full w-1/5 transition-colors duration-300 ${
                    strengthDetails.score >= level ? strengthDetails.color : 'bg-transparent'
                  }`}
                />
              ))}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 pt-1">
              {strengthDetails.checks?.map((check, idx) => (
                <div key={idx} className="flex items-center gap-1.5 text-[11px]">
                  <CheckCircle className={`w-3.5 h-3.5 shrink-0 transition-colors ${
                    check.valid ? 'text-emerald-500' : 'text-slate-300 dark:text-slate-600'
                  }`} />
                  <span className={check.valid ? 'text-slate-700 dark:text-slate-200 font-medium' : 'text-slate-400'}>
                    {check.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex items-start gap-2 pt-1">
          <input
            id="terms"
            name="terms"
            type="checkbox"
            checked={termsAccepted}
            onChange={(e) => setTermsAccepted(e.target.checked)}
            className="mt-0.5 h-3.5 w-3.5 rounded border-slate-300 text-brand-600 focus:ring-brand-600 dark:border-slate-700 dark:bg-slate-900"
          />
          <label htmlFor="terms" className="block text-xs text-slate-600 dark:text-slate-400 leading-tight">
            I agree to the <a href="#" className="font-medium text-brand-600 hover:text-brand-500 dark:text-brand-400 transition-colors">Terms of Service</a> and <a href="#" className="font-medium text-brand-600 hover:text-brand-500 dark:text-brand-400 transition-colors">Privacy Policy</a>
          </label>
        </div>

        <button
          type="submit"
          disabled={loading || !termsAccepted}
          className="w-full py-2.5 px-4 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-medium rounded-xl text-sm flex items-center justify-center gap-2 transition-all shadow-sm"
        >
          {loading ? (
            <Loader size="sm" text="" />
          ) : (
            <>
              <span>Create Account</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>

      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-center">
        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
          Already have an account?{' '}
          <Link
            to="/login"
            className="font-bold text-brand-600 hover:text-brand-500 dark:text-brand-400 underline underline-offset-4 ml-1 transition-colors"
          >
            Sign In here
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterForm;

