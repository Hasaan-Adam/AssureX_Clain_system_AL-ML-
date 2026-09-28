import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Compass, Map } from 'lucide-react';

export const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col items-center justify-center p-6 text-center overflow-hidden relative">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-brand-500/10 dark:bg-brand-500/5 blur-[100px] rounded-full pointer-events-none" />

      <div className="relative z-10 flex flex-col items-center">
        <div className="flex items-center justify-center mb-6 relative">
          <Map className="w-24 h-24 text-slate-200 dark:text-slate-800 absolute -z-10 animate-pulse" />
          <Compass className="w-16 h-16 text-brand-500 animate-[spin_4s_linear_infinite]" />
        </div>

        <h1 className="text-8xl sm:text-9xl font-black tracking-tighter mb-4">
          <span className="bg-gradient-to-br from-brand-600 via-brand-500 to-cyan-400 bg-clip-text text-transparent drop-shadow-sm">
            404
          </span>
        </h1>
        
        <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-3">
          Lost in the Engine
        </h2>
        
        <p className="text-base text-slate-500 dark:text-slate-400 max-w-md mb-8 leading-relaxed">
          The requested claim, document, or portal endpoint does not exist. It might have been relocated or completely erased from our records.
        </p>

        <Link
          to="/"
          className="group flex items-center gap-2 px-6 py-3 bg-brand-600 hover:bg-brand-500 text-white text-sm font-bold rounded-2xl shadow-xl shadow-brand-500/25 transition-all hover:-translate-y-0.5"
        >
          <Home className="w-4 h-4 group-hover:scale-110 transition-transform" />
          <span>Back to Safety</span>
        </Link>
      </div>
    </div>
  );
};

export default NotFoundPage;
