"use client";

import { motion } from "framer-motion";
import { AlertTriangle, TrendingUp } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useAlerts, useAlertsSummary } from "@/hooks/useAlertManagement";
import { LiveThreatFeed } from "./components/LiveThreatFeed";
import { ThreatSummaryWidget } from "./components/ThreatSummaryWidget";
import {
  AlertStatsWidget,
  SeverityBreakdown,
} from "./components/AlertStatsWidget";
import {
  TopAttackTypesWidget,
  NetworkActivityWidget,
  TopTargetsWidget,
} from "./components/NetworkStatsWidgets";
import Link from "next/link";
import { Alert } from "@/lib/api/alertsApi";

export default function DashboardPage() {
  const { user } = useAuth();

  // Fetch alerts summary for statistics
  const { data: summary } = useAlertsSummary();

  // Fetch recent active alerts for display
  const { data: recentAlertsData } = useAlerts({
    page: 1,
    size: 5,
    status: "active",
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-400";
      case "high":
        return "bg-orange-400";
      case "medium":
        return "bg-yellow-400";
      case "low":
        return "bg-blue-400";
      default:
        return "bg-gray-400";
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-500/20 text-red-400";
      case "high":
        return "bg-orange-500/20 text-orange-400";
      case "medium":
        return "bg-yellow-500/20 text-yellow-400";
      case "low":
        return "bg-blue-500/20 text-blue-400";
      default:
        return "bg-gray-500/20 text-gray-400";
    }
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const alertTime = new Date(timestamp);
    const diffMs = now.getTime() - alertTime.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) {
      return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`;
    } else if (diffHours > 0) {
      return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
    } else if (diffMins > 0) {
      return `${diffMins} minute${diffMins > 1 ? "s" : ""} ago`;
    } else {
      return "Just now";
    }
  };

  // Calculate total active threats from summary
  const activeThreatCount =
    (summary?.by_status.active || 0) + (summary?.by_status.investigating || 0);

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

      {/* Alert Statistics Widget */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <AlertStatsWidget />
      </motion.div>

      {/* Quick Stats Banner - Only show if there are active threats */}
      {activeThreatCount > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-linear-to-r from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-xl p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-red-500/20 rounded-lg">
                <TrendingUp className="w-6 h-6 text-red-400" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">
                  {activeThreatCount} Active Threats
                </h3>
                <p className="text-gray-400 text-sm">
                  Requires immediate attention
                </p>
              </div>
            </div>
            <Link
              href="/alerts?status=active"
              className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
            >
              View All
            </Link>
          </div>
        </motion.div>
      )}

      {/* Live Threat Monitor Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="space-y-4"
      >
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">Real-Time Monitoring</h2>
          <span className="text-sm text-gray-400">
            Auto-refreshing every 2 seconds
          </span>
        </div>

        {/* Threat Summary Cards */}
        <ThreatSummaryWidget />

        {/* Live Threat Feed and Recent Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LiveThreatFeed />

          {/* Recent Alerts (API Data) */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Recent Alerts</h2>
              <Link
                href="/alerts"
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                View All
              </Link>
            </div>

            <div className="space-y-4">
              {recentAlertsData?.items.length === 0 && (
                <div className="text-center py-8">
                  <AlertTriangle className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400 text-sm">No active alerts</p>
                </div>
              )}

              {recentAlertsData?.items.map((alert: Alert) => (
                <Link
                  key={alert.id}
                  href={`/alerts/${alert.id}`}
                  className="block"
                >
                  <div className="flex items-start space-x-4 p-4 bg-slate-900/50 rounded-lg hover:bg-slate-900 transition-colors cursor-pointer">
                    <div
                      className={`mt-1 w-2 h-2 rounded-full ${getSeverityColor(alert.severity)}`}
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <span
                          className={`text-xs font-semibold px-2 py-1 rounded ${getSeverityBadge(alert.severity)}`}
                        >
                          {alert.severity.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-400">
                          {getTimeAgo(alert.flow_timestamp)}
                        </span>
                      </div>
                      <p className="text-sm text-white font-medium mb-1">
                        {alert.title}
                      </p>
                      <p className="text-xs text-gray-400">
                        Source: {alert.src_ip} → {alert.dst_ip}:{alert.dst_port}
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Network Intelligence - Replace dummy data with real stats */}
      <div className="grid md:grid-cols-2 gap-6">
        <TopAttackTypesWidget />
        <NetworkActivityWidget />
      </div>

      {/* Additional Analytics */}
      <div className="grid md:grid-cols-2 gap-6">
        <SeverityBreakdown />
        <TopTargetsWidget />
      </div>
    </div>
  );
}
