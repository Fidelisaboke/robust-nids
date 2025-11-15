"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  Search,
  Clock,
  Eye,
  CheckCircle,
  MoreVertical,
  Loader2,
  User,
  ExternalLink,
  Zap,
} from "lucide-react";
import { useAlerts, useAcknowledgeAlert } from "@/hooks/useAlertManagement";
import { AlertListParams, Alert } from "@/lib/api/alertsApi";
import { Pagination } from "@/components/Pagination";
import { AlertActionsDialog } from "@/components/dialogs/AlertActionsDialog";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { normalizeError } from "@/lib/api/apiClient";
import { useDebounce } from "@/hooks/useDebounce";

export default function AlertsPage() {
  const router = useRouter();
  const [filter, setFilter] = useState<
    "all" | "critical" | "high" | "medium" | "low"
  >("all");
  const [statusFilter, setStatusFilter] = useState<
    "all" | "active" | "investigating" | "resolved" | "acknowledged"
  >("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const pageSize = 10;
  const debouncedSearchQuery = useDebounce(searchQuery, 500);

  const acknowledgeMutation = useAcknowledgeAlert();

  const params: AlertListParams = {
    page: currentPage,
    size: pageSize,
    ...(filter !== "all" && { severity: filter }),
    ...(statusFilter !== "all" && { status: statusFilter }),
    ...(debouncedSearchQuery.trim() !== "" && {
      search: debouncedSearchQuery.trim(),
    }),
  };

  const { data, isLoading, error } = useAlerts(params);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return {
          bg: "bg-red-500/10",
          border: "border-red-500/20",
          text: "text-red-400",
          badge: "bg-red-500/20 text-red-400",
        };
      case "high":
        return {
          bg: "bg-orange-500/10",
          border: "border-orange-500/20",
          text: "text-orange-400",
          badge: "bg-orange-500/20 text-orange-400",
        };
      case "medium":
        return {
          bg: "bg-yellow-500/10",
          border: "border-yellow-500/20",
          text: "text-yellow-400",
          badge: "bg-yellow-500/20 text-yellow-400",
        };
      case "low":
        return {
          bg: "bg-blue-500/10",
          border: "border-blue-500/20",
          text: "text-blue-400",
          badge: "bg-blue-500/20 text-blue-400",
        };
      default:
        return {
          bg: "bg-gray-500/10",
          border: "border-gray-500/20",
          text: "text-gray-400",
          badge: "bg-gray-500/20 text-gray-400",
        };
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return <AlertTriangle className="w-4 h-4" />;
      case "investigating":
        return <Eye className="w-4 h-4" />;
      case "resolved":
        return <CheckCircle className="w-4 h-4" />;
      case "acknowledged":
        return <Clock className="w-4 h-4" />;
      default:
        return <AlertTriangle className="w-4 h-4" />;
    }
  };

  const handleQuickAcknowledge = async (
    alertId: number,
    e: React.MouseEvent,
  ) => {
    e.stopPropagation(); // Prevent card click
    try {
      await acknowledgeMutation.mutateAsync(alertId);
      toast.success("Alert acknowledged");
    } catch (error) {
      const normalizedError = normalizeError(error);
      toast.error(normalizedError.message || "Failed to acknowledge alert");
    }
  };

  const handleCardClick = (alertId: number) => {
    router.push(`/alerts/${alertId}`);
  };

  const filteredAlerts = data?.items || [];

  const alertCounts = {
    all: data?.total || 0,
    critical:
      data?.items.filter((a: Alert) => a.severity === "critical").length || 0,
    high: data?.items.filter((a: Alert) => a.severity === "high").length || 0,
    medium:
      data?.items.filter((a: Alert) => a.severity === "medium").length || 0,
    low: data?.items.filter((a: Alert) => a.severity === "low").length || 0,
  };

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <p className="text-gray-400">Failed to load alerts</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold text-white">Security Alerts</h1>
        <p className="text-gray-400 mt-2">
          Monitor and manage security threats in real-time
        </p>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="space-y-4"
      >
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            placeholder="Search alerts by title, category, or IP..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          />
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex gap-2 overflow-x-auto">
            {(["all", "critical", "high", "medium", "low"] as const).map(
              (severity) => (
                <button
                  key={severity}
                  onClick={() => {
                    setFilter(severity);
                    setCurrentPage(1);
                  }}
                  className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
                    filter === severity
                      ? "bg-blue-500 text-white"
                      : "bg-slate-800/50 text-gray-400 hover:bg-slate-700 hover:text-white"
                  }`}
                >
                  {severity.charAt(0).toUpperCase() + severity.slice(1)}
                  {filter === severity && ` (${alertCounts[severity]})`}
                </button>
              ),
            )}
          </div>

          <div className="flex gap-2 overflow-x-auto">
            {(
              [
                "all",
                "active",
                "investigating",
                "acknowledged",
                "resolved",
              ] as const
            ).map((status) => (
              <button
                key={status}
                onClick={() => {
                  setStatusFilter(status);
                  setCurrentPage(1);
                }}
                className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
                  statusFilter === status
                    ? "bg-purple-500 text-white"
                    : "bg-slate-800/50 text-gray-400 hover:bg-slate-700 hover:text-white"
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center h-96">
          <Loader2 className="w-12 h-12 text-blue-400 animate-spin" />
        </div>
      )}

      {/* Alerts List */}
      {!isLoading && (
        <>
          <div className="space-y-4">
            {filteredAlerts.map((alert: Alert, index: number) => {
              const colors = getSeverityColor(alert.severity);
              return (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  onClick={() => handleCardClick(alert.id)}
                  className={`bg-slate-800/50 border ${colors.border} rounded-xl p-6 hover:scale-[1.01] transition-all cursor-pointer group`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start space-x-4 flex-1">
                      <div
                        className={`p-3 ${colors.bg} rounded-lg ${colors.text}`}
                      >
                        {getStatusIcon(alert.status)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3 mb-2">
                          <span
                            className={`text-xs font-semibold px-3 py-1 rounded-full ${colors.badge}`}
                          >
                            {alert.severity.toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-400 capitalize">
                            {alert.status}
                          </span>
                          <span className="text-xs text-gray-500">
                            {alert.category}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="text-lg font-semibold text-white">
                            {alert.title}
                          </h3>
                          <ExternalLink className="w-4 h-4 text-gray-500 group-hover:text-blue-400 transition-colors" />
                        </div>
                        {alert.description && (
                          <p className="text-sm text-gray-400 mb-3 whitespace-pre-line line-clamp-2">
                            {alert.description}
                          </p>
                        )}
                        <div className="flex flex-wrap gap-4 text-sm mb-3">
                          <div className="flex items-center space-x-2">
                            <span className="text-gray-500">Source:</span>
                            <code className="text-gray-300 bg-slate-900/50 px-2 py-1 rounded">
                              {alert.src_ip}
                            </code>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="text-gray-500">Destination:</span>
                            <code className="text-gray-300 bg-slate-900/50 px-2 py-1 rounded">
                              {alert.dst_ip}:{alert.dst_port}
                            </code>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Clock className="w-4 h-4 text-gray-500" />
                            <span className="text-gray-400">
                              {new Date(alert.flow_timestamp).toLocaleString()}
                            </span>
                          </div>
                        </div>
                        {alert.assigned_user && (
                          <div className="flex items-center space-x-2 text-sm">
                            <User className="w-4 h-4 text-blue-400" />
                            <span className="text-gray-400">Assigned to:</span>
                            <span className="text-blue-400">
                              {alert.assigned_user.first_name}{" "}
                              {alert.assigned_user.last_name}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="flex items-center space-x-2 ml-4">
                      {alert.status !== "acknowledged" &&
                        alert.status !== "resolved" && (
                          <button
                            onClick={(e) => handleQuickAcknowledge(alert.id, e)}
                            disabled={acknowledgeMutation.isPending}
                            className="p-2 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 rounded-lg transition-colors disabled:opacity-50 group/btn"
                            title="Quick Acknowledge"
                          >
                            <Zap className="w-5 h-5" />
                          </button>
                        )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedAlert(alert);
                        }}
                        className="p-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg transition-colors"
                        title="More Actions"
                      >
                        <MoreVertical className="w-5 h-5" />
                      </button>
                    </div>
                  </div>

                  {/* Model Confidence Indicator */}
                  <div className="flex items-center space-x-4 pt-4 border-t border-slate-700/50">
                    <div className="flex items-center space-x-2 text-xs">
                      <span className="text-gray-500">Threat Confidence:</span>
                      <div className="flex items-center space-x-1">
                        <div className="h-1.5 w-16 bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              alert.model_output.binary.confidence > 0.9
                                ? "bg-red-500"
                                : alert.model_output.binary.confidence > 0.7
                                  ? "bg-orange-500"
                                  : "bg-yellow-500"
                            }`}
                            style={{
                              width: `${alert.model_output.binary.confidence * 100}%`,
                            }}
                          />
                        </div>
                        <span className="text-white font-medium">
                          {(alert.model_output.binary.confidence * 100).toFixed(
                            0,
                          )}
                          %
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 text-xs">
                      <span className="text-gray-500">Attack Type:</span>
                      <span className="text-white font-medium">
                        {alert.model_output.multiclass.label}
                      </span>
                      <span className="text-gray-500">
                        (
                        {(
                          alert.model_output.multiclass.confidence * 100
                        ).toFixed(0)}
                        %)
                      </span>
                    </div>
                    {alert.model_output.anomaly.is_anomaly && (
                      <div className="flex items-center space-x-2 text-xs">
                        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                        <span className="text-red-400 font-medium">
                          Anomaly Detected
                        </span>
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>

          {filteredAlerts.length === 0 && !isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <AlertTriangle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">
                No alerts found matching your criteria
              </p>
            </motion.div>
          )}

          {/* Pagination */}
          {data && data.total > 0 && (
            <Pagination
              currentPage={currentPage}
              totalPages={data.pages}
              onPageChange={setCurrentPage}
              totalItems={data.total}
              itemsPerPage={pageSize}
            />
          )}
        </>
      )}

      {/* Alert Actions Dialog */}
      {selectedAlert && (
        <AlertActionsDialog
          alert={selectedAlert}
          onClose={() => setSelectedAlert(null)}
        />
      )}
    </div>
  );
}
