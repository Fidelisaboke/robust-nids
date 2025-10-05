'use client';

import { useState } from 'react';

export default function ReportsPage() {
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  const reports = [
    {
      id: 1,
      title: 'Daily Security Summary',
      type: 'daily',
      status: 'ready',
      createdBy: 'System',
      createdAt: '2025-10-05 08:00:00',
      period: '2025-10-04',
      format: 'PDF',
      size: '2.4 MB',
    },
    {
      id: 2,
      title: 'Weekly Threat Analysis',
      type: 'weekly',
      status: 'ready',
      createdBy: 'Admin User',
      createdAt: '2025-10-01 09:30:00',
      period: 'Sep 24 - Oct 01',
      format: 'PDF',
      size: '5.8 MB',
    },
    {
      id: 3,
      title: 'Monthly Compliance Report',
      type: 'monthly',
      status: 'generating',
      createdBy: 'Admin User',
      createdAt: '2025-10-05 14:00:00',
      period: 'September 2025',
      format: 'PDF',
      size: '-',
    },
    {
      id: 4,
      title: 'Incident Response Report',
      type: 'incident',
      status: 'ready',
      createdBy: 'Security Team',
      createdAt: '2025-10-03 16:45:00',
      period: 'Oct 02 Incident',
      format: 'PDF',
      size: '1.2 MB',
    },
  ];

  const getStatusColor = (status: string) => {
    const colors = {
      ready: 'bg-green-500/10 text-green-400 border-green-500/20',
      generating: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
      failed: 'bg-red-500/10 text-red-400 border-red-500/20',
    };
    return colors[status as keyof typeof colors];
  };

  const getTypeColor = (type: string) => {
    const colors = {
      daily: 'bg-blue-500/10 text-blue-400',
      weekly: 'bg-purple-500/10 text-purple-400',
      monthly: 'bg-cyan-500/10 text-cyan-400',
      incident: 'bg-orange-500/10 text-orange-400',
      compliance: 'bg-green-500/10 text-green-400',
    };
    return colors[type as keyof typeof colors];
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Security Reports</h2>
          <p className="text-gray-400">Generate and manage security analysis reports</p>
        </div>
        <button
          onClick={() => setShowGenerateModal(true)}
          className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Generate Report
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Reports', value: '48', icon: '📄' },
          { label: 'This Month', value: '12', icon: '📅' },
          { label: 'Ready', value: '45', icon: '✅' },
          { label: 'Generating', value: '3', icon: '⏳' },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-slate-900 border border-slate-800 rounded-lg p-4 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">{stat.icon}</span>
              <span className="text-gray-400 text-sm">{stat.label}</span>
            </div>
            <p className="text-2xl font-bold text-white">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="search"
              placeholder="Search reports..."
              className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select className="px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option>All Types</option>
            <option>Daily</option>
            <option>Weekly</option>
            <option>Monthly</option>
            <option>Incident</option>
            <option>Compliance</option>
          </select>
          <select className="px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option>All Status</option>
            <option>Ready</option>
            <option>Generating</option>
            <option>Failed</option>
          </select>
        </div>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {reports.map((report) => (
          <div
            key={report.id}
            className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white mb-2">{report.title}</h3>
                <div className="flex items-center gap-2 mb-3">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getTypeColor(report.type)}`}>
                    {report.type}
                  </span>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${getStatusColor(report.status)}`}>
                    {report.status}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {report.status === 'ready' && (
                  <>
                    <button className="p-2 text-blue-400 hover:text-blue-300 hover:bg-slate-800 rounded-lg transition-colors">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button className="p-2 text-green-400 hover:text-green-300 hover:bg-slate-800 rounded-lg transition-colors">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                    </button>
                  </>
                )}
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Period:</span>
                <span className="text-white">{report.period}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Created by:</span>
                <span className="text-white">{report.createdBy}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Created:</span>
                <span className="text-white">{report.createdAt}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Format:</span>
                <span className="text-white">{report.format}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Size:</span>
                <span className="text-white">{report.size}</span>
              </div>
            </div>

            {report.status === 'generating' && (
              <div className="mt-4">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-gray-400">Generating...</span>
                  <span className="text-yellow-400">45%</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-yellow-500 to-orange-500 transition-all duration-300" style={{ width: '45%' }} />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Generate Report Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Generate New Report</h3>
              <button
                onClick={() => setShowGenerateModal(false)}
                className="p-2 text-gray-400 hover:text-white transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Report Title
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Custom Security Report"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Report Type
                </label>
                <select className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option>Daily Summary</option>
                  <option>Weekly Analysis</option>
                  <option>Monthly Report</option>
                  <option>Incident Report</option>
                  <option>Compliance Report</option>
                  <option>Custom Report</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Format
                </label>
                <select className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option>PDF</option>
                  <option>CSV</option>
                  <option>JSON</option>
                  <option>HTML</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Include Sections
                </label>
                <div className="space-y-2">
                  {[
                    'Executive Summary',
                    'Alert Statistics',
                    'Threat Analysis',
                    'Network Metrics',
                    'Incident Timeline',
                    'Recommendations',
                  ].map((section) => (
                    <label key={section} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="w-4 h-4 rounded border-gray-600 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-900 bg-slate-800"
                      />
                      <span className="text-sm text-gray-400">{section}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowGenerateModal(false)}
                  className="flex-1 px-4 py-2.5 bg-slate-800 text-white font-medium rounded-lg hover:bg-slate-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2.5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all"
                >
                  Generate Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
