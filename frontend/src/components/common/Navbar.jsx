import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import { Bell, Menu, X, ChevronDown, LogOut, Settings, User as UserIcon } from 'lucide-react';
import { timeAgo } from '../../utils/formatters';
import Badge from './Badge';

export const Navbar = ({ onToggleSidebar, isSidebarOpen }) => {
  const { user, logout } = useAuth();
  const { notifications, unreadCount, handleMarkRead, handleMarkAllRead } = useNotification();
  const navigate = useNavigate();

  const [profileOpen, setProfileOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const profileRef = useRef(null);
  const notifRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setProfileOpen(false);
      }
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setNotifOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getDotColor = (type) => {
    switch(type) {
      case 'warranty_expiry': return 'bg-amber-500';
      case 'claim_approved': return 'bg-emerald-500';
      case 'claim_rejected': return 'bg-rose-500';
      default: return 'bg-blue-500';
    }
  };

  return (
    <header className="sticky top-0 z-20 w-full bg-white/80 backdrop-blur-md border-b border-slate-200/80 transition-colors">
      <div className="px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Left: Hamburger and Logo for mobile */}
        <div className="flex items-center gap-3">
          {onToggleSidebar && (
            <button
              type="button"
              onClick={onToggleSidebar}
              className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors md:hidden"
            >
              {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          )}
          <div className="flex items-center gap-2 md:hidden">
            <img src="/logo.png" alt="AssureX Logo" className="w-7 h-7 rounded-lg object-contain shadow-sm" />
            <span className="text-base font-extrabold tracking-tight bg-gradient-to-r from-brand-600 to-blue-600 bg-clip-text text-transparent">AssureX</span>
          </div>
          <div className="hidden md:block">
            <h2 className="text-lg font-bold text-slate-800 tracking-tight">Command Center</h2>
          </div>
        </div>

        {/* Right Action Icons & User Dropdown */}
        <div className="flex items-center gap-4">
          
          {/* Notifications Center */}
          <div className="relative" ref={notifRef}>
            <button
              type="button"
              onClick={() => setNotifOpen(!notifOpen)}
              className="relative p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
              title="Notifications"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 w-4 h-4 flex items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white ring-2 ring-white">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>

            {/* Notification Drawer Popover */}
            {notifOpen && (
              <div className="absolute right-0 mt-2 w-80 rounded-2xl bg-white border border-slate-200 shadow-2xl p-4 animate-slide-up z-50">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-2">
                  <h4 className="text-sm font-semibold text-slate-900">Notifications</h4>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">{unreadCount} unread</span>
                    {unreadCount > 0 && (
                      <button 
                        onClick={handleMarkAllRead}
                        className="text-xs text-brand-600 hover:text-brand-700 font-medium"
                      >
                        Mark all read
                      </button>
                    )}
                  </div>
                </div>
                <div className="max-h-64 overflow-y-auto space-y-2">
                  {notifications && notifications.length > 0 ? (
                    notifications.map((n) => (
                      <div
                        key={n.id}
                        onClick={() => !n.is_read && handleMarkRead(n.id)}
                        className={`p-2.5 rounded-xl text-xs border cursor-pointer transition-colors ${
                          n.is_read 
                            ? 'bg-slate-50 border-transparent text-slate-600' 
                            : 'bg-white border-slate-200 shadow-sm text-slate-800'
                        }`}
                      >
                        <div className="flex items-start gap-2">
                          <div className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${getDotColor(n.type)}`} />
                          <div className="flex-1 min-w-0">
                            <div className="flex justify-between items-start gap-1">
                              <p className="font-semibold truncate">{n.title}</p>
                              <span className="text-[10px] text-slate-400 whitespace-nowrap">{timeAgo(n.created_at)}</span>
                            </div>
                            <p className="mt-0.5 text-slate-500 line-clamp-2 leading-tight">
                              {n.message}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-6 text-slate-400 flex flex-col items-center">
                      <Bell className="w-8 h-8 mb-2 opacity-20" />
                      <span className="text-xs">No new notifications</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* User Profile Dropdown */}
          {user ? (
            <div className="relative border-l border-slate-200 pl-4 ml-1" ref={profileRef}>
              <button
                type="button"
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex items-center gap-2.5 py-1 rounded-xl hover:opacity-80 transition-opacity"
              >
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-bold text-slate-800 leading-tight">
                    {user.full_name || user.email.split('@')[0]}
                  </p>
                  <p className="text-[10px] text-slate-500 font-medium capitalize">
                    {user.role || 'Customer'}
                  </p>
                </div>
                <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-brand-600 to-brand-400 text-white font-bold flex items-center justify-center text-sm shadow-md ring-2 ring-white overflow-hidden">
                  {user.profile_image_url ? (
                    <img src={user.profile_image_url} alt="Profile" className="w-full h-full object-cover" />
                  ) : (
                    user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'
                  )}
                </div>
              </button>

              {/* Profile Menu Popover */}
              {profileOpen && (
                <div className="absolute right-0 mt-3 w-56 rounded-2xl bg-white border border-slate-200 shadow-2xl p-2 animate-slide-up z-50">
                  <div className="px-3 py-2 border-b border-slate-100 mb-1">
                    <p className="text-xs font-semibold text-slate-900 truncate">
                      {user.full_name}
                    </p>
                    <p className="text-[11px] text-slate-400 truncate">{user.email}</p>
                  </div>

                  <Link
                    to="/profile"
                    onClick={() => setProfileOpen(false)}
                    className="flex items-center gap-2 px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 rounded-xl transition-colors mt-1"
                  >
                    <UserIcon className="w-4 h-4 text-slate-400" />
                    User Profile Management
                  </Link>

                  <div className="my-1 border-t border-slate-100" />

                  <button
                    type="button"
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2 px-3 py-2 text-xs font-medium text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
                  >
                    <LogOut className="w-4 h-4 text-rose-500" />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
