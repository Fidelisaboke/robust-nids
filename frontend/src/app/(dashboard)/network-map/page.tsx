"use client";

import { motion } from "framer-motion";
import { Globe, MapPin, TrendingUp, Shield } from "lucide-react";
import { useLiveThreats } from "@/hooks/useNids";
import { Badge } from "@/components/ui/badge";

export default function NetworkMapPage() {
  const { data: threats } = useLiveThreats();

  // Group threats by source IP
  const topSources = threats
    ? Object.entries(
        threats.reduce(
          (acc, threat) => {
            acc[threat.src_ip] = (acc[threat.src_ip] || 0) + 1;
            return acc;
          },
          {} as Record<string, number>,
        ),
      )
        .map(([ip, count]) => ({ ip, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10)
    : [];

  // Group by attack type
  const attackTypes = threats
    ? Object.entries(
        threats.reduce(
          (acc, threat) => {
            acc[threat.multiclass.label] =
              (acc[threat.multiclass.label] || 0) + 1;
            return acc;
          },
          {} as Record<string, number>,
        ),
      )
        .map(([type, count]) => ({ type, count }))
        .sort((a, b) => b.count - a.count)
    : [];

  // Most targeted destinations
  const topTargets = threats
    ? Object.entries(
        threats.reduce(
          (acc, threat) => {
            acc[threat.dst_ip] = (acc[threat.dst_ip] || 0) + 1;
            return acc;
          },
          {} as Record<string, number>,
        ),
      )
        .map(([ip, count]) => ({ ip, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10)
    : [];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-white">Network Map</h1>
        <p className="text-gray-400 mt-2">
          Real-time view of attack sources and targets across your network
        </p>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-red-500/10 rounded-lg">
              <Globe className="w-6 h-6 text-red-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Unique Sources</p>
              <p className="text-2xl font-bold text-white">
                {new Set(threats?.map((t) => t.src_ip)).size || 0}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-orange-500/10 rounded-lg">
              <MapPin className="w-6 h-6 text-orange-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Attack Vectors</p>
              <p className="text-2xl font-bold text-white">
                {attackTypes.length}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-purple-500/10 rounded-lg">
              <Shield className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Targeted Assets</p>
              <p className="text-2xl font-bold text-white">
                {new Set(threats?.map((t) => t.dst_ip)).size || 0}
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Attack Sources */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center space-x-3 mb-6">
            <Globe className="w-6 h-6 text-red-400" />
            <h2 className="text-xl font-bold text-white">Top Attack Sources</h2>
          </div>

          {topSources.length === 0 ? (
            <div className="text-center py-12">
              <Shield className="w-16 h-16 text-green-400 mx-auto mb-3" />
              <p className="text-gray-400">No threats detected</p>
            </div>
          ) : (
            <div className="space-y-3">
              {topSources.map((source, index) => (
                <motion.div
                  key={source.ip}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + index * 0.05 }}
                  className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg hover:bg-slate-900 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`flex items-center justify-center w-8 h-8 rounded-lg font-bold text-sm ${
                        index === 0
                          ? "bg-red-500/20 text-red-400"
                          : index === 1
                            ? "bg-orange-500/20 text-orange-400"
                            : index === 2
                              ? "bg-yellow-500/20 text-yellow-400"
                              : "bg-slate-700 text-gray-400"
                      }`}
                    >
                      #{index + 1}
                    </div>
                    <span className="text-sm font-mono text-white">
                      {source.ip}
                    </span>
                  </div>
                  <Badge className="bg-red-500/20 text-red-400 border-red-500/50">
                    {source.count} attacks
                  </Badge>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Top Targeted Assets */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center space-x-3 mb-6">
            <MapPin className="w-6 h-6 text-purple-400" />
            <h2 className="text-xl font-bold text-white">
              Most Targeted Assets
            </h2>
          </div>

          {topTargets.length === 0 ? (
            <div className="text-center py-12">
              <Shield className="w-16 h-16 text-green-400 mx-auto mb-3" />
              <p className="text-gray-400">No targets detected</p>
            </div>
          ) : (
            <div className="space-y-3">
              {topTargets.map((target, index) => (
                <motion.div
                  key={target.ip}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + index * 0.05 }}
                  className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg hover:bg-slate-900 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`flex items-center justify-center w-8 h-8 rounded-lg font-bold text-sm ${
                        index === 0
                          ? "bg-purple-500/20 text-purple-400"
                          : index === 1
                            ? "bg-blue-500/20 text-blue-400"
                            : index === 2
                              ? "bg-cyan-500/20 text-cyan-400"
                              : "bg-slate-700 text-gray-400"
                      }`}
                    >
                      #{index + 1}
                    </div>
                    <span className="text-sm font-mono text-white">
                      {target.ip}
                    </span>
                  </div>
                  <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/50">
                    {target.count} attempts
                  </Badge>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>

      {/* Attack Types Distribution */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <TrendingUp className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-bold text-white">
            Attack Type Distribution
          </h2>
        </div>

        {attackTypes.length === 0 ? (
          <div className="text-center py-12">
            <Shield className="w-16 h-16 text-green-400 mx-auto mb-3" />
            <p className="text-gray-400">No attack data available</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {attackTypes.map((attack, index) => (
              <motion.div
                key={attack.type}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.7 + index * 0.05 }}
                className="bg-slate-900/50 rounded-lg p-4 text-center hover:bg-slate-900 transition-colors"
              >
                <p className="text-3xl font-bold text-blue-400 mb-2">
                  {attack.count}
                </p>
                <p className="text-sm text-gray-400">{attack.type}</p>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}
