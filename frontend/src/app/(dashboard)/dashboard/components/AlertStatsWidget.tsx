import { motion } from "framer-motion";
import { AlertTriangle, Clock, CheckCircle, Eye, Loader2 } from "lucide-react";
import { useAlertsSummary } from "@/hooks/useAlertManagement";

export function AlertStatsWidget() {
  const { data: summary, isLoading } = useAlertsSummary();

  const statCards = [
    {
      label: "Active",
      value: summary?.by_status.active || 0,
      icon: AlertTriangle,
      color: "text-red-400",
      bgColor: "bg-red-500/10",
      borderColor: "border-red-500/20",
    },
    {
      label: "Investigating",
      value: summary?.by_status.investigating || 0,
      icon: Eye,
      color: "text-orange-400",
      bgColor: "bg-orange-500/10",
      borderColor: "border-orange-500/20",
    },
    {
      label: "Acknowledged",
      value: summary?.by_status.acknowledged || 0,
      icon: Clock,
      color: "text-yellow-400",
      bgColor: "bg-yellow-500/10",
      borderColor: "border-yellow-500/20",
    },
    {
      label: "Resolved",
      value: summary?.by_status.resolved || 0,
      icon: CheckCircle,
      color: "text-green-400",
      bgColor: "bg-green-500/10",
      borderColor: "border-green-500/20",
    },
  ];

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 animate-pulse"
          >
            <div className="h-6 w-6 bg-slate-700 rounded mb-3" />
            <div className="h-8 w-16 bg-slate-700 rounded mb-2" />
            <div className="h-4 w-20 bg-slate-700 rounded" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {statCards.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className={`${stat.bgColor} border ${stat.borderColor} rounded-xl p-6 hover:scale-105 transition-transform`}
          >
            <div className="flex items-center justify-between mb-3">
              <Icon className={`w-6 h-6 ${stat.color}`} />
              <span className={`text-2xl font-bold ${stat.color}`}>
                {stat.value}
              </span>
            </div>
            <p className="text-sm text-gray-400 font-medium">{stat.label}</p>
          </motion.div>
        );
      })}
    </div>
  );
}

export function SeverityBreakdown() {
  const { data: summary, isLoading } = useAlertsSummary();

  const severities = [
    {
      label: "Critical",
      count: summary?.by_severity.critical || 0,
      color: "from-red-500 to-red-600",
      bgColor: "bg-red-500/10",
      textColor: "text-red-400",
    },
    {
      label: "High",
      count: summary?.by_severity.high || 0,
      color: "from-orange-500 to-orange-600",
      bgColor: "bg-orange-500/10",
      textColor: "text-orange-400",
    },
    {
      label: "Medium",
      count: summary?.by_severity.medium || 0,
      color: "from-yellow-500 to-yellow-600",
      bgColor: "bg-yellow-500/10",
      textColor: "text-yellow-400",
    },
    {
      label: "Low",
      count: summary?.by_severity.low || 0,
      color: "from-blue-500 to-blue-600",
      bgColor: "bg-blue-500/10",
      textColor: "text-blue-400",
    },
  ];

  const total = severities.reduce((sum, s) => sum + s.count, 0);

  if (isLoading) {
    return (
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
    >
      <h3 className="text-lg font-bold text-white mb-4">Severity Breakdown</h3>

      {/* Bar Chart */}
      <div className="space-y-4 mb-6">
        {severities.map((severity) => {
          const percentage = total > 0 ? (severity.count / total) * 100 : 0;

          return (
            <div key={severity.label}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">{severity.label}</span>
                <span className={`text-sm font-semibold ${severity.textColor}`}>
                  {severity.count} ({percentage.toFixed(0)}%)
                </span>
              </div>
              <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${percentage}%` }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className={`h-full bg-gradient-to-r ${severity.color}`}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 gap-3">
        {severities.map((severity) => (
          <div
            key={severity.label}
            className={`${severity.bgColor} rounded-lg p-3 text-center`}
          >
            <p className={`text-2xl font-bold ${severity.textColor}`}>
              {severity.count}
            </p>
            <p className="text-xs text-gray-400 mt-1">{severity.label}</p>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
