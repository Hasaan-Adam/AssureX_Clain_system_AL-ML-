import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Doughnut, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const isDark = () => document.documentElement.classList.contains('dark');
const gridColor   = () => isDark() ? 'rgba(100,116,139,0.2)' : 'rgba(226,232,240,0.5)';
const tickColor   = () => isDark() ? '#94a3b8' : '#64748b';
const legendColor = () => isDark() ? '#cbd5e1' : '#475569';

export const ClaimTrendsChart = ({ data = null }) => {
  const chartData = data || {
    labels: ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr'],
    datasets: [
      {
        label: 'Auto Approved',
        data: [65, 78, 90, 85, 95, 110, 125, 140, 130, 145, 160, 180],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Manual Review',
        data: [15, 20, 18, 22, 19, 25, 28, 30, 24, 28, 22, 26],
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.05)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Rejected',
        data: [12, 14, 11, 15, 10, 13, 16, 18, 14, 15, 12, 14],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.05)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          boxWidth: 8,
          font: { size: 11, family: 'Inter' },
          color: legendColor(),
        },
      },
      tooltip: {
        backgroundColor: isDark() ? '#1e293b' : '#0f172a',
        padding: 10,
        cornerRadius: 8,
        titleFont: { size: 12, family: 'Inter', weight: 'bold' },
        bodyFont: { size: 11, family: 'Inter' },
      },
    },
    scales: {
      y: {
        grid: { color: gridColor() },
        ticks: { font: { size: 10 }, color: tickColor() },
      },
      x: {
        grid: { display: false },
        ticks: { font: { size: 10 }, color: tickColor() },
      },
    },
  };

  return (
    <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
      <div>
        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
          Claim Volume & Adjudication Trends
        </h3>
        <p className="text-xs text-slate-500">Monthly throughput by adjudication result</p>
      </div>
      <div className="h-64 w-full">
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
};

export const DecisionDistributionChart = ({ data = null }) => {
  const chartData = data || {
    labels: ['Auto-Approved', 'Manual Review', 'Auto-Rejected', 'Escalated'],
    datasets: [
      {
        data: [68, 18, 10, 4],
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#a855f7'],
        borderWidth: 0,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '70%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          boxWidth: 8,
          font: { size: 11, family: 'Inter' },
        },
      },
    },
  };

  return (
    <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
      <div>
        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
          Decision Distribution
        </h3>
        <p className="text-xs text-slate-500">Ensemble outcome breakdown</p>
      </div>
      <div className="h-64 w-full flex items-center justify-center">
        <Doughnut data={chartData} options={options} />
      </div>
    </div>
  );
};

export const CategoryBreakdownChart = ({ data = null }) => {
  const chartData = data || {
    labels: ['Smartphones', 'OLED TVs', 'Laptops', 'Refrigerators', 'Washing Machines', 'Audio Systems'],
    datasets: [
      {
        label: 'Claim Frequency',
        data: [340, 290, 210, 185, 140, 95],
        backgroundColor: '#6366f1',
        borderRadius: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0f172a',
        padding: 10,
        cornerRadius: 8,
      },
    },
    scales: {
      y: {
        grid: { color: gridColor() },
        ticks: { font: { size: 10 }, color: tickColor() },
      },
      x: {
        grid: { display: false },
        ticks: { font: { size: 10 }, color: tickColor() },
      },
    },
  };

  return (
    <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
      <div>
        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
          Claims by Product Category
        </h3>
        <p className="text-xs text-slate-500">Most frequent defect incidence</p>
      </div>
      <div className="h-64 w-full">
        <Bar data={chartData} options={options} />
      </div>
    </div>
  );
};