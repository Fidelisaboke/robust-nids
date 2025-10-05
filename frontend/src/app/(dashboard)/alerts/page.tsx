'use client';

import { useState } from 'react';

export default function AlertsPage() {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAlert, setSelectedAlert] = useState<number | null>(null);

  const alerts = [
    {
      id: 1,
      type: 'DDoS Attack',
      severity: 'critical',
      source: '192.168.1.45',
      destination: '10.0.0.1',
      protocol: 'TCP',
      timestamp: '2025-10-05 14:23:45',
      description: 'Massive flood of SYN packets detected from single source',
      status: 'active',
      affectedSystems: 3,
      packets: '1.2M',
      bandwidth: '850 Mbps',
    },
    {
      id: 2,
      type: 'Port Scan',
      severity: 'high',
      source: '10.0.0.123',
      destination: '192.168.1.0/24',
      protocol: 'TCP',
      timestamp: '2025-10-05 14:08:12',
      description: 'Sequential port scanning activity detected across multiple hosts',
      status: 'investigating',
      affectedSystems: 12,
      packets: '45K',
      bandwidth: '12 Mbps',
    },
    {
      id: 3,
      type: 'Brute Force',
      severity: 'high',
      source: '172.16.0.89',
      destination: '192.168.1.10:22',
      protocol: 'SSH',
      timestamp: '2025-10-05 13:51:33',
      description: 'Multiple failed SSH login attempts from external IP',
      status: 'blocked',
      affectedSystems: 1,
      packets: '8.5K',
      bandwidth: '2 Mbps',
    },
    {
      id: 4,
      type: 'SQL Injection',
      severity: 'medium',
      source: '192.168.2.100',
      destination: '10.0.0.5:3306',
      protocol: 'MySQL',
      timestamp: '2025-10-05 13:15:22',
      description: 'Suspicious SQL query patterns detected in web traffic',
      status: 'resolved',
      affectedSystems: 1,
      packets: '234',
      bandwidth: '0.5 Mbps',
    },
    {
      id: 5,
      type: 'Malware Detected',
      severity: 'critical',
      source: '10.0.1.56',
      destination: 'external',
      protocol: 'HTTPS',
      timestamp: '2025-10-05 12:42:18',
      description: 'Known malware signature detected in outbound traffic',
      status: 'active',
      affectedSystems: 1,
      packets: '15K',
      bandwidth: '5 Mbps',
    },
  ];

  const getSeverityColor = (severity: string) => {
    const colors = {
      critical: 'bg-red-500/10 text-red-400 border-red-500/20',
      high: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      medium: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
      low: 'bg-green-500/10 text-green-400 border-green-500/20',
    };
    return colors[severity as keyof typeof colors];
  };

  const getStatusColor = (status: string) => {
    const colors = {
      active: 'bg-red-500/10 text-red-400',
      investigating: 'bg-yellow-500/10 text-yellow-400',
      blocked: 'bg-blue-500/10 text-blue-400',
      resolved: 'bg-green-500/10 text-green-400',
    };
    return colors[status as keyof typeof colors];
  };

  const getStatusIcon = (status: string) => {
    const icons = {
      active: '🔴',
      investigating: '🔍',
      blocked: '🛡️',
      resolved: '✅',
    };
    return icons[status as keyof typeof icons];
  };

  const filteredAlerts = alerts.filter(alert => {
    const matchesFilter = filter === 'all' || alert.severity === filter || alert.status === filter;
    const matchesSearch = searchTerm === '' ||
      alert.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.source.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.destination.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const selectedAlertData = alerts.find(a => a.id === selectedAlert);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Security Alerts</h2>
          <p className="text-gray-400">Monitor and respond to detected threats in real-time</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 bg-slate-800 text-white font-medium rounded-lg hover:bg-slate-700 transition-colors border border-slate-700">
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              Filters
            </span>
          </button>
          <button className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all">
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export Alerts
            </span>
          </button>
        </div>
      </div>

      {/* Alert Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Active', count: 2, color: 'red', icon: '🔴' },
          { label: 'Investigating', count: 1, color: 'yellow', icon: '🔍' },
          { label: 'Blocked', count: 1, color: 'blue', icon: '🛡️' },
          { label: 'Resolved', count: 1, color: 'green', icon: '✅' },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-slate-900 border border-slate-800 rounded-lg p-4 hover:border-slate-700 transition-colors cursor-pointer"
            onClick={() => setFilter(stat.label.toLowerCase())}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{stat.icon}</span>
                <span className="text-gray-400 text-sm font-medium">{stat.label}</span>
              </div>
              <div className={`w-3 h-3 rounded-full bg-${stat.color}-500 animate-pulse`} />
            </div>
            <p className="text-3xl font-bold text-white mt-2">{stat.count}</p>
          </div>
        ))}
      </div>

      {/* Filters and Search */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <input
                type="search"
                placeholder="Search alerts by type, source, or destination..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2.5 pl-10 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <svg
                className="absolute left-3 top-3 w-5 h-5 text-gray-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          <div className="flex gap-2 flex-wrap">
            {['all', 'critical', 'high', 'medium', 'low'].map((level) => (
              <button
                key={level}
                onClick={() => setFilter(level)}
                className={`px-4 py-2.5 rounded-lg font-medium text-sm transition-all ${
                  filter === level
                    ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30'
                    : 'bg-slate-800 text-gray-400 hover:text-white hover:bg-slate-700 border border-slate-700'
                }`}
              >
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-800/50 border-b border-slate-700">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  <input type="checkbox" className="w-4 h-4 rounded border-gray-600 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-900 bg-slate-800" />
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Alert
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Severity
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Source
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Destination
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {filteredAlerts.map((alert) => (
                <tr
                  key={alert.id}
                  className="hover:bg-slate-800/50 transition-colors cursor-pointer"
                  onClick={() => setSelectedAlert(alert.id)}
                >
                  <td className="px-6 py-4">
                    <input
                      type="checkbox"
                      className="w-4 h-4 rounded border-gray-600 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-900 bg-slate-800"
                      onClick={(e) => e.stopPropagation()}
                    />
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${
                        alert.severity === 'critical' ? 'bg-red-500' :
                        alert.severity === 'high' ? 'bg-orange-500' :
                        'bg-yellow-500'
                      } animate-pulse`} />
                      <div>
                        <p className="text-white font-medium">{alert.type}</p>
                        <p className="text-sm text-gray-400 mt-1">{alert.description}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border inline-block ${getSeverityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <code className="text-sm text-cyan-400 bg-slate-800 px-2 py-1 rounded font-mono">
                      {alert.source}
                    </code>
                  </td>
                  <td className="px-6 py-4">
                    <code className="text-sm text-cyan-400 bg-slate-800 px-2 py-1 rounded font-mono">
                      {alert.destination}
                    </code>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium inline-flex items-center gap-1.5 ${getStatusColor(alert.status)}`}>
                      <span>{getStatusIcon(alert.status)}</span>
                      {alert.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-400">
                      <p>{alert.timestamp.split(' ')[0]}</p>
                      <p className="text-xs text-gray-500">{alert.timestamp.split(' ')[1]}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        className="p-2 text-blue-400 hover:text-blue-300 hover:bg-slate-800 rounded-lg transition-colors"
                        title="View Details"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedAlert(alert.id);
                        }}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </button>
                      <button
                        className="p-2 text-green-400 hover:text-green-300 hover:bg-slate-800 rounded-lg transition-colors"
                        title="Acknowledge"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </button>
                      <button
                        className="p-2 text-gray-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                        title="More Options"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="bg-slate-800/50 px-6 py-4 flex items-center justify-between border-t border-slate-700">
          <div className="flex items-center gap-4">
            <p className="text-sm text-gray-400">
              Showing <span className="font-medium text-white">1</span> to{' '}
              <span className="font-medium text-white">{filteredAlerts.length}</span> of{' '}
              <span className="font-medium text-white">{filteredAlerts.length}</span> alerts
            </p>
            <select className="px-3 py-1 bg-slate-800 border border-slate-700 rounded text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>10 per page</option>
              <option>25 per page</option>
              <option>50 per page</option>
              <option>100 per page</option>
            </select>
          </div>
          <div className="flex gap-2">
            <button className="px-3 py-1.5 bg-slate-800 text-gray-400 rounded-lg hover:bg-slate-700 hover:text-white transition-colors text-sm border border-slate-700 disabled:opacity-50 disabled:cursor-not-allowed">
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Previous
              </span>
            </button>
            <button className="px-3 py-1.5 bg-blue-500 text-white rounded-lg font-medium text-sm">1</button>
            <button className="px-3 py-1.5 bg-slate-800 text-gray-400 rounded-lg hover:bg-slate-700 hover:text-white transition-colors text-sm border border-slate-700">2</button>
            <button className="px-3 py-1.5 bg-slate-800 text-gray-400 rounded-lg hover:bg-slate-700 hover:text-white transition-colors text-sm border border-slate-700">3</button>
            <span className="px-3 py-1.5 text-gray-500">...</span>
            <button className="px-3 py-1.5 bg-slate-800 text-gray-400 rounded-lg hover:bg-slate-700 hover:text-white transition-colors text-sm border border-slate-700">10</button>
            <button className="px-3 py-1.5 bg-slate-800 text-gray-400 rounded-lg hover:bg-slate-700 hover:text-white transition-colors text-sm border border-slate-700">
              <span className="flex items-center gap-1">
                Next
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Alert Detail Modal */}
      {selectedAlert && selectedAlertData && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-slate-900 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`w-3 h-3 rounded-full ${
                  selectedAlertData.severity === 'critical' ? 'bg-red-500' :
                  selectedAlertData.severity === 'high' ? 'bg-orange-500' :
                  'bg-yellow-500'
                } animate-pulse`} />
                <div>
                  <h3 className="text-xl font-bold text-white">{selectedAlertData.type}</h3>
                  <p className="text-sm text-gray-400">Alert ID: #{selectedAlertData.id}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedAlert(null)}
                className="p-2 text-gray-400 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Status and Severity */}
              <div className="flex items-center gap-3">
                <span className={`px-4 py-2 rounded-lg text-sm font-medium border ${getSeverityColor(selectedAlertData.severity)}`}>
                  {selectedAlertData.severity.toUpperCase()}
                </span>
                <span className={`px-4 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-2 ${getStatusColor(selectedAlertData.status)}`}>
                  <span>{getStatusIcon(selectedAlertData.status)}</span>
                  {selectedAlertData.status.toUpperCase()}
                </span>
              </div>

              {/* Description */}
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                <p className="text-white">{selectedAlertData.description}</p>
              </div>

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400 mb-1">Source IP</p>
                  <code className="text-lg text-cyan-400 font-mono">{selectedAlertData.source}</code>
                </div>
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400 mb-1">Destination</p>
                  <code className="text-lg text-cyan-400 font-mono">{selectedAlertData.destination}</code>
                </div>
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400 mb-1">Protocol</p>
                  <p className="text-lg text-white font-medium">{selectedAlertData.protocol}</p>
                </div>
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                  <p className="text-sm text-gray-400 mb-1">Timestamp</p>
                  <p className="text-lg text-white font-medium">{selectedAlertData.timestamp}</p>
                </div>
              </div>

              {/* Impact Metrics */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-center">
                  <p className="text-sm text-gray-400 mb-1">Affected Systems</p>
                  <p className="text-2xl font-bold text-white">{selectedAlertData.affectedSystems}</p>
                </div>
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-center">
                  <p className="text-sm text-gray-400 mb-1">Packets</p>
                  <p className="text-2xl font-bold text-orange-400">{selectedAlertData.packets}</p>
                </div>
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-center">
                  <p className="text-sm text-gray-400 mb-1">Bandwidth</p>
                  <p className="text-2xl font-bold text-red-400">{selectedAlertData.bandwidth}</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-slate-800">
                <button className="flex-1 px-4 py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 transition-colors">
                  Acknowledge Alert
                </button>
                <button className="flex-1 px-4 py-3 bg-slate-800 text-white font-medium rounded-lg hover:bg-slate-700 transition-colors border border-slate-700">
                  Block Source IP
                </button>
                <button className="flex-1 px-4 py-3 bg-red-500/10 text-red-400 font-medium rounded-lg hover:bg-red-500/20 transition-colors border border-red-500/20">
                  Escalate Incident
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
