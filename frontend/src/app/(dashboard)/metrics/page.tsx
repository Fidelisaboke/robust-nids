'use client';

import { useState } from 'react';

export default function MetricsPage() {
  const [timeRange, setTimeRange] = useState('24h');

  const networkStats = [
    { label: 'Total Traffic', value: '2.4 TB', change: '+12%', trend: 'up' },
    { label: 'Avg Throughput', value: '850 Mbps', change: '+5%', trend: 'up' },
    { label: 'Active Connections', value: '1,234', change: '-3%', trend: 'down' },
    { label: 'Packet Loss', value: '0.02%', change: '-0.01%', trend: 'down' },
  ];

  const mlMetrics = [
    { label: 'Model Accuracy', value: '98.5%', color: 'green' },
    { label: 'Detection Rate', value: '97.2%', color: 'green' },
    { label: 'False Positive Rate', value: '1.3%', color: 'yellow' },
    { label: 'Processing Time', value: '12ms', color: 'blue' },
  ];

  const topThreats = [
    { type: 'DDoS Attacks', count: 45, percentage: 35 },
    { type: 'Port Scans', count: 32, percentage: 25 },
    { type: 'Brute Force', count: 28, percentage: 22 },
    { type: 'SQL Injection', count: 15, percentage: 12 },
    { type: 'Others', count: 8, percentage: 6 },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Network Metrics</h2>
          <p className="text-gray-400">Detailed network and system performance analytics</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <button className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all">
            Export Report
          </button>
        </div>
      </div>

      {/* Network Statistics */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">Network Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {networkStats.map((stat, idx) => (
            <div
              key={idx}
              className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-gray-400 text-sm font-medium">{stat.label}</span>
                <span className={`text-xs font-medium ${
                  stat.trend === 'up' ? 'text-green-400' : 'text-red-400'
                }`}>
                  {stat.change}
                </span>
              </div>
              <p className="text-3xl font-bold text-white">{stat.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ML Model Performance */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">ML Model Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {mlMetrics.map((metric, idx) => (
            <div
              key={idx}
              className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-colors"
            >
              <p className="text-gray-400 text-sm font-medium mb-3">{metric.label}</p>
              <div className="flex items-end justify-between">
                <p className="text-3xl font-bold text-white">{metric.value}</p>
                <div className={`w-3 h-3 rounded-full bg-${metric.color}-500 animate-pulse`} />
              </div>
              <div className="mt-4 h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full bg-${metric.color}-500 transition-all duration-500`}
                  style={{ width: metric.value }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Traffic Overview Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Traffic Overview</h3>
          <div className="h-64 flex items-center justify-center bg-slate-800/50 rounded-lg border border-slate-700">
            <p className="text-gray-500">Line chart - Traffic over time</p>
          </div>
          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="text-center">
              <p className="text-sm text-gray-400 mb-1">Inbound</p>
              <p className="text-xl font-bold text-blue-400">1.2 TB</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-400 mb-1">Outbound</p>
              <p className="text-xl font-bold text-cyan-400">1.2 TB</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-400 mb-1">Internal</p>
              <p className="text-xl font-bold text-purple-400">450 GB</p>
            </div>
          </div>
        </div>

        {/* Top Threats */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Top Threat Types</h3>
          <div className="space-y-4">
            {topThreats.map((threat, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-medium">{threat.type}</span>
                  <span className="text-gray-400 text-sm">{threat.count} incidents</span>
                </div>
                <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-red-500 to-orange-500 transition-all duration-500"
                    style={{ width: `${threat.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Protocol Distribution */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Protocol Distribution</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[
            { protocol: 'HTTP/HTTPS', percentage: 45, color: 'blue' },
            { protocol: 'SSH', percentage: 20, color: 'green' },
            { protocol: 'DNS', percentage: 15, color: 'purple' },
            { protocol: 'FTP', percentage: 8, color: 'yellow' },
            { protocol: 'SMTP', percentage: 7, color: 'orange' },
            { protocol: 'Others', percentage: 5, color: 'gray' },
          ].map((item, idx) => (
            <div
              key={idx}
              className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-center hover:border-slate-600 transition-colors"
            >
              <p className="text-sm text-gray-400 mb-2">{item.protocol}</p>
              <p className={`text-2xl font-bold text-${item.color}-400`}>{item.percentage}%</p>
            </div>
          ))}
        </div>
      </div>

      {/* System Health */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">System Health</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { label: 'CPU Usage', value: 45, max: 100, unit: '%', color: 'blue' },
            { label: 'Memory Usage', value: 6.2, max: 16, unit: 'GB', color: 'green' },
            { label: 'Disk Usage', value: 234, max: 500, unit: 'GB', color: 'purple' },
          ].map((resource, idx) => (
            <div key={idx} className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-white font-medium">{resource.label}</span>
                <span className="text-gray-400 text-sm">
                  {resource.value}{resource.unit} / {resource.max}{resource.unit}
                </span>
              </div>
              <div className="h-4 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full bg-gradient-to-r from-${resource.color}-500 to-${resource.color}-600 transition-all duration-500`}
                  style={{ width: `${(resource.value / resource.max) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
