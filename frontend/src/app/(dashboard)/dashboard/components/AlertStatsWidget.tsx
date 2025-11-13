import { motion } from "framer-motion";
import { AlertTriangle, Clock, CheckCircle, Eye } from "lucide-react";
import { useAlerts } from "@/hooks/useAlertManagement";

export function AlertStatsWidget() {
  // Fetch all alerts
  // TODO: Optimize this by creating a dedicated stats endpoint
  const { data: allAlerts } = useAlerts({ size: 100 });

  // Calculate statistics
  const stats = {
    total: allAlerts?.total || 0,
    bySeverity: {
      critical:
        allAlerts?.items.filter((a) => a.severity === "critical").length || 0,
      high: allAlerts?.items.filter((a) => a.severity === "high").length || 0,
      medium:
        allAlerts?.items.filter((a) => a.severity === "medium").length || 0,
      low: allAlerts?.items.filter((a) => a.severity === "low").length || 0,
    },
    byStatus: {
      active: allAlerts?.items.filter((a) => a.status === "active").length || 0,
      investigating:
        allAlerts?.items.filter((a) => a.status === "investigating").length ||
        0,
      acknowledged:
        allAlerts?.items.filter((a) => a.status === "acknowledged").length || 0,
      resolved:
        allAlerts?.items.filter((a) => a.status === "resolved").length || 0,
    },
  };

  const statCards = [
    {
      label: "Active",
      value: stats.byStatus.active,
      icon: AlertTriangle,
      color: "text-red-400",
      bgColor: "bg-red-500/10",
      borderColor: "border-red-500/20",
    },
    {
      label: "Investigating",
      value: stats.byStatus.investigating,
      icon: Eye,
      color: "text-orange-400",
      bgColor: "bg-orange-500/10",
      borderColor: "border-orange-500/20",
    },
    {
      label: "Acknowledged",
      value: stats.byStatus.acknowledged,
      icon: Clock,
      color: "text-yellow-400",
      bgColor: "bg-yellow-500/10",
      borderColor: "border-yellow-500/20",
    },
    {
      label: "Resolved",
      value: stats.byStatus.resolved,
      icon: CheckCircle,
      color: "text-green-400",
      bgColor: "bg-green-500/10",
      borderColor: "border-green-500/20",
    },
  ];

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
  // Fetch all alerts
  // TODO: Optimize this by creating a dedicated stats endpoint
  const { data: allAlerts } = useAlerts({ size: 100 });

  const severities = [
    {
      label: "Critical",
      count:
        allAlerts?.items.filter((a) => a.severity === "critical").length || 0,
      color: "from-red-500 to-red-600",
      bgColor: "bg-red-500/10",
      textColor: "text-red-400",
    },
    {
      label: "High",
      count: allAlerts?.items.filter((a) => a.severity === "high").length || 0,
      color: "from-orange-500 to-orange-600",
      bgColor: "bg-orange-500/10",
      textColor: "text-orange-400",
    },
    {
      label: "Medium",
      count:
        allAlerts?.items.filter((a) => a.severity === "medium").length || 0,
      color: "from-yellow-500 to-yellow-600",
      bgColor: "bg-yellow-500/10",
      textColor: "text-yellow-400",
    },
    {
      label: "Low",
      count: allAlerts?.items.filter((a) => a.severity === "low").length || 0,
      color: "from-blue-500 to-blue-600",
      bgColor: "bg-blue-500/10",
      textColor: "text-blue-400",
    },
  ];

  const total = severities.reduce((sum, s) => sum + s.count, 0);

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
