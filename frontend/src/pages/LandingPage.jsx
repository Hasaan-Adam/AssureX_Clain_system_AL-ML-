import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, Sparkles, Cpu, FileSearch, Clock, Layers, Brain, Zap, 
  ShieldAlert, BarChart, Lock, Users, Menu, X, 
  Github, Mail, Globe 
} from 'lucide-react';

const LandingPage = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [isAuthenticated] = useState(false); // Can be replaced with actual auth context

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const statsRef = useRef(null);
  const [statsVisible, setStatsVisible] = useState(false);
  const [countAcc, setCountAcc] = useState(0);
  const [countTime, setCountTime] = useState(0);
  const [countScenarios, setCountScenarios] = useState(0);
  const [countModels, setCountModels] = useState(0);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setStatsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );
    if (statsRef.current) {
      observer.observe(statsRef.current);
    }
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (statsVisible) {
      const duration = 1500;
      const steps = 60;
      const stepTime = duration / steps;
      
      let currentStep = 0;
      const timer = setInterval(() => {
        currentStep++;
        const progress = currentStep / steps;
        
        setCountAcc(Math.floor(progress * 97));
        setCountTime(progress * 3);
        setCountScenarios(Math.floor(progress * 11));
        setCountModels(Math.floor(progress * 2));

        if (currentStep >= steps) {
          clearInterval(timer);
          setCountAcc(97);
          setCountTime(3);
          setCountScenarios(11);
          setCountModels(2);
        }
      }, stepTime);
      return () => clearInterval(timer);
    }
  }, [statsVisible]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 font-sans text-slate-900 dark:text-slate-50 overflow-x-hidden">
      {/* SECTION 1 - Navbar (Floating Pill Design) */}
      <nav className={`fixed top-4 left-1/2 -translate-x-1/2 w-[95%] max-w-6xl z-50 transition-all duration-500 rounded-full ${isScrolled ? 'bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-slate-200/50 dark:border-slate-700/50 shadow-xl shadow-slate-200/40 dark:shadow-none' : 'bg-white/40 dark:bg-slate-900/40 backdrop-blur-md border border-white/50 dark:border-slate-700/50 shadow-lg shadow-slate-200/10 dark:shadow-none'}`}>
        <div className="px-5 sm:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center cursor-pointer" onClick={() => window.scrollTo(0,0)}>
              <img src="/logo.png" alt="AssureX Logo" className="h-10 sm:h-11 w-auto object-contain drop-shadow-sm" />
            </div>
            
            <div className="hidden md:flex items-center space-x-1">
              <a href="#features" className="px-4 py-2 rounded-full text-sm font-bold text-slate-600 dark:text-slate-300 hover:text-brand-600 dark:hover:text-brand-400 hover:bg-slate-100/50 dark:hover:bg-slate-800/50 transition-all">Features</a>
              <a href="#how-it-works" className="px-4 py-2 rounded-full text-sm font-bold text-slate-600 dark:text-slate-300 hover:text-brand-600 dark:hover:text-brand-400 hover:bg-slate-100/50 dark:hover:bg-slate-800/50 transition-all">How It Works</a>
              <a href="#ai-engine" className="px-4 py-2 rounded-full text-sm font-bold text-slate-600 dark:text-slate-300 hover:text-brand-600 dark:hover:text-brand-400 hover:bg-slate-100/50 dark:hover:bg-slate-800/50 transition-all">AI Engine</a>
            </div>

            <div className="hidden md:flex items-center space-x-3">
              {isAuthenticated ? (
                <Link to="/dashboard" className="px-5 py-2.5 rounded-full text-sm font-bold text-white bg-brand-600 hover:bg-brand-500 shadow-md shadow-brand-500/25 transition-all hover:scale-105 active:scale-95 flex items-center gap-2">
                  Dashboard <ArrowRight className="w-4 h-4" />
                </Link>
              ) : (
                <>
                  <Link to="/login" className="px-5 py-2.5 rounded-full text-sm font-bold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">Sign In</Link>
                  <Link to="/register" className="px-6 py-2.5 rounded-full text-sm font-bold text-white bg-slate-900 dark:bg-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-100 shadow-md transition-all hover:scale-105 active:scale-95">Get Started</Link>
                </>
              )}
            </div>

            <div className="md:hidden flex items-center">
              <button onClick={() => setMenuOpen(!menuOpen)} className="p-2 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>
        
        {/* Mobile menu */}
        <div className={`md:hidden overflow-hidden transition-all duration-300 ${menuOpen ? 'max-h-[400px] border-t border-slate-200/50 dark:border-slate-700/50 opacity-100' : 'max-h-0 opacity-0'}`}>
          <div className="p-5 flex flex-col space-y-2">
            <a href="#features" className="px-4 py-3 rounded-2xl bg-slate-50 dark:bg-slate-800/50 text-slate-700 dark:text-slate-200 font-bold text-center" onClick={() => setMenuOpen(false)}>Features</a>
            <a href="#how-it-works" className="px-4 py-3 rounded-2xl bg-slate-50 dark:bg-slate-800/50 text-slate-700 dark:text-slate-200 font-bold text-center" onClick={() => setMenuOpen(false)}>How It Works</a>
            <a href="#ai-engine" className="px-4 py-3 rounded-2xl bg-slate-50 dark:bg-slate-800/50 text-slate-700 dark:text-slate-200 font-bold text-center" onClick={() => setMenuOpen(false)}>AI Engine</a>
            <div className="pt-3 flex flex-col space-y-2">
              {isAuthenticated ? (
                <Link to="/dashboard" className="w-full text-center bg-brand-600 text-white px-4 py-3 rounded-2xl font-bold shadow-md" onClick={() => setMenuOpen(false)}>Go to Dashboard</Link>
              ) : (
                <>
                  <Link to="/login" className="w-full text-center bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 px-4 py-3 rounded-2xl font-bold" onClick={() => setMenuOpen(false)}>Sign In</Link>
                  <Link to="/register" className="w-full text-center bg-slate-900 dark:bg-white dark:text-slate-900 text-white px-4 py-3 rounded-2xl font-bold shadow-md" onClick={() => setMenuOpen(false)}>Get Started</Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* SECTION 2 - Hero (Collage Style) */}
        <section className="relative pt-24 pb-16 lg:pt-36 lg:pb-24 overflow-hidden min-h-screen flex items-center">
          <div className="absolute top-0 right-0 w-[80%] h-[120%] bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-brand-400/20 via-slate-50/5 dark:via-slate-950/5 to-transparent pointer-events-none blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-[80%] h-[120%] bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-accent-peach/10 via-slate-50/5 dark:via-slate-950/5 to-transparent pointer-events-none blur-3xl"></div>
          
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-8 items-center">
              
              {/* Left Column - Text Content */}
              <div className="flex flex-col items-start text-left">
                
                
                <h1 className="text-5xl sm:text-6xl lg:text-[5rem] font-black tracking-tight text-slate-900 dark:text-white leading-[1.1] mb-6">
                  Warranty Claims<br />
                  Evaluated by AI<br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 via-brand-400 to-accent-peach">in Seconds</span>
                </h1>
                
                <p className="max-w-xl text-lg text-slate-600 dark:text-slate-400 mb-10 leading-relaxed font-medium">
                  AssureX combines Python Machine Learning and Google Teachable Machine to auto-adjudicate equipment warranty claims &mdash; instantly, transparently, and accurately.
                </p>
                
                <div className="flex flex-col sm:flex-row gap-4 mb-10 w-full sm:w-auto">
                  <Link to="/register" className="inline-flex justify-center items-center gap-2 bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-700 hover:to-brand-600 text-white px-8 py-4 rounded-full font-bold text-lg transition-all shadow-[0_0_40px_-10px_rgba(35,206,217,0.5)] hover:shadow-[0_0_60px_-15px_rgba(35,206,217,0.7)] hover:-translate-y-1">
                    Start Your Claim &rarr;
                  </Link>
                  <Link to="/login" className="inline-flex justify-center items-center px-8 py-4 rounded-full font-bold text-lg text-slate-700 dark:text-slate-200 border-2 border-slate-200 dark:border-slate-700 hover:border-brand-500 dark:hover:border-brand-400 hover:text-brand-600 dark:hover:text-brand-400 hover:bg-brand-50 dark:hover:bg-slate-800 transition-all">
                    Sign In
                  </Link>
                </div>

                <div className="flex flex-wrap gap-6 text-sm font-bold text-slate-500 dark:text-slate-400">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-5 h-5 text-accent-peach" />
                    <span>Dual-AI Engine</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <FileSearch className="w-5 h-5 text-accent-green" />
                    <span>OCR Verified</span>
                  </div>
                </div>
              </div>
              
              {/* Right Column - Image Collage */}
              <div className="relative h-[500px] lg:h-[600px] w-full hidden sm:block">
                {/* Main Large Image */}
                <div className="absolute top-10 right-10 w-[65%] h-[60%] rounded-3xl overflow-hidden shadow-2xl border-4 border-white dark:border-slate-800 z-10 transition-transform hover:-translate-y-2 hover:rotate-1 duration-500">
                  <div className="absolute inset-0 bg-brand-600/10 mix-blend-overlay z-10"></div>
                  <img src="https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&q=80&w=800" alt="Appliance Repair" className="w-full h-full object-cover" />
                </div>
                
                {/* Bottom Left Image */}
                <div className="absolute bottom-10 left-10 w-[55%] h-[45%] rounded-3xl overflow-hidden shadow-2xl border-4 border-white dark:border-slate-800 z-20 transition-transform hover:-translate-y-2 hover:-rotate-2 duration-500">
                  <img src="https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?auto=format&fit=crop&q=80&w=600" alt="Tech Device" className="w-full h-full object-cover" />
                </div>
                
                {/* Top Left Floating Data/Code Image */}
                <div className="absolute top-0 left-5 w-[45%] h-[35%] rounded-3xl overflow-hidden shadow-2xl border-4 border-white dark:border-slate-800 z-30 transition-transform hover:-translate-y-2 hover:rotate-3 duration-500">
                  <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=600" alt="AI Data" className="w-full h-full object-cover" />
                </div>

                {/* Floating UI Elements */}
                <div className="absolute bottom-24 right-5 bg-white dark:bg-slate-900 rounded-2xl p-4 shadow-xl border border-slate-200 dark:border-slate-700 z-40 animate-slide-up flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center">
                    <ShieldCheck className="w-6 h-6 text-emerald-600" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 font-bold uppercase">AI Decision</p>
                    <p className="text-sm font-black text-slate-900 dark:text-white">Claim Approved</p>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </section>

      {/* SECTION 3 - Live Stats Bar (Digital & Professional) */}
        <section ref={statsRef} className="relative z-30 -mt-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto pb-24">
          <div className="relative rounded-3xl bg-slate-900/80 dark:bg-slate-950/80 backdrop-blur-2xl border border-slate-700/50 shadow-[0_0_50px_-12px_rgba(35,206,217,0.2)] overflow-hidden">
            {/* Digital Grid Background */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none opacity-20"></div>
            
            <div className="absolute top-0 left-1/4 w-1/2 h-px bg-gradient-to-r from-transparent via-brand-400 to-transparent shadow-[0_0_10px_rgba(35,206,217,0.8)]"></div>

            <div className="relative grid grid-cols-2 lg:grid-cols-4 gap-px bg-slate-800/50">
              {/* Stat 1 */}
              <div className="bg-slate-900/90 p-8 sm:p-10 flex flex-col items-center justify-center text-center group hover:bg-slate-800/90 transition-colors">
                <div className="w-12 h-12 rounded-2xl bg-brand-500/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                  <ShieldCheck className="w-6 h-6 text-brand-400" />
                </div>
                <div className="text-4xl lg:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-slate-400 mb-2 drop-shadow-sm">{countAcc}%+</div>
                <div className="text-xs font-mono uppercase tracking-widest text-brand-300/80">Model Accuracy</div>
              </div>

              {/* Stat 2 */}
              <div className="bg-slate-900/90 p-8 sm:p-10 flex flex-col items-center justify-center text-center group hover:bg-slate-800/90 transition-colors">
                <div className="w-12 h-12 rounded-2xl bg-accent-peach/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                  <Clock className="w-6 h-6 text-accent-peach" />
                </div>
                <div className="text-4xl lg:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-slate-400 mb-2 drop-shadow-sm">&lt; {countTime === 3 ? '3' : (countTime).toFixed(1)}s</div>
                <div className="text-xs font-mono uppercase tracking-widest text-accent-peach/80">Avg Decision Time</div>
              </div>

              {/* Stat 3 */}
              <div className="bg-slate-900/90 p-8 sm:p-10 flex flex-col items-center justify-center text-center group hover:bg-slate-800/90 transition-colors">
                <div className="w-12 h-12 rounded-2xl bg-accent-yellow/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                  <Cpu className="w-6 h-6 text-accent-yellow" />
                </div>
                <div className="text-4xl lg:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-slate-400 mb-2 drop-shadow-sm">{countScenarios}</div>
                <div className="text-xs font-mono uppercase tracking-widest text-accent-yellow/80">Scenarios Covered</div>
              </div>

              {/* Stat 4 */}
              <div className="bg-slate-900/90 p-8 sm:p-10 flex flex-col items-center justify-center text-center group hover:bg-slate-800/90 transition-colors">
                <div className="w-12 h-12 rounded-2xl bg-accent-green/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                  <Layers className="w-6 h-6 text-accent-green" />
                </div>
                <div className="text-4xl lg:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-slate-400 mb-2 drop-shadow-sm">{countModels}</div>
                <div className="text-xs font-mono uppercase tracking-widest text-accent-green/80">Models in Ensemble</div>
              </div>
            </div>
            
            <div className="absolute bottom-0 left-1/4 w-1/2 h-px bg-gradient-to-r from-transparent via-brand-600 to-transparent"></div>
          </div>
        </section>

      {/* SECTION 4 - How It Works */}
      <section id="how-it-works" className="py-24 bg-white dark:bg-slate-900 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4">How It Works</h2>
            <p className="text-slate-600 dark:text-slate-400 text-lg">From submission to decision in three simple steps.</p>
          </div>
          
          <div className="relative">
            {/* Desktop connecting line */}
            <div className="hidden md:block absolute top-12 left-[15%] right-[15%] h-0.5 border-t-2 border-dashed border-slate-200 dark:border-slate-700 z-0"></div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative z-10">
              {/* Step 1 */}
              <div className="flex flex-col items-center text-center">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-brand-100 to-white dark:from-slate-800 dark:to-slate-900 border-4 border-white dark:border-slate-900 shadow-xl flex items-center justify-center mb-6 relative">
                  <span className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-brand-600 text-white font-bold flex items-center justify-center text-sm shadow-md">1</span>
                  <ShieldCheck className="w-10 h-10 text-brand-600 dark:text-brand-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Register Warranty</h3>
                <p className="text-slate-600 dark:text-slate-400">Upload your purchase invoice and product serial number to activate coverage.</p>
              </div>
              
              {/* Step 2 */}
              <div className="flex flex-col items-center text-center">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-brand-100 to-white dark:from-slate-800 dark:to-slate-900 border-4 border-white dark:border-slate-900 shadow-xl flex items-center justify-center mb-6 relative">
                  <span className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-brand-600 text-white font-bold flex items-center justify-center text-sm shadow-md">2</span>
                  <FileSearch className="w-10 h-10 text-brand-600 dark:text-brand-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Submit a Claim</h3>
                <p className="text-slate-600 dark:text-slate-400">Describe the fault, upload photos, and our OCR engine verifies your documents automatically.</p>
              </div>
              
              {/* Step 3 */}
              <div className="flex flex-col items-center text-center">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-brand-100 to-white dark:from-slate-800 dark:to-slate-900 border-4 border-white dark:border-slate-900 shadow-xl flex items-center justify-center mb-6 relative">
                  <span className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-brand-600 text-white font-bold flex items-center justify-center text-sm shadow-md">3</span>
                  <Cpu className="w-10 h-10 text-brand-600 dark:text-brand-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">AI Adjudicates</h3>
                <p className="text-slate-600 dark:text-slate-400">Our dual-model ensemble (tabular ML + Teachable Machine vision) returns a decision in seconds.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 5 - Features Grid */}
      <section id="features" className="py-24 bg-slate-50 dark:bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4">Everything Built In</h2>
            <p className="text-slate-600 dark:text-slate-400 text-lg">A complete platform for intelligent warranty lifecycle management.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="p-8 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-brand-50 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400 flex items-center justify-center mb-6">
                <Brain className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Dual-Model Ensemble</h3>
              <p className="text-slate-600 dark:text-slate-400 line-clamp-3">XGBoost tabular classifier + Google Teachable Machine vision work together for maximum accuracy.</p>
            </div>
            
            <div className="p-8 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 flex items-center justify-center mb-6">
                <Zap className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Real-Time OCR</h3>
              <p className="text-slate-600 dark:text-slate-400 line-clamp-3">Tesseract-powered document scanning extracts invoice amounts, dates, and serial numbers automatically.</p>
            </div>
            
            <div className="p-8 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-rose-50 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 flex items-center justify-center mb-6">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Fraud Detection</h3>
              <p className="text-slate-600 dark:text-slate-400 line-clamp-3">Multi-signal anomaly scoring flags duplicates, serial mismatches, and contradictions before human review.</p>
            </div>
            
            <div className="p-8 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-violet-50 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 flex items-center justify-center mb-6">
                <BarChart className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Analytics Dashboard</h3>
              <p className="text-slate-600 dark:text-slate-400 line-clamp-3">Trend charts, fault category breakdowns, fraud stats, and model reliability metrics in one place.</p>
            </div>
            
            <div className="p-8 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-6">
                <Lock className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Policy Rule Engine</h3>
              <p className="text-slate-600 dark:text-slate-400 line-clamp-3">Deterministic warranty rules enforce coverage limits, expiry dates, and exclusion clauses automatically.</p>
            </div>
            
            <div className="p-8 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-6">
                <Users className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Role-Based Portal</h3>
              <p className="text-slate-600 dark:text-slate-400 line-clamp-3">Separate dashboards for customers, reviewers, and administrators with granular access control.</p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 6 - AI Engine Showcase */}
      <section id="ai-engine" className="py-24 bg-gradient-to-br from-slate-900 via-brand-950 to-slate-900 text-white overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row items-center gap-16">
            <div className="w-full lg:w-1/2 space-y-8">
              <div>
                <span className="text-brand-400 font-bold tracking-wider text-sm uppercase">Our AI Engine</span>
                <h2 className="text-4xl md:text-5xl font-extrabold mt-2 leading-tight">Two Models, One<br />Confident Decision</h2>
              </div>
              <p className="text-lg text-slate-300 leading-relaxed">
                We built a hybrid ensemble that first runs deterministic policy rules, then passes the claim through a trained tabular ML model, and finally cross-validates the visual evidence with Google Teachable Machine. Only when all systems agree does the claim get auto-approved.
              </p>
              
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="mt-1 p-2 bg-brand-500/20 rounded-lg text-brand-400">
                    <Brain className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-white">Python ML (scikit-learn)</h4>
                    <p className="text-slate-400 text-sm">Trained on 1,500 synthetic claims with 23 engineered features</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="mt-1 p-2 bg-purple-500/20 rounded-lg text-purple-400">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-white">Teachable Machine Vision</h4>
                    <p className="text-slate-400 text-sm">Trained on 224&times;224 RGB claim card images</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="w-full lg:w-1/2 relative">
              <div className="absolute inset-0 bg-brand-500/20 blur-[100px] rounded-full pointer-events-none"></div>
              <div className="relative bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 md:p-8 shadow-2xl shadow-brand-900/50">
                <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                  <Cpu className="w-6 h-6 text-brand-400" /> AI Adjudication Pipeline
                </h3>
                
                <div className="space-y-4 mb-8">
                  <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-sm text-slate-300">1. Rule Engine</span>
                      <span className="text-xs text-emerald-400 flex items-center gap-1"><ShieldCheck className="w-3 h-3" /> Policy validated</span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-2">
                      <div className="bg-emerald-500 h-2 rounded-full w-full"></div>
                    </div>
                  </div>
                  
                  <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-sm text-slate-300">2. ML Model</span>
                      <span className="text-xs text-brand-400">89% confidence</span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-2">
                      <div className="bg-brand-500 h-2 rounded-full w-[89%]"></div>
                    </div>
                  </div>
                  
                  <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-sm text-slate-300">3. Vision Model</span>
                      <span className="text-xs text-purple-400">84% match</span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-2">
                      <div className="bg-purple-500 h-2 rounded-full w-[84%]"></div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 text-center">
                  <div className="text-emerald-400 font-bold text-xl tracking-wide flex items-center justify-center gap-2">
                    <ShieldCheck className="w-6 h-6" /> AUTO APPROVED
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 7 - Testimonials / Use Cases */}
      <section className="py-24 bg-slate-50 dark:bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4">Built for Real Scenarios</h2>
            <p className="text-slate-600 dark:text-slate-400 text-lg">See how the engine handles different claim types.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Card 1 */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 border-l-4 border-l-emerald-500 flex flex-col h-full">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-lg">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-slate-900 dark:text-white">Valid Warranty Claim</h3>
              </div>
              <p className="text-slate-600 dark:text-slate-400 text-sm flex-grow mb-6">
                Customer uploads invoice, photos. OCR extracts serial. Rules pass. ML returns 91% confidence. Approved in 2.1 seconds.
              </p>
              <div className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/20 px-3 py-1.5 rounded-full inline-flex items-center w-max">
                &check; Auto-Approved
              </div>
            </div>
            
            {/* Card 2 */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 border-l-4 border-l-rose-500 flex flex-col h-full">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 rounded-lg">
                  <ShieldAlert className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-slate-900 dark:text-white">Duplicate Submission Detected</h3>
              </div>
              <p className="text-slate-600 dark:text-slate-400 text-sm flex-grow mb-6">
                System detects matching document hash from a prior claim. Fraud score spikes to 0.78. Claim auto-rejected with audit trail.
              </p>
              <div className="text-xs font-bold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-900/20 px-3 py-1.5 rounded-full inline-flex items-center w-max">
                &cross; Auto-Rejected
              </div>
            </div>
            
            {/* Card 3 */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 border-l-4 border-l-amber-500 flex flex-col h-full">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 rounded-lg">
                  <Brain className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-slate-900 dark:text-white">Model Disagreement &mdash; Human Review</h3>
              </div>
              <p className="text-slate-600 dark:text-slate-400 text-sm flex-grow mb-6">
                ML says approve (76%), but vision model detects borderline wear pattern. Disagreement triggers manual adjudicator queue.
              </p>
              <div className="text-xs font-bold text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 px-3 py-1.5 rounded-full inline-flex items-center w-max">
                &#9888; Sent to Review Queue
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 8 - CTA Banner */}
      <section className="py-20 bg-gradient-to-r from-slate-900 to-brand-950 text-center relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4IiBoZWlnaHQ9IjgiPgo8cmVjdCB3aWR0aD0iOCIgaGVpZ2h0PSI4IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDUiLz4KPHBhdGggZD0iTTAgMEw4IDhaTTAgOEw4IDBaIiBzdHJva2U9IiNmZmYiIHN0cm9rZS1vcGFjaXR5PSIwLjAyNSIgc3Ryb2tlLXdpZHRoPSIxIi8+Cjwvc3ZnPg==')] opacity-30"></div>
        <div className="relative z-10 max-w-4xl mx-auto px-4">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">Ready to See It in Action?</h2>
          <p className="text-xl text-slate-300 mb-10">Register an account and submit a test claim through our full adjudication pipeline.</p>
          <div className="flex flex-col sm:flex-row justify-center gap-4 mb-8">
            <Link to="/register" className="bg-brand-500 hover:bg-brand-600 text-white px-8 py-3 rounded-xl font-bold text-lg transition-colors shadow-lg">
              Create Account &rarr;
            </Link>
            <Link to="/login" className="bg-slate-800 hover:bg-slate-700 text-white px-8 py-3 rounded-xl font-bold text-lg transition-colors border border-slate-600">
              Sign In
            </Link>
          </div>
          <p className="text-sm text-slate-400">Academic project &middot; TechWizz 2026 NextWave AI Competition</p>
        </div>
      </section>

      {/* SECTION 9 - Footer */}
      <footer className="bg-slate-950 text-slate-400 pt-16 pb-8 border-t border-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
            
            {/* Col 1 */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-white mb-6">
                <ShieldCheck className="h-6 w-6 text-brand-500" />
                <span className="text-lg font-bold">AssureX Claim Engine</span>
              </div>
              <p className="text-sm text-slate-500">
                AI-powered warranty claim adjudication built for accuracy, speed, and transparency.
              </p>
              <div className="flex space-x-4 pt-2">
                <a href="#" className="text-slate-500 hover:text-white transition-colors"><Github className="w-5 h-5" /></a>
                <a href="#" className="text-slate-500 hover:text-white transition-colors"><Mail className="w-5 h-5" /></a>
                <a href="#" className="text-slate-500 hover:text-white transition-colors"><Globe className="w-5 h-5" /></a>
              </div>
            </div>
            
            {/* Col 2 */}
            <div>
              <h4 className="text-white font-semibold mb-6">Platform</h4>
              <ul className="space-y-3 text-sm">
                <li><a href="#features" className="hover:text-brand-400 transition-colors">Features</a></li>
                <li><a href="#how-it-works" className="hover:text-brand-400 transition-colors">How It Works</a></li>
                <li><a href="#ai-engine" className="hover:text-brand-400 transition-colors">AI Engine</a></li>
                <li><Link to="/dashboard" className="hover:text-brand-400 transition-colors">Analytics</Link></li>
                <li><Link to="/admin" className="hover:text-brand-400 transition-colors">Admin Console</Link></li>
              </ul>
            </div>
            
            {/* Col 3 */}
            <div>
              <h4 className="text-white font-semibold mb-6">Account</h4>
              <ul className="space-y-3 text-sm">
                <li><Link to="/login" className="hover:text-brand-400 transition-colors">Sign In</Link></li>
                <li><Link to="/register" className="hover:text-brand-400 transition-colors">Create Account</Link></li>
                <li><Link to="/dashboard" className="hover:text-brand-400 transition-colors">Customer Portal</Link></li>
                <li><Link to="/reviewer" className="hover:text-brand-400 transition-colors">Reviewer Portal</Link></li>
              </ul>
            </div>
            
            {/* Col 4 */}
            <div>
              <h4 className="text-white font-semibold mb-6">Project Info</h4>
              <ul className="space-y-3 text-sm text-slate-500">
                <li>Built for Aptech NextWave AI & ML</li>
                <li className="pt-2">Stack: FastAPI &middot; React &middot; SQLite &middot; scikit-learn &middot; Teachable Machine</li>
                <li className="pt-2 text-slate-400">Ahmed Bilal Khan &middot; Bushra Khalid &middot; Komal Mubeen &middot; Areeb Mughal</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-center items-center gap-4 text-sm text-slate-600">
            <p>&copy; 2026 AssureX Claim Engine. Academic Project.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;






