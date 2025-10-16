"use client";

import { motion } from "framer-motion";
import {
  Activity,
  TrendingUp,
  TrendingDown,
  Zap,
  Database,
  Network as NetworkIcon,
} from "lucide-react";

export default function MetricsPage() {
  const metrics = [
    {
      label: "Packets Analyzed",
      value: "1.2M",
      change: "+15%",
      trend: "up",
      icon: Activity,
    },
    {
      label: "Bandwidth Usage",
      value: "2.4 GB/s",
      change: "+8%",
      trend: "up",
      icon: Zap,
    },
    {
      label: "Active Connections",
      value: "8,452",
      change: "-3%",
      trend: "down",
      icon: NetworkIcon,
    },
    {
      label: "Database Queries",
      value: "45K/min",
      change: "+22%",
      trend: "up",
      icon: Database,
    },
  ];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-white">System Metrics</h1>
        <p className="text-gray-400 mt-2">
          Real-time performance and network statistics
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          const TrendIcon = metric.trend === "up" ? TrendingUp : TrendingDown;
          return (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <Icon className="w-8 h-8 text-blue-400" />
                <span
                  className={`flex items-center text-sm ${metric.trend === "up" ? "text-green-400" : "text-red-400"}`}
                >
                  <TrendIcon className="w-4 h-4 mr-1" />
                  {metric.change}
                </span>
              </div>
              <p className="text-3xl font-bold text-white mb-2">
                {metric.value}
              </p>
              <p className="text-sm text-gray-400">{metric.label}</p>
            </motion.div>
          );
        })}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <h2 className="text-xl font-bold text-white mb-6">
          Network Traffic (Last 24 Hours)
        </h2>
        <div className="h-64 flex items-end justify-between space-x-2">
          {Array.from({ length: 24 }).map((_, i) => {
            const height = Math.random() * 100;
            return (
              <div
                key={i}
                className="flex-1 bg-gradient-to-t from-blue-500 to-cyan-500 rounded-t opacity-70 hover:opacity-100 transition-opacity"
                style={{ height: `${height}%` }}
              />
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}
