import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  LayoutDashboard, 
  FileText, 
  PlusCircle, 
  ShieldCheck, 
  Package, 
  CheckSquare, 
  BarChart3, 
  Settings, 
  ShieldAlert,
  HelpCircle,
  Sparkles,
  User as UserIcon,
  Users,
  Circle,
  Download
} from 'lucide-react';
import Badge from './Badge';

export const Sidebar = ({ isOpen, onClose }) => {
  const { user, isAdmin, isReviewer, isStaff } = useAuth();

  let navItems = [];

  if (isAdmin) {
    navItems = [
      {
        label: 'Administration',
        items: [
          { name: 'Admin Console', path: '/admin', icon: ShieldAlert },
          { name: 'Review Queue', path: '/reviews', icon: CheckSquare, badge: 'Queue' },
          { name: 'Claims Registry', path: '/claims', icon: FileText },
          { name: 'Warranty Registry', path: '/warranties', icon: ShieldCheck },
          { name: 'Product Catalog', path: '/products', icon: Package },
        ],
      },
      {
        label: 'Analytics & Governance',
        items: [
          { name: 'Analytics & Trends', path: '/analytics', icon: BarChart3 },
          { name: 'Reports & Export', path: '/reports', icon: Download },
          { name: 'User Management', path: '/users', icon: Users },
          { name: 'Global Audit Logs', path: '/admin/audit-logs', icon: ShieldAlert },
          { name: 'Warranty Policies', path: '/admin/policies', icon: Settings },
          { name: 'System Settings', path: '/settings', icon: Settings },
        ],
      },
    ];
  } else if (isReviewer || isStaff) {
    navItems = [
      {
        label: 'Adjudication Ops',
        items: [
          { name: 'Review Queue', path: '/reviews', icon: CheckSquare, badge: 'Queue' },
          { name: 'Claims Registry', path: '/claims', icon: FileText },
          { name: 'File Customer Claim', path: '/claims/new', icon: PlusCircle, badge: 'AI' },
          { name: 'Warranty Registry', path: '/warranties', icon: ShieldCheck },
          { name: 'Product Catalog', path: '/products', icon: Package },
        ],
      },
      {
        label: 'Intelligence & Reports',
        items: [
          { name: 'Analytics & Trends', path: '/analytics', icon: BarChart3 },
          { name: 'Reports & Export', path: '/reports', icon: Download },
        ],
      },
    ];
  } else {
    navItems = [
      {
        label: 'Main',
        items: [
          { name: 'Claim Dashboard', path: '/dashboard', icon: LayoutDashboard },
          { name: 'My Claims', path: '/claims', icon: FileText },
          { name: 'Submit New Claim', path: '/claims/new', icon: PlusCircle, badge: 'AI' },
          { name: 'My Warranties', path: '/warranties', icon: ShieldCheck },
          { name: 'Product Catalog', path: '/products', icon: Package },
        ],
      },
    ];
  }

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-slate-900/50 backdrop-blur-sm md:hidden transition-opacity"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed md:sticky top-0 z-40 h-screen w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col transition-transform duration-300 ease-out shrink-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <NavLink
          to={isAdmin ? '/admin' : isReviewer || isStaff ? '/reviews' : '/dashboard'}
          className="h-18 py-4 flex items-center px-6 border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
        >
          <img src="/logo.png" alt="AssureX Logo" className="h-11 w-auto object-contain drop-shadow-sm" />
        </NavLink>

        <div className="flex flex-col flex-1 overflow-y-auto">
          {/* User Profile Section */}
          {user && (
            <div className="p-5 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-brand-500 to-brand-500 text-white flex items-center justify-center text-sm font-bold shadow-md shrink-0">
                  {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-sm font-bold text-slate-900 dark:text-white truncate">
                    {user.full_name || 'User'}
                  </span>
                  <div className="mt-0.5">
                    <Badge type="status" value={user.role || 'CUSTOMER'} size="sm" />
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="p-4 space-y-6">
            {navItems.map((section, idx) => (
              <div key={idx}>
                <p className="px-3 text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-3">
                  {section.label}
                </p>
                <div className="space-y-1">
                  {section.items.map((item) => {
                    const Icon = item.icon;
                    return (
                      <NavLink
                        key={item.path}
                        to={item.path}
                        onClick={onClose}
                        className={({ isActive }) =>
                          `group flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ease-in-out ${
                            isActive
                              ? 'bg-brand-50 dark:bg-brand-900/40 text-brand-700 dark:text-brand-300 shadow-sm ring-1 ring-brand-100 dark:ring-brand-800'
                              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                          }`
                        }
                      >
                        <div className="flex items-center gap-3">
                          <Icon className="w-5 h-5 shrink-0 transition-transform group-hover:scale-110" />
                          <span>{item.name}</span>
                        </div>
                        {item.badge && (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-brand-100 dark:bg-brand-800/60 text-brand-700 dark:text-brand-300">
                            {item.badge}
                          </span>
                        )}
                      </NavLink>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom AI Status Indicator */}
        <div className="p-4 mt-auto border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
          <div className="flex items-center gap-3 p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-md transition-shadow">
            <div className="relative flex h-3 w-3 shrink-0">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                <Sparkles className="w-3 h-3 text-brand-500" />
                AssureX AI v1.0 Active
              </span>
              <span className="text-[10px] text-slate-500 dark:text-slate-400">
                System operational
              </span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;

