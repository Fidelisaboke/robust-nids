"use client";

import { motion } from "framer-motion";
import { Users, Server } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { LiveThreatFeed } from "./components/LiveThreatFeed";
import { ThreatSummaryWidget } from "./components/ThreatSummaryWidget";

export default function DashboardPage() {
  const { user } = useAuth();

  const recentAlerts = [
    {
      id: 1,
      type: "Critical",
      message: "Potential SQL Injection Attempt Detected",
      time: "2 minutes ago",
      source: "192.168.1.45",
    },
    {
      id: 2,
      type: "High",
      message: "Unusual Port Scan Activity",
      time: "15 minutes ago",
      source: "10.0.0.23",
    },
    {
      id: 3,
      type: "Medium",
      message: "Failed Authentication Attempts",
      time: "1 hour ago",
      source: "172.16.0.8",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold text-white">
          Welcome back, {user?.first_name || "User"}!
        </h1>
        <p className="text-gray-400 mt-2">
          Here&apos;s what&apos;s happening with your network security today.
        </p>
      </motion.div>

      {/* Live Threat Monitor Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="space-y-4"
      >
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">Real-Time Threats</h2>
          <span className="text-sm text-gray-400">
            Auto-refreshing every 2 seconds
          </span>
        </div>

        {/* Threat Summary Cards */}
        <ThreatSummaryWidget />

        {/* Live Threat Feed */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LiveThreatFeed />

          {/* Recent Alerts (Static Data) */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Recent Alerts</h2>
              <button className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
                View All
              </button>
            </div>

            <div className="space-y-4">
              {recentAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-start space-x-4 p-4 bg-slate-900/50 rounded-lg hover:bg-slate-900 transition-colors"
                >
                  <div
                    className={`mt-1 w-2 h-2 rounded-full ${
                      alert.type === "Critical"
                        ? "bg-red-400"
                        : alert.type === "High"
                          ? "bg-orange-400"
                          : "bg-yellow-400"
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <span
                        className={`text-xs font-semibold px-2 py-1 rounded ${
                          alert.type === "Critical"
                            ? "bg-red-500/20 text-red-400"
                            : alert.type === "High"
                              ? "bg-orange-500/20 text-orange-400"
                              : "bg-yellow-500/20 text-yellow-400"
                        }`}
                      >
                        {alert.type}
                      </span>
                      <span className="text-xs text-gray-400">
                        {alert.time}
                      </span>
                    </div>
                    <p className="text-sm text-white font-medium mb-1">
                      {alert.message}
                    </p>
                    <p className="text-xs text-gray-400">
                      Source: {alert.source}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* System Status */}
      <div className="grid md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center space-x-3 mb-6">
            <Server className="w-6 h-6 text-blue-400" />
            <h2 className="text-xl font-bold text-white">System Health</h2>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">CPU Usage</span>
                <span className="text-sm text-white font-medium">45%</span>
              </div>
              <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 w-[45%]" />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Memory Usage</span>
                <span className="text-sm text-white font-medium">62%</span>
              </div>
              <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-green-500 to-emerald-500 w-[62%]" />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Network Load</span>
                <span className="text-sm text-white font-medium">38%</span>
              </div>
              <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500 w-[38%]" />
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center space-x-3 mb-6">
            <Users className="w-6 h-6 text-purple-400" />
            <h2 className="text-xl font-bold text-white">Active Sessions</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
              <div>
                <p className="text-sm text-white font-medium">Administrator</p>
                <p className="text-xs text-gray-400">Desktop - Chrome</p>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-green-400" />
                <span className="text-xs text-green-400">Active</span>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
              <div>
                <p className="text-sm text-white font-medium">
                  Security Analyst
                </p>
                <p className="text-xs text-gray-400">Mobile - Safari</p>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-green-400" />
                <span className="text-xs text-green-400">Active</span>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
              <div>
                <p className="text-sm text-white font-medium">
                  Network Monitor
                </p>
                <p className="text-xs text-gray-400">Tablet - Firefox</p>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-gray-400" />
                <span className="text-xs text-gray-400">Idle</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
