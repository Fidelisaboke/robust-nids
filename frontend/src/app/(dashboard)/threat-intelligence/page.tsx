'use client';

import { motion } from 'framer-motion';
import { Globe, Shield, AlertTriangle, TrendingUp, MapPin } from 'lucide-react';

export default function ThreatIntelligencePage() {
  const threats = [
    {
      id: 1,
      name: 'Mirai Botnet Variant',
      severity: 'critical',
      category: 'Botnet',
      targets: 'IoT Devices',
      countries: ['CN', 'RU', 'US'],
      confidence: 95,
      trend: 'increasing',
    },
    {
      id: 2,
      name: 'Emotet Campaign',
      severity: 'high',
      category: 'Malware',
      targets: 'Email Systems',
      countries: ['DE', 'FR', 'GB'],
      confidence: 88,
      trend: 'stable',
    },
    {
      id: 3,
      name: 'SQL Injection Attack Pattern',
      severity: 'high',
      category: 'Web Attack',
      targets: 'Web Applications',
      countries: ['BR', 'IN', 'VN'],
      confidence: 92,
      trend: 'increasing',
    },
    {
      id: 4,
      name: 'Ransomware Activity',
      severity: 'critical',
      category: 'Ransomware',
      targets: 'Healthcare, Finance',
      countries: ['RU', 'KP', 'IR'],
      confidence: 97,
      trend: 'increasing',
    },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'high':
        return 'text-orange-400 bg-orange-500/10 border-orange-500/20';
      case 'medium':
        return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
      default:
        return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
    }
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-white">Threat Intelligence</h1>
        <p className="text-gray-400 mt-2">Global threat landscape and emerging security risks</p>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <Globe className="w-8 h-8 text-blue-400" />
            <span className="text-sm text-green-400">↑ 12%</span>
          </div>
          <p className="text-3xl font-bold text-white mb-2">147</p>
          <p className="text-sm text-gray-400">Active Threats</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <Shield className="w-8 h-8 text-purple-400" />
            <span className="text-sm text-red-400">↑ 8%</span>
          </div>
          <p className="text-3xl font-bold text-white mb-2">23</p>
          <p className="text-sm text-gray-400">Critical Alerts</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <MapPin className="w-8 h-8 text-cyan-400" />
            <span className="text-sm text-orange-400">45 countries</span>
          </div>
          <p className="text-3xl font-bold text-white mb-2">892K</p>
          <p className="text-sm text-gray-400">Attack Sources</p>
        </motion.div>
      </div>

      {/* Threat Feed */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <h2 className="text-xl font-bold text-white mb-6">Active Threat Intelligence</h2>

        <div className="space-y-4">
          {threats.map((threat, index) => (
            <motion.div
              key={threat.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              className="bg-slate-900/50 rounded-lg p-5 hover:bg-slate-900 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-white">{threat.name}</h3>
                    <span className={`text-xs font-semibold px-3 py-1 rounded-full ${getSeverityColor(threat.severity)}`}>
                      {threat.severity.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-4 text-sm mb-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-500">Category:</span>
                      <span className="text-gray-300">{threat.category}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-500">Targets:</span>
                      <span className="text-gray-300">{threat.targets}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-500">Confidence:</span>
                      <span className="text-green-400 font-medium">{threat.confidence}%</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center space-x-2">
                      <MapPin className="w-4 h-4 text-gray-500" />
                      <div className="flex space-x-1">
                        {threat.countries.map((country) => (
                          <span key={country} className="text-xs px-2 py-1 bg-slate-800 rounded text-gray-400">
                            {country}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <TrendingUp className={`w-4 h-4 ${threat.trend === 'increasing' ? 'text-red-400' : 'text-gray-400'}`} />
                      <span className={`text-xs ${threat.trend === 'increasing' ? 'text-red-400' : 'text-gray-400'}`}>
                        {threat.trend}
                      </span>
                    </div>
                  </div>
                </div>
                <button className="ml-4 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg transition-colors text-sm">
                  View Details
                </button>
              </div>

              {/* Confidence Bar */}
              <div className="mt-4">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-500">Confidence Score</span>
                  <span className="text-xs text-gray-400">{threat.confidence}%</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-cyan-500"
                    style={{ width: `${threat.confidence}%` }}
                  />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Threat Map Placeholder */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <h2 className="text-xl font-bold text-white mb-4">Global Threat Map</h2>
        <div className="h-96 flex items-center justify-center bg-slate-900/50 rounded-lg">
          <div className="text-center">
            <Globe className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">Interactive threat map visualization</p>
            <p className="text-sm text-gray-500 mt-2">Real-time attack origin tracking</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
