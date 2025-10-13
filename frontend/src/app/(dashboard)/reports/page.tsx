'use client';

import { motion } from 'framer-motion';
import { FileText, Download, Calendar, Clock, Eye, TrendingUp } from 'lucide-react';

export default function ReportsPage() {
  const reports = [
    {
      id: 1,
      title: 'Monthly Security Overview',
      description: 'Comprehensive security analysis for October 2025',
      type: 'Security',
      date: '2025-10-01',
      size: '2.4 MB',
      format: 'PDF',
      status: 'ready',
    },
    {
      id: 2,
      title: 'Incident Response Report',
      description: 'Critical incidents and response actions',
      type: 'Incident',
      date: '2025-10-10',
      size: '1.8 MB',
      format: 'PDF',
      status: 'ready',
    },
    {
      id: 3,
      title: 'Threat Intelligence Summary',
      description: 'Weekly threat landscape analysis',
      type: 'Intelligence',
      date: '2025-10-13',
      size: '3.1 MB',
      format: 'PDF',
      status: 'generating',
    },
    {
      id: 4,
      title: 'Compliance Audit Report',
      description: 'Security compliance and policy adherence',
      type: 'Compliance',
      date: '2025-09-30',
      size: '4.2 MB',
      format: 'PDF',
      status: 'ready',
    },
    {
      id: 5,
      title: 'Network Traffic Analysis',
      description: 'Detailed network traffic patterns and anomalies',
      type: 'Analytics',
      date: '2025-10-12',
      size: '5.6 MB',
      format: 'CSV',
      status: 'ready',
    },
  ];

  const stats = [
    { label: 'Total Reports', value: '127', icon: FileText, color: 'text-blue-400' },
    { label: 'This Month', value: '12', icon: Calendar, color: 'text-purple-400' },
    { label: 'Pending', value: '3', icon: Clock, color: 'text-orange-400' },
    { label: 'Downloads', value: '489', icon: Download, color: 'text-green-400' },
  ];

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'Security':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'Incident':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'Intelligence':
        return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'Compliance':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'Analytics':
        return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-white">Reports & Analytics</h1>
        <p className="text-gray-400 mt-2">Generate and access security reports</p>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <Icon className={`w-8 h-8 ${stat.color}`} />
              </div>
              <p className="text-3xl font-bold text-white mb-2">{stat.value}</p>
              <p className="text-sm text-gray-400">{stat.label}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Generate New Report */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-xl p-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white mb-2">Generate New Report</h2>
            <p className="text-gray-400">Create custom security reports with specific date ranges and filters</p>
          </div>
          <button className="px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all">
            Create Report
          </button>
        </div>
      </motion.div>

      {/* Reports List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <h2 className="text-xl font-bold text-white mb-6">Recent Reports</h2>

        <div className="space-y-4">
          {reports.map((report, index) => (
            <motion.div
              key={report.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 + index * 0.1 }}
              className="bg-slate-900/50 rounded-lg p-5 hover:bg-slate-900 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="p-3 bg-blue-500/10 rounded-lg">
                    <FileText className="w-6 h-6 text-blue-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-white">{report.title}</h3>
                      <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${getTypeColor(report.type)}`}>
                        {report.type}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 mb-3">{report.description}</p>
                    <div className="flex flex-wrap gap-4 text-sm">
                      <div className="flex items-center space-x-2">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        <span className="text-gray-400">{new Date(report.date).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-gray-500">Size:</span>
                        <span className="text-gray-400">{report.size}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-gray-500">Format:</span>
                        <span className="text-gray-400">{report.format}</span>
                      </div>
                      {report.status === 'generating' && (
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 rounded-full bg-orange-400 animate-pulse" />
                          <span className="text-orange-400 text-xs">Generating...</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {report.status === 'ready' && (
                  <div className="flex items-center space-x-2 ml-4">
                    <button className="p-2 text-gray-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors">
                      <Eye className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 rounded-lg transition-colors">
                      <Download className="w-5 h-5" />
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <h2 className="text-xl font-bold text-white mb-6">Report Insights</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Critical Findings</span>
              <span className="text-lg font-semibold text-red-400">23</span>
            </div>
            <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
              <div className="h-full bg-red-500 w-[75%]" />
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Resolved Issues</span>
              <span className="text-lg font-semibold text-green-400">156</span>
            </div>
            <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
              <div className="h-full bg-green-500 w-[85%]" />
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Pending Actions</span>
              <span className="text-lg font-semibold text-yellow-400">42</span>
            </div>
            <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
              <div className="h-full bg-yellow-500 w-[45%]" />
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
