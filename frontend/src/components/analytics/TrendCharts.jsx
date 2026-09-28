import React from 'react';
import { ClaimTrendsChart, DecisionDistributionChart, CategoryBreakdownChart } from '../dashboard/Charts';
import { BarChart2, Activity, Zap } from 'lucide-react';

export const TrendCharts = ({ data }) => {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
        <p className="text-slate-500 dark:text-slate-400">No data available for the selected filters.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top 2 charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {data?.trends ? <ClaimTrendsChart data={data.trends} /> : <div className="p-4 text-center text-sm text-slate-500">No trends data</div>}
        </div>
        <div>
          {data?.distribution ? <DecisionDistributionChart data={data.distribution} /> : <div className="p-4 text-center text-sm text-slate-500">No distribution data</div>}
        </div>
      </div>

      {/* Product category Breakdown */}
      <div>
        {data?.categories ? <CategoryBreakdownChart data={data.categories} /> : <div className="p-4 text-center text-sm text-slate-500">No categories data</div>}
      </div>
    </div>
  );
};

export default TrendCharts;