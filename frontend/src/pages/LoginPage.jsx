import React from 'react';
import { Link } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';
import { Shield, Zap, BarChart3, Lock } from 'lucide-react';

export const LoginPage = () => {
  return (
    <div className="h-screen overflow-hidden flex w-full">
      {/* Left Panel - Brand/Visuals */}
      <div className="hidden lg:flex w-1/2 bg-slate-950 flex-col justify-between relative overflow-hidden p-8 lg:p-12 xl:p-16 border-r border-slate-800">
        {/* Background Effects */}
        <div className="absolute top-0 left-0 w-full h-full bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-brand-500/20 rounded-full blur-[120px] mix-blend-screen pointer-events-none"></div>
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-blue-500/20 rounded-full blur-[120px] mix-blend-screen pointer-events-none"></div>
        
        {/* Top: Logo */}
        <div className="relative z-10">
          <Link to="/" className="inline-block group">
            <img 
              src="/logo.png" 
              alt="AssureX Logo" 
              className="h-16 w-auto object-contain drop-shadow-[0_10px_25px_rgba(59,130,246,0.35)] transition-transform duration-300 group-hover:scale-105" 
            />
          </Link>
        </div>

        {/* Middle: Value Prop */}
        <div className="relative z-10 my-auto pr-4">
          <h1 className="text-2xl xl:text-3xl font-bold text-white mb-4 leading-tight tracking-tight">
            Automating Warranty Adjudication with <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 to-blue-400">Next-Gen AI</span>
          </h1>
          <p className="text-slate-400 text-base xl:text-lg max-w-lg leading-relaxed">
            Transform your claims process with intelligent automation. Reduce review times from days to seconds while maintaining perfect accuracy.
          </p>
        </div>

        {/* Bottom: Footer / Quote */}
        <div className="relative z-10 flex items-center justify-between text-xs text-slate-500">
          <p>© {new Date().getFullYear()} AssureX Claim Engine.</p>
        </div>
      </div>
      
      {/* Right Panel - Auth Form */}
      <div className="w-full lg:w-1/2 bg-white dark:bg-slate-950 flex flex-col justify-between h-full overflow-y-auto px-6 sm:px-12 lg:px-14 xl:px-20 py-6">
        {/* Top Header Navigation */}
        <div className="w-full flex items-center justify-between sm:justify-end pb-4 border-b border-slate-100 dark:border-slate-800 lg:border-none">
          <Link to="/" className="lg:hidden">
            <img src="/logo.png" alt="AssureX" className="h-8 w-auto object-contain" />
          </Link>
          <div className="flex items-center gap-2 text-xs sm:text-sm">
            <span className="text-slate-500 dark:text-slate-400 hidden sm:inline">New to AssureX?</span>
            <Link
              to="/register"
              className="px-4 py-2 text-xs sm:text-sm font-semibold text-brand-600 dark:text-brand-400 bg-brand-50 hover:bg-brand-100 dark:bg-brand-950/60 dark:hover:bg-brand-900/60 border border-brand-200 dark:border-brand-800 rounded-xl transition-all shadow-sm"
            >
              Create Account →
            </Link>
          </div>
        </div>

        <div className="w-full max-w-md my-auto py-4">
          <LoginForm />
        </div>

        {/* Mobile footer */}
        <div className="text-center text-[11px] text-slate-400 py-2 lg:hidden">
          © {new Date().getFullYear()} AssureX Claim Engine
        </div>
      </div>
    </div>
  );
};

export default LoginPage;

