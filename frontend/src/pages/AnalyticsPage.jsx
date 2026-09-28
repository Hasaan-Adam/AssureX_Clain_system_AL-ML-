import React, { useState, useEffect } from 'react';
import analyticsAPI from '../api/analyticsAPI';
import Filters from '../components/analytics/Filters';
import TrendCharts from '../components/analytics/TrendCharts';
import ExportButtons from '../components/analytics/ExportButtons';
import Loader from '../components/common/Loader';
import { useNotification } from '../context/NotificationContext';
import { BarChart3, TrendingUp, Clock, CheckCircle2, ShieldAlert, Zap, AlertTriangle, Activity } from 'lucide-react';

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'trends', label: 'Trends' },
  { id: 'faults', label: 'Fault Analysis' },
  { id: 'fraud', label: 'Fraud Detection' },
  { id: 'reliability', label: 'Model Reliability' },
];

export const AnalyticsPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('30d');
  const [category, setCategory] = useState('ALL');
  const [decision, setDecision] = useState('ALL');
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(false);
  const { toastError } = useNotification();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const params = { time_range: timeRange, category, decision };
        let res;
        switch (activeTab) {
          case 'overview':
            res = await analyticsAPI.getOverview(params);
            break;
          case 'trends':
            res = await analyticsAPI.getAnalyticsTrends(params);
            break;
          case 'faults':
            res = await analyticsAPI.getFaultAnalysis(params);
            break;
          case 'fraud':
            res = await analyticsAPI.getFraudStats(params);
            break;
          case 'reliability':
            res = await analyticsAPI.getReliability(params);
            break;
          default:
            return;
        }
        setData(prev => ({ ...prev, [activeTab]: res.data || res }));
      } catch (err) {
        console.error(err);
        setData(prev => ({ ...prev, [activeTab]: null }));
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [activeTab, timeRange, category, decision]);

  const currentData = data[activeTab];

  const renderTabContent = () => {
    if (loading) return <Loader text={`Loading ${activeTab} data...`} />;
    if (!currentData || Object.keys(currentData).length === 0) {
      return (
        <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
          <p className="text-slate-500 dark:text-slate-400">No data available for the selected filters.</p>
        </div>
      );
    }

    switch (activeTab) {
      case 'overview':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <p className="text-sm font-medium text-slate-500">Brand Reliability</p>
              <p className="text-2xl font-bold mt-1 text-slate-900 dark:text-white">
                {currentData.brand_reliability ? `${currentData.brand_reliability}%` : 'N/A'}
              </p>
            </div>
            <div className="col-span-full mt-4">
              <div className="p-4 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
                 <h4 className="font-semibold mb-2 text-sm text-slate-700 dark:text-slate-300">Raw Overview Data</h4>
                 <pre className="overflow-auto text-xs text-slate-600 dark:text-slate-400">
                  {JSON.stringify(currentData, null, 2)}
                 </pre>
              </div>
            </div>
          </div>
        );
      case 'trends':
        return <TrendCharts data={currentData} />;
      case 'faults': {
        const faults = currentData.faults || (Array.isArray(currentData) ? currentData : []);
        if (!Array.isArray(faults) || faults.length === 0) {
           return <pre className="text-xs">{JSON.stringify(currentData, null, 2)}</pre>;
        }
        return (
          <div className="space-y-4">
            {faults.map((f, i) => {
              const val = f.value || f.count || f.percentage || 0;
              return (
                <div key={i} className="p-4 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                  <div className="flex justify-between mb-2">
                    <span className="font-semibold text-sm text-slate-700 dark:text-slate-300">{f.name || f.fault_type || f.type}</span>
                    <span className="text-sm font-bold text-slate-900 dark:text-white">{val}%</span>
                  </div>
                  <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2">
                    <div className="bg-brand-500 h-2 rounded-full" style={{ width: `${Math.min(val, 100)}%` }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        );
      }
      case 'fraud':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex flex-col items-center shadow-sm">
                <ShieldAlert className="w-8 h-8 text-red-500 mb-2" />
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Fraud Rate</span>
                <span className="text-3xl font-black text-red-600 mt-1">{currentData.fraud_rate || 0}%</span>
              </div>
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex flex-col items-center shadow-sm">
                <AlertTriangle className="w-8 h-8 text-orange-500 mb-2" />
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Flagged Count</span>
                <span className="text-3xl font-black text-slate-800 dark:text-white mt-1">{currentData.flagged_count || 0}</span>
              </div>
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex flex-col items-center shadow-sm">
                <Activity className="w-8 h-8 text-yellow-500 mb-2" />
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Fraud Score</span>
                <span className="text-3xl font-black text-slate-800 dark:text-white mt-1">{currentData.avg_fraud_score || 0}</span>
              </div>
            </div>
            {currentData.risk_levels && (
              <div className="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <h4 className="font-bold mb-5 text-slate-800 dark:text-white flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-slate-400"/>
                  Risk Level Distribution
                </h4>
                <div className="space-y-5">
                  {Object.entries(currentData.risk_levels).map(([level, val]) => {
                     let color = 'bg-emerald-500';
                     if (level.toLowerCase() === 'high') color = 'bg-red-500';
                     if (level.toLowerCase() === 'medium') color = 'bg-orange-500';
                     return (
                      <div key={level}>
                        <div className="flex justify-between text-xs font-semibold mb-2">
                          <span className="uppercase text-slate-600 dark:text-slate-400">{level}</span>
                          <span className="text-slate-800 dark:text-slate-200">{val}%</span>
                        </div>
                        <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2">
                          <div className={`h-2 rounded-full ${color}`} style={{ width: `${Math.min(val, 100)}%` }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        );
      case 'reliability':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-slate-800 dark:text-white">
                <Zap className="w-5 h-5 text-brand-500"/>
                Python ML Model
              </h3>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm font-semibold mb-2">
                    <span className="text-slate-600 dark:text-slate-400">Accuracy</span>
                    <span className="text-slate-900 dark:text-white">{currentData.ml_accuracy || 0}%</span>
                  </div>
                  <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2.5">
                    <div className="bg-brand-500 h-2.5 rounded-full" style={{ width: `${currentData.ml_accuracy || 0}%` }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm font-semibold mb-2">
                    <span className="text-slate-600 dark:text-slate-400">F1 Score</span>
                    <span className="text-slate-900 dark:text-white">{currentData.ml_f1 || 0}</span>
                  </div>
                  <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2.5">
                    <div className="bg-brand-400 h-2.5 rounded-full" style={{ width: `${Math.min((currentData.ml_f1 || 0) * 100, 100)}%` }}></div>
                  </div>
                </div>
              </div>
            </div>
            <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-slate-800 dark:text-white">
                <CheckCircle2 className="w-5 h-5 text-emerald-500"/>
                Traditional Rules Engine (TM)
              </h3>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm font-semibold mb-2">
                    <span className="text-slate-600 dark:text-slate-400">Accuracy</span>
                    <span className="text-slate-900 dark:text-white">{currentData.tm_accuracy || 0}%</span>
                  </div>
                  <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2.5">
                    <div className="bg-emerald-500 h-2.5 rounded-full" style={{ width: `${currentData.tm_accuracy || 0}%` }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm font-semibold mb-2">
                    <span className="text-slate-600 dark:text-slate-400">Coverage</span>
                    <span className="text-slate-900 dark:text-white">{currentData.tm_coverage || 0}%</span>
                  </div>
                  <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2.5">
                    <div className="bg-emerald-400 h-2.5 rounded-full" style={{ width: `${currentData.tm_coverage || 0}%` }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      {/* Page Header & Export Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white flex items-center gap-2.5">
            <BarChart3 className="w-6 h-6 text-brand-600" />
            <span>Adjudication Analytics & Insights</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Throughput velocity, ensemble model accuracy, and defect category intelligence
          </p>
        </div>
        <ExportButtons params={{ timeRange, category, decision }} />
      </div>

      {/* Filter Matrix */}
      <Filters
        timeRange={timeRange}
        onTimeRangeChange={setTimeRange}
        category={category}
        onCategoryChange={setCategory}
        decision={decision}
        onDecisionChange={setDecision}
      />

      {/* Tabs */}
      <div className="border-b border-slate-200 dark:border-slate-700">
        <nav className="-mb-px flex space-x-6 overflow-x-auto">
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                  : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 hover:border-slate-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="mt-6">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default AnalyticsPage;
