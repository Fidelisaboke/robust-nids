import React from "react";
import { motion } from "framer-motion";
import { Activity, Globe, Shield, Zap } from "lucide-react";
import { useLiveThreats } from "@/hooks/useNids";

/**
 * Top Attack Types Widget
 * Shows the most common attack types from live threat data
 */
export const TopAttackTypesWidget: React.FC = () => {
  const { data: threats } = useLiveThreats();

  // Calculate top attack types
  const attackStats = React.useMemo(() => {
    if (!threats || threats.length === 0) return [];

    const typeCounts = threats.reduce(
      (acc, threat) => {
        const type = threat.multiclass.label;
        acc[type] = (acc[type] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>,
    );

    return Object.entries(typeCounts)
      .map(([type, count]) => ({
        type,
        count,
        percentage: (count / threats.length) * 100,
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
  }, [threats]);

  const getAttackColor = (index: number) => {
    const colors = [
      { from: "from-red-500", to: "to-orange-500" },
      { from: "from-orange-500", to: "to-yellow-500" },
      { from: "from-yellow-500", to: "to-green-500" },
      { from: "from-green-500", to: "to-cyan-500" },
      { from: "from-cyan-500", to: "to-blue-500" },
    ];
    return colors[index] || colors[0];
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.5 }}
      className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
    >
      <div className="flex items-center space-x-3 mb-6">
        <Shield className="w-6 h-6 text-red-400" />
        <h2 className="text-xl font-bold text-white">Top Attack Types</h2>
      </div>

      {attackStats.length === 0 ? (
        <div className="text-center py-8">
          <Shield className="w-12 h-12 text-green-400 mx-auto mb-3" />
          <p className="text-sm text-gray-400">No attacks detected</p>
        </div>
      ) : (
        <div className="space-y-4">
          {attackStats.map((attack, index) => {
            const colors = getAttackColor(index);
            return (
              <div key={attack.type}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-300 font-medium">
                    {attack.type}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-white font-bold">
                      {attack.count}
                    </span>
                    <span className="text-xs text-gray-400">
                      ({attack.percentage.toFixed(0)}%)
                    </span>
                  </div>
                </div>
                <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${attack.percentage}%` }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className={`h-full bg-linear-to-r ${colors.from} ${colors.to}`}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </motion.div>
  );
};

/**
 * Network Activity Widget
 * Shows statistics about network traffic from threat data
 */
export const NetworkActivityWidget: React.FC = () => {
  const { data: threats } = useLiveThreats();

  // Calculate network statistics
  const networkStats = React.useMemo(() => {
    if (!threats || threats.length === 0) {
      return {
        uniqueSources: 0,
        uniqueDestinations: 0,
        totalFlows: 0,
        maliciousRate: 0,
      };
    }

    const sources = new Set(threats.map((t) => t.src_ip));
    const destinations = new Set(threats.map((t) => t.dst_ip));
    const malicious = threats.filter((t) => t.binary.is_malicious).length;

    return {
      uniqueSources: sources.size,
      uniqueDestinations: destinations.size,
      totalFlows: threats.length,
      maliciousRate: (malicious / threats.length) * 100,
    };
  }, [threats]);

  const stats = [
    {
      label: "Unique Sources",
      value: networkStats.uniqueSources,
      icon: Globe,
      color: "text-blue-400",
      bgColor: "bg-blue-500/10",
    },
    {
      label: "Destinations",
      value: networkStats.uniqueDestinations,
      icon: Activity,
      color: "text-purple-400",
      bgColor: "bg-purple-500/10",
    },
    {
      label: "Total Flows",
      value: networkStats.totalFlows,
      icon: Zap,
      color: "text-cyan-400",
      bgColor: "bg-cyan-500/10",
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.5 }}
      className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
    >
      <div className="flex items-center space-x-3 mb-6">
        <Activity className="w-6 h-6 text-blue-400" />
        <h2 className="text-xl font-bold text-white">Network Activity</h2>
      </div>

      <div className="space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-4">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: 0.5 + index * 0.05 }}
                className="text-center"
              >
                <div
                  className={`inline-flex p-3 ${stat.bgColor} rounded-lg mb-2`}
                >
                  <Icon className={`w-5 h-5 ${stat.color}`} />
                </div>
                <p className={`text-2xl font-bold ${stat.color}`}>
                  {stat.value}
                </p>
                <p className="text-xs text-gray-400 mt-1">{stat.label}</p>
              </motion.div>
            );
          })}
        </div>

        {/* Malicious Traffic Rate */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Malicious Traffic</span>
            <span
              className={`text-sm font-medium ${
                networkStats.maliciousRate > 50
                  ? "text-red-400"
                  : networkStats.maliciousRate > 20
                    ? "text-orange-400"
                    : "text-green-400"
              }`}
            >
              {networkStats.maliciousRate.toFixed(1)}%
            </span>
          </div>
          <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${networkStats.maliciousRate}%` }}
              transition={{ duration: 0.5, delay: 0.6 }}
              className={`h-full ${
                networkStats.maliciousRate > 50
                  ? "bg-linear-to-r from-red-500 to-red-600"
                  : networkStats.maliciousRate > 20
                    ? "bg-linear-to-r from-orange-500 to-orange-600"
                    : "bg-linear-to-r from-green-500 to-green-600"
              }`}
            />
          </div>
        </div>

        {/* Detection Confidence */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Avg Confidence</span>
            <span className="text-sm text-white font-medium">
              {threats && threats.length > 0
                ? (
                    (threats.reduce((sum, t) => sum + t.binary.confidence, 0) /
                      threats.length) *
                    100
                  ).toFixed(1)
                : "0"}
              %
            </span>
          </div>
          <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{
                width: `${threats && threats.length > 0 ? (threats.reduce((sum, t) => sum + t.binary.confidence, 0) / threats.length) * 100 : 0}%`,
              }}
              transition={{ duration: 0.5, delay: 0.7 }}
              className="h-full bg-linear-to-r from-blue-500 to-cyan-500"
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

/**
 * Top Targeted IPs Widget
 * Shows the most frequently targeted destination IPs
 */
export const TopTargetsWidget: React.FC = () => {
  const { data: threats } = useLiveThreats();

  const topTargets = React.useMemo(() => {
    if (!threats || threats.length === 0) return [];

    const targetCounts = threats.reduce(
      (acc, threat) => {
        acc[threat.dst_ip] = (acc[threat.dst_ip] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>,
    );

    return Object.entries(targetCounts)
      .map(([ip, count]) => ({ ip, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
  }, [threats]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.6 }}
      className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
    >
      <div className="flex items-center space-x-3 mb-6">
        <Globe className="w-6 h-6 text-orange-400" />
        <h2 className="text-xl font-bold text-white">Most Targeted Assets</h2>
      </div>

      {topTargets.length === 0 ? (
        <div className="text-center py-8">
          <Shield className="w-12 h-12 text-green-400 mx-auto mb-3" />
          <p className="text-sm text-gray-400">No targets detected</p>
        </div>
      ) : (
        <div className="space-y-3">
          {topTargets.map((target, index) => (
            <div
              key={target.ip}
              className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg hover:bg-slate-900 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-8 h-8 bg-orange-500/10 text-orange-400 rounded-lg font-bold text-sm">
                  #{index + 1}
                </div>
                <span className="text-sm text-white font-mono">
                  {target.ip}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-white font-bold">
                  {target.count}
                </span>
                <span className="text-xs text-gray-400">attempts</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
};
