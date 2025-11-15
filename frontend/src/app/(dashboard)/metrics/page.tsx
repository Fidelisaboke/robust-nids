"use client";

import { motion } from "framer-motion";
import {
  Activity,
  TrendingUp,
  TrendingDown,
  Loader2,
  AlertTriangle,
  ShieldCheck,
} from "lucide-react";
import { useAlertsSummary } from "@/hooks/useAlertManagement";
import { useAdversarialReport } from "@/hooks/useNids";
import { useMemo } from "react";
import { AlertsTimeChart } from "./components/AlertsTimeChart";
import { AdversarialReportChart } from "./components/AdversarialReportChart";

// Types for metrics and summary
interface Metric {
  label: string;
  value: string;
  change: string;
  trend: "up" | "down";
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

interface TimeSeriesData {
  timestamp: string;
  count: number;
}

interface CategoryData {
  category: string;
  count: number;
}

export default function MetricsPage() {
  const { data: summary, isLoading } = useAlertsSummary();
  const { data: adReport, isLoading: isReportLoading } = useAdversarialReport();

  // Calculate metrics from summary
  const metrics: Metric[] = useMemo(() => {
    if (!summary) return [];

    const totalAlerts = summary.total_alerts || 0;
    const activeAlerts =
      summary.by_status.active + summary.by_status.investigating || 0;
    const resolvedAlerts = summary.by_status.resolved || 0;
    const criticalAlerts = summary.by_severity.critical || 0;

    return [
      {
        label: "Total Alerts",
        value: totalAlerts.toLocaleString(),
        change: "+15%",
        trend: "up",
        icon: Activity,
        description: "All time",
      },
      {
        label: "Active Threats",
        value: activeAlerts.toLocaleString(),
        change:
          criticalAlerts > 0 ? `${criticalAlerts} critical` : "No critical",
        trend: criticalAlerts > 0 ? "up" : "down",
        icon: ShieldCheck,
        description: "Requires attention",
      },
      {
        label: "Resolved Issues",
        value: resolvedAlerts.toLocaleString(),
        change: `${((resolvedAlerts / totalAlerts) * 100).toFixed(1)}%`,
        trend: "up",
        icon: TrendingUp,
        description: "Resolution rate",
      },
      {
        label: "Critical Severity",
        value: criticalAlerts.toLocaleString(),
        change: `${((criticalAlerts / totalAlerts) * 100).toFixed(1)}%`,
        trend: criticalAlerts > 100 ? "up" : "down",
        icon: AlertTriangle,
        description: "Of total alerts",
      },
    ];
  }, [summary]);

  const chartData = useMemo(() => {
    if (!summary?.time_series) return [];
    // Format timestamp string to a readable day for the X-axis
    return summary.time_series.map((dataPoint: TimeSeriesData) => ({
      count: dataPoint.count,
      day: new Date(dataPoint.timestamp).toLocaleDateString("en-US", {
        weekday: "short",
      }),
    }));
  }, [summary]);

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-white">Security Metrics</h1>
        <p className="text-gray-400 mt-2">
          Comprehensive threat analysis and statistics
        </p>
      </motion.div>

      {/* Main Metrics Cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i: number) => (
            <div
              key={i}
              className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 animate-pulse"
            >
              <div className="h-8 w-8 bg-slate-700 rounded mb-4" />
              <div className="h-8 w-24 bg-slate-700 rounded mb-2" />
              <div className="h-4 w-32 bg-slate-700 rounded" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric: Metric, index: number) => {
            const Icon = metric.icon;
            const TrendIcon = metric.trend === "up" ? TrendingUp : TrendingDown;
            return (
              <motion.div
                key={metric.label}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:scale-105 transition-transform"
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
                <p className="text-xs text-gray-500 mt-1">
                  {metric.description}
                </p>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alerts Over Time */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white">Alerts Over Time</h2>
            <span className="text-xs text-gray-400">Last 7 days</span>
          </div>

          {isLoading ? (
            <div className="h-64 flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
            </div>
          ) : (
            <>
              {/* Chart.js Line Chart */}
              <div className="h-64 w-full">
                <AlertsTimeChart chartData={chartData} />
              </div>

              {/* Summary Stats Below Chart (Unchanged) */}
              <div className="mt-6 pt-6 border-t border-slate-700 grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-white">
                    {summary?.time_series.reduce(
                      (sum: number, d: TimeSeriesData) => sum + d.count,
                      0,
                    ) || 0}
                  </p>
                  <p className="text-xs text-gray-400">Total (7 days)</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-white">
                    {summary?.time_series.length
                      ? Math.round(
                          summary.time_series.reduce(
                            (sum: number, d: TimeSeriesData) => sum + d.count,
                            0,
                          ) / summary.time_series.length,
                        )
                      : 0}
                  </p>
                  <p className="text-xs text-gray-400">Daily Average</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-white">
                    {summary?.time_series.length
                      ? Math.max(
                          ...summary.time_series.map(
                            (d: TimeSeriesData) => d.count,
                          ),
                        )
                      : 0}
                  </p>
                  <p className="text-xs text-gray-400">Peak Day</p>
                </div>
              </div>
            </>
          )}
        </motion.div>

        {/* Attack Categories Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <h2 className="text-xl font-bold text-white mb-6">
            Attack Categories
          </h2>

          {isLoading ? (
            <div className="h-64 flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
            </div>
          ) : (
            <div className="space-y-4">
              {summary?.by_category.map(
                (category: CategoryData, index: number) => {
                  const percentage =
                    (category.count / summary.total_alerts) * 100;
                  const colors = [
                    {
                      gradient: "from-red-500 to-red-600",
                      text: "text-red-400",
                    },
                    {
                      gradient: "from-orange-500 to-orange-600",
                      text: "text-orange-400",
                    },
                    {
                      gradient: "from-yellow-500 to-yellow-600",
                      text: "text-yellow-400",
                    },
                    {
                      gradient: "from-green-500 to-green-600",
                      text: "text-green-400",
                    },
                    {
                      gradient: "from-blue-500 to-blue-600",
                      text: "text-blue-400",
                    },
                    {
                      gradient: "from-purple-500 to-purple-600",
                      text: "text-purple-400",
                    },
                  ];
                  const color = colors[index % colors.length];

                  return (
                    <motion.div
                      key={category.category}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.1 }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-white font-medium">
                          {category.category}
                        </span>
                        <span className={`text-sm font-semibold ${color.text}`}>
                          {category.count} ({percentage.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="h-3 bg-slate-900/50 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${percentage}%` }}
                          transition={{
                            duration: 0.5,
                            delay: 0.6 + index * 0.1,
                          }}
                          className={`h-full bg-linear-to-r ${color.gradient}`}
                        />
                      </div>
                    </motion.div>
                  );
                },
              )}
            </div>
          )}
        </motion.div>
      </div>

      {/* --- NEW: Adversarial Robustness Report --- */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <ShieldCheck className="w-6 h-6 text-green-400" />
          <h2 className="text-xl font-bold text-white">
            Adversarial Robustness (FGSM Attack)
          </h2>
        </div>

        {isReportLoading ? (
          <div className="h-80 flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
          </div>
        ) : adReport ? (
          <div className="h-80 w-full">
            <AdversarialReportChart chartData={adReport.metrics} />
          </div>
        ) : (
          <div className="h-80 flex items-center justify-center text-center text-gray-500">
            <p>Adversarial report data could not be loaded.</p>
          </div>
        )}
      </motion.div>

      {/* Status Distribution Pie Chart Visual */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <h2 className="text-xl font-bold text-white mb-6">
          Status Distribution
        </h2>

        {isLoading ? (
          <div className="h-48 flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              {
                label: "Active",
                count: summary?.by_status.active || 0,
                color: "from-red-500 to-red-600",
                bgColor: "bg-red-500/10",
                borderColor: "border-red-500/20",
              },
              {
                label: "Investigating",
                count: summary?.by_status.investigating || 0,
                color: "from-orange-500 to-orange-600",
                bgColor: "bg-orange-500/10",
                borderColor: "border-orange-500/20",
              },
              {
                label: "Acknowledged",
                count: summary?.by_status.acknowledged || 0,
                color: "from-yellow-500 to-yellow-600",
                bgColor: "bg-yellow-500/10",
                borderColor: "border-yellow-500/20",
              },
              {
                label: "Resolved",
                count: summary?.by_status.resolved || 0,
                color: "from-green-500 to-green-600",
                bgColor: "bg-green-500/10",
                borderColor: "border-green-500/20",
              },
            ].map(
              (
                status: {
                  label: string;
                  count: number;
                  color: string;
                  bgColor: string;
                  borderColor: string;
                },
                index: number,
              ) => {
                const percentage = summary?.total_alerts
                  ? (status.count / summary.total_alerts) * 100
                  : 0;

                return (
                  <motion.div
                    key={status.label}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.7 + index * 0.1 }}
                    className={`${status.bgColor} border ${status.borderColor} rounded-xl p-6 text-center hover:scale-105 transition-transform`}
                  >
                    <div className="relative w-24 h-24 mx-auto mb-4">
                      <svg className="transform -rotate-90 w-24 h-24">
                        <circle
                          cx="48"
                          cy="48"
                          r="40"
                          stroke="currentColor"
                          strokeWidth="8"
                          fill="transparent"
                          className="text-slate-700"
                        />
                        <circle
                          cx="48"
                          cy="48"
                          r="40"
                          stroke="currentColor"
                          strokeWidth="8"
                          fill="transparent"
                          strokeDasharray={`${percentage * 2.51} 251`}
                          className={`bg-linear-to-r ${status.color}`}
                          style={{ stroke: `url(#gradient-${index})` }}
                        />
                        <defs>
                          <linearGradient
                            id={`gradient-${index}`}
                            x1="0%"
                            y1="0%"
                            x2="100%"
                            y2="100%"
                          >
                            <stop
                              offset="0%"
                              style={{
                                stopColor: status.color.includes("red")
                                  ? "#ef4444"
                                  : status.color.includes("orange")
                                    ? "#f97316"
                                    : status.color.includes("yellow")
                                      ? "#eab308"
                                      : "#22c55e",
                              }}
                            />
                            <stop
                              offset="100%"
                              style={{
                                stopColor: status.color.includes("red")
                                  ? "#dc2626"
                                  : status.color.includes("orange")
                                    ? "#ea580c"
                                    : status.color.includes("yellow")
                                      ? "#ca8a04"
                                      : "#16a34a",
                              }}
                            />
                          </linearGradient>
                        </defs>
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-2xl font-bold text-white">
                          {percentage.toFixed(0)}%
                        </span>
                      </div>
                    </div>
                    <p className="text-lg font-bold text-white mb-1">
                      {status.count}
                    </p>
                    <p className="text-sm text-gray-400">{status.label}</p>
                  </motion.div>
                );
              },
            )}
          </div>
        )}
      </motion.div>
    </div>
  );
}
