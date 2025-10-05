'use client';

export default function DashboardPage() {
  const stats = [
    { label: 'Active Alerts', value: '24', change: '+12%', trend: 'up', severity: 'critical' },
    { label: 'Network Traffic', value: '2.4 TB', change: '+5%', trend: 'up', severity: 'info' },
    { label: 'Blocked Threats', value: '156', change: '-8%', trend: 'down', severity: 'success' },
    { label: 'System Health', value: '98%', change: '+2%', trend: 'up', severity: 'success' },
  ];

  const recentAlerts = [
    { id: 1, type: 'DDoS Attack', severity: 'critical', source: '192.168.1.45', time: '2 min ago', status: 'active' },
    { id: 2, type: 'Port Scan', severity: 'high', source: '10.0.0.123', time: '15 min ago', status: 'investigating' },
    { id: 3, type: 'Brute Force', severity: 'high', source: '172.16.0.89', time: '32 min ago', status: 'blocked' },
    { id: 4, type: 'SQL Injection', severity: 'medium', source: '192.168.2.100', time: '1 hour ago', status: 'resolved' },
    { id: 5, type: 'Malware Detected', severity: 'critical', source: '10.0.1.56', time: '2 hours ago', status: 'active' },
  ];

  const getSeverityColor = (severity: string) => {
    const colors = {
      critical: 'bg-red-500/10 text-red-400 border-red-500/20',
      high: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      medium: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
      low: 'bg-green-500/10 text-green-400 border-green-500/20',
      info: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    };
    return colors[severity as keyof typeof colors] || colors.info;
  };

  const getStatusColor = (status: string) => {
    const colors = {
      active: 'bg-red-500/10 text-red-400',
      investigating: 'bg-yellow-500/10 text-yellow-400',
      blocked: 'bg-blue-500/10 text-blue-400',
      resolved: 'bg-green-500/10 text-green-400',
    };
    return colors[status as keyof typeof colors] || colors.active;
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Dashboard Overview</h2>
        <p className="text-gray-400">Real-time network security monitoring and threat detection</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div
            key={index}
            className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-400 text-sm font-medium">{stat.label}</span>
              <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${getSeverityColor(stat.severity)}`}>
                {stat.change}
              </span>
            </div>
            <div className="flex items-end justify-between">
              <div>
                <p className="text-3xl font-bold text-white mb-1">{stat.value}</p>
                <p className="text-xs text-gray-500">Last 24 hours</p>
              </div>
              <svg
                className={`w-8 h-8 ${stat.trend === 'up' ? 'text-blue-500' : 'text-emerald-500'}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {stat.trend === 'up' ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                )}
              </svg>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Alerts */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">Recent Alerts</h3>
            <button className="px-4 py-2 text-sm font-medium text-blue-400 hover:text-blue-300 transition-colors">
              View All →
            </button>
          </div>

          <div className="space-y-3">
            {recentAlerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-2 h-2 rounded-full ${
                    alert.severity === 'critical' ? 'bg-red-500' :
                    alert.severity === 'high' ? 'bg-orange-500' :
                    'bg-yellow-500'
                  } animate-pulse`} />
                  <div>
                    <p className="text-white font-medium">{alert.type}</p>
                    <p className="text-sm text-gray-400">Source: {alert.source}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(alert.status)}`}>
                    {alert.status}
                  </span>
                  <span className="text-sm text-gray-500">{alert.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-6">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full p-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all text-left">
              <div className="flex items-center gap-3">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="font-medium">Run Network Scan</span>
              </div>
            </button>

            <button className="w-full p-4 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-colors text-left border border-slate-700">
              <div className="flex items-center gap-3">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span className="font-medium">Generate Report</span>
              </div>
            </button>

            <button className="w-full p-4 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-colors text-left border border-slate-700">
              <div className="flex items-center gap-3">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span className="font-medium">Configure Rules</span>
              </div>
            </button>

            <button className="w-full p-4 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-colors text-left border border-slate-700">
              <div className="flex items-center gap-3">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                <span className="font-medium">Manage Users</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Network Activity Chart Placeholder */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="text-xl font-bold text-white mb-6">Network Activity</h3>
        <div className="h-64 flex items-center justify-center bg-slate-800/50 rounded-lg border border-slate-700">
          <p className="text-gray-500">Chart will be implemented with real data</p>
        </div>
      </div>
    </div>
  );
}
