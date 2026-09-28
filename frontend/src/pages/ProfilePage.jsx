import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import authAPI from '../api/authAPI';
import {
  User, Mail, Phone, Lock, Shield, Save, Edit3, Check,
  X, Calendar, Award, FileText, ShieldCheck, Key, LogOut,
  ChevronDown, ChevronUp, Eye, EyeOff,
} from 'lucide-react';
import Loader from '../components/common/Loader';

/* ── role badge ────────────────────────────────────── */
const ROLE_COLORS = {
  admin:    'bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300',
  reviewer: 'bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300',
  staff:    'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300',
  customer: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300',
};

const RoleBadge = ({ role }) => {
  const r = (role || 'customer').toLowerCase();
  const icons = { admin: '👑', reviewer: '🛡️', staff: '⚙️', customer: '👤' };
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold capitalize ${ROLE_COLORS[r] || ROLE_COLORS.customer}`}>
      <span>{icons[r] || '👤'}</span>
      {r.charAt(0).toUpperCase() + r.slice(1)}
    </span>
  );
};

/* ── input field ───────────────────────────────────── */
const Field = ({ label, icon: Icon, type = 'text', value, onChange, disabled, placeholder, rightElement }) => (
  <div>
    <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">{label}</label>
    <div className="relative">
      {Icon && <Icon className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />}
      <input
        type={type}
        value={value}
        onChange={onChange}
        disabled={disabled}
        placeholder={placeholder}
        className={`w-full ${Icon ? 'pl-10' : 'pl-4'} ${rightElement ? 'pr-10' : 'pr-4'} py-2.5 text-sm rounded-xl border transition-all
          ${disabled
            ? 'bg-slate-100 dark:bg-slate-800/30 border-slate-200 dark:border-slate-800 text-slate-400 cursor-not-allowed'
            : 'bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500'
          }`}
      />
      {rightElement && <div className="absolute right-3 top-1/2 -translate-y-1/2">{rightElement}</div>}
    </div>
  </div>
);

/* ── main component ────────────────────────────────── */
export const ProfilePage = () => {
  const { user, updateUser } = useAuth();
  const { toastSuccess, toastError } = useNotification();

  const [editing, setEditing] = useState(false);
  const [showPwSection, setShowPwSection] = useState(false);
  const [showCurrentPw, setShowCurrentPw] = useState(false);
  const [showNewPw, setShowNewPw]         = useState(false);
  const [showConfirmPw, setShowConfirmPw] = useState(false);

  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email:     user?.email     || '',
    phone:     user?.phone     || '',
    profile_image_url: user?.profile_image_url || '',
  });

  const [passwordData, setPasswordData] = useState({
    current_password:  '',
    new_password:      '',
    confirm_password:  '',
  });

  const [savingProfile,  setSavingProfile]  = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  /* ── initials avatar ─── */
  const initials = (user?.full_name || 'U')
    .split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase();

  const joinDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    : 'Unknown';

  /* ── handlers ─── */
  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    try {
      await authAPI.updateProfile(formData);
      updateUser(formData);
      toastSuccess('Profile updated successfully.');
      setEditing(false);
    } catch (err) {
      toastError(err.message || 'Failed to update profile');
    } finally {
      setSavingProfile(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      toastError('New passwords do not match');
      return;
    }
    setSavingPassword(true);
    try {
      await authAPI.changePassword({
        current_password: passwordData.current_password,
        new_password:     passwordData.new_password,
      });
      toastSuccess('Password updated successfully.');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      setShowPwSection(false);
    } catch (err) {
      toastError(err.message || 'Failed to update password');
    } finally {
      setSavingPassword(false);
    }
  };

  const cancelEdit = () => {
    setFormData({ full_name: user?.full_name || '', email: user?.email || '', phone: user?.phone || '' });
    setEditing(false);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">

      {/* ── Page Header ─────────────────────────────────────── */}
      <div>
        <h2 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white flex items-center gap-2.5">
          <User className="w-6 h-6 text-brand-600" />
          My Profile & Account Security
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Manage your identity, contact details, and access credentials
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* ── Left: Avatar Card ──────────────────────────────── */}
        <div className="md:col-span-1">
          <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm text-center space-y-4">
            {/* Avatar */}
            <div className="relative inline-flex">
              {user?.profile_image_url ? (
                <img src={user.profile_image_url} alt="Avatar" className="w-24 h-24 rounded-2xl object-cover shadow-xl shadow-brand-500/30" />
              ) : (
                <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center shadow-xl shadow-brand-500/30">
                  <span className="text-3xl font-extrabold text-white">{initials}</span>
                </div>
              )}
              <div className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-emerald-500 border-2 border-white dark:border-slate-900 flex items-center justify-center">
                <Check className="w-3 h-3 text-white" />
              </div>
            </div>

            <div>
              <p className="text-lg font-bold text-slate-900 dark:text-white">{user?.full_name || '—'}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{user?.email || '—'}</p>
            </div>

            <RoleBadge role={user?.role} />

            <div className="pt-3 border-t border-slate-100 dark:border-slate-800 space-y-2 text-xs text-left">
              <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                <Calendar className="w-3.5 h-3.5 shrink-0" />
                <span>Joined {joinDate}</span>
              </div>
              <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                <ShieldCheck className="w-3.5 h-3.5 shrink-0 text-emerald-500" />
                <span className="text-emerald-600 dark:text-emerald-400 font-medium">Account Verified</span>
              </div>
              <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                <Shield className="w-3.5 h-3.5 shrink-0 text-brand-500" />
                <span>256-bit Encrypted</span>
              </div>
            </div>
          </div>
        </div>

        {/* ── Right: Info + Security ─────────────────────────── */}
        <div className="md:col-span-2 space-y-5">

          {/* Profile Info Card */}
          <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-brand-600" />
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">Personal Information</h3>
              </div>
              {!editing ? (
                <button
                  onClick={() => setEditing(true)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/50 hover:bg-brand-100 dark:hover:bg-brand-900/50 rounded-lg transition-colors"
                >
                  <Edit3 className="w-3.5 h-3.5" /> Edit
                </button>
              ) : (
                <div className="flex gap-2">
                  <button
                    onClick={cancelEdit}
                    className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg transition-colors"
                  >
                    <X className="w-3.5 h-3.5" /> Cancel
                  </button>
                </div>
              )}
            </div>

            <form onSubmit={handleProfileSubmit} className="space-y-4">
              <Field
                label="Full Name"
                icon={User}
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                disabled={!editing}
                placeholder="Your full name"
              />
              <Field
                label="Email Address"
                icon={Mail}
                type="email"
                value={formData.email}
                disabled
                placeholder="email@example.com"
              />
              <Field
                label="Phone Number"
                icon={Phone}
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                disabled={!editing}
                placeholder="+1 (555) 000-0000"
              />
              <Field
                label="Avatar URL (Optional)"
                icon={User}
                type="text"
                value={formData.profile_image_url}
                onChange={(e) => setFormData({ ...formData, profile_image_url: e.target.value })}
                disabled={!editing}
                placeholder="https://example.com/avatar.png"
              />

              {editing && (
                <div className="flex justify-end pt-1">
                  <button
                    type="submit"
                    disabled={savingProfile}
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white text-sm font-bold rounded-xl shadow-lg shadow-brand-500/25 transition-all"
                  >
                    {savingProfile ? <Loader size="sm" text="" /> : <Save className="w-4 h-4" />}
                    Save Changes
                  </button>
                </div>
              )}
            </form>
          </div>

          {/* Change Password Card */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            <button
              onClick={() => setShowPwSection(!showPwSection)}
              className="w-full flex items-center justify-between px-6 py-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Key className="w-4 h-4 text-brand-600" />
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">Change Password</h3>
              </div>
              {showPwSection ? (
                <ChevronUp className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              )}
            </button>

            {showPwSection && (
              <form onSubmit={handlePasswordSubmit} className="px-6 pb-6 space-y-4 border-t border-slate-100 dark:border-slate-800 pt-4">
                <Field
                  label="Current Password"
                  icon={Lock}
                  type={showCurrentPw ? 'text' : 'password'}
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                  placeholder="••••••••"
                  rightElement={
                    <button type="button" onClick={() => setShowCurrentPw(!showCurrentPw)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                      {showCurrentPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  }
                />
                <div className="grid grid-cols-2 gap-3">
                  <Field
                    label="New Password"
                    icon={Lock}
                    type={showNewPw ? 'text' : 'password'}
                    value={passwordData.new_password}
                    onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                    placeholder="••••••••"
                    rightElement={
                      <button type="button" onClick={() => setShowNewPw(!showNewPw)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                        {showNewPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    }
                  />
                  <Field
                    label="Confirm New Password"
                    icon={Lock}
                    type={showConfirmPw ? 'text' : 'password'}
                    value={passwordData.confirm_password}
                    onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                    placeholder="••••••••"
                    rightElement={
                      <button type="button" onClick={() => setShowConfirmPw(!showConfirmPw)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                        {showConfirmPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    }
                  />
                </div>
                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={savingPassword}
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-800 hover:bg-slate-700 dark:bg-slate-700 dark:hover:bg-slate-600 disabled:opacity-50 text-white text-sm font-bold rounded-xl transition-all"
                  >
                    {savingPassword ? <Loader size="sm" text="" /> : <Lock className="w-4 h-4" />}
                    Update Password
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* Security Info Card */}
          <div className="p-5 bg-brand-50 dark:bg-brand-950/30 rounded-2xl border border-brand-100 dark:border-brand-900/50">
            <div className="flex items-center gap-2 mb-3">
              <Shield className="w-4 h-4 text-brand-600 dark:text-brand-400" />
              <h4 className="text-xs font-bold text-brand-800 dark:text-brand-300 uppercase tracking-wider">Security Status</h4>
            </div>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="flex items-center gap-2 text-brand-700 dark:text-brand-300">
                <Check className="w-3.5 h-3.5 text-emerald-500" />
                <span>JWT Authentication Active</span>
              </div>
              <div className="flex items-center gap-2 text-brand-700 dark:text-brand-300">
                <Check className="w-3.5 h-3.5 text-emerald-500" />
                <span>bcrypt Password Hashing</span>
              </div>
              <div className="flex items-center gap-2 text-brand-700 dark:text-brand-300">
                <Check className="w-3.5 h-3.5 text-emerald-500" />
                <span>HTTPS / TLS Encrypted</span>
              </div>
              <div className="flex items-center gap-2 text-brand-700 dark:text-brand-300">
                <Check className="w-3.5 h-3.5 text-emerald-500" />
                <span>Role-Based Access Control</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
