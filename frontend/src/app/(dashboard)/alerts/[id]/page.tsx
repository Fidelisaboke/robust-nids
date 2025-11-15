"use client";

import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  AlertTriangle,
  Clock,
  User,
  Activity,
  Shield,
  TrendingUp,
  Loader2,
  Copy,
  Check,
  FileJson,
  ExternalLink,
} from "lucide-react";
import { useAlert } from "@/hooks/useAlertManagement";
import { AlertActionsDialog } from "@/components/dialogs/AlertActionsDialog";
import { useState } from "react";
import { toast } from "sonner";

export default function AlertDetailPage() {
  const params = useParams();
  const router = useRouter();
  const alertId = parseInt(params.id as string);
  const [showActions, setShowActions] = useState(false);
  const [copied, setCopied] = useState(false);

  const { data: alert, isLoading, error } = useAlert(alertId);

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

  const handleCopyFlowData = async () => {
    if (!alert?.flow_data) return;

    try {
      const jsonString = JSON.stringify(alert.flow_data, null, 2);
      await navigator.clipboard.writeText(jsonString);
      setCopied(true);
      toast.success("Flow data copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Failed to copy to clipboard");
    }
  };

  const handleAnalyzeInWorkbench = () => {
    if (!alert?.flow_data) return;

    // Store flow data in sessionStorage for the workbench to pick up
    sessionStorage.setItem(
      "threat-intelligence-flow",
      JSON.stringify(alert.flow_data, null, 2),
    );
    router.push("/threat-intelligence");
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-12 h-12 text-blue-400 animate-spin" />
      </div>
    );
  }

  if (error || !alert) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <p className="text-gray-400 mb-4">Failed to load alert details</p>
          <button
            onClick={() => router.push("/alerts")}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            Back to Alerts
          </button>
        </div>
      </div>
    );
  }

  const colors = getSeverityColor(alert.severity);

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <button
          onClick={() => router.push("/alerts")}
          className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Alerts</span>
        </button>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span
                className={`text-xs font-semibold px-3 py-1 rounded-full ${colors.badge}`}
              >
                {alert.severity.toUpperCase()}
              </span>
              <span className="text-xs text-gray-400 capitalize">
                {alert.status}
              </span>
              <span className="text-xs text-gray-500">{alert.category}</span>
            </div>
            <h1 className="text-3xl font-bold text-white">{alert.title}</h1>
          </div>
          <button
            onClick={() => setShowActions(true)}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            Manage Alert
          </button>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Overview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className={`bg-slate-800/50 border ${colors.border} rounded-xl p-6`}
          >
            <h2 className="text-xl font-bold text-white mb-4">Overview</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-400 mb-1">Source IP</p>
                <code className="text-white bg-slate-900/50 px-3 py-2 rounded block">
                  {alert.src_ip}
                </code>
              </div>
              <div>
                <p className="text-sm text-gray-400 mb-1">Destination</p>
                <code className="text-white bg-slate-900/50 px-3 py-2 rounded block">
                  {alert.dst_ip}:{alert.dst_port}
                </code>
              </div>
              <div>
                <p className="text-sm text-gray-400 mb-1">Timestamp</p>
                <p className="text-white">
                  {new Date(alert.flow_timestamp).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-400 mb-1">Alert ID</p>
                <p className="text-white">#{alert.id}</p>
              </div>
            </div>
            {alert.description && (
              <div className="mt-4">
                <p className="text-sm text-gray-400 mb-2">Notes</p>
                <p className="text-white bg-slate-900/50 px-4 py-3 rounded whitespace-pre-line">
                  {alert.description}
                </p>
              </div>
            )}
          </motion.div>

          {/* Network Flow Data */}
          {alert.flow_data && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.15 }}
              className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <FileJson className="w-5 h-5 text-blue-400" />
                  <h2 className="text-xl font-bold text-white">
                    Network Flow Data
                  </h2>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleAnalyzeInWorkbench}
                    className="px-3 py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 rounded-lg transition-colors flex items-center space-x-2 text-sm"
                  >
                    <ExternalLink className="w-4 h-4" />
                    <span>Analyze in Workbench</span>
                  </button>
                  <button
                    onClick={handleCopyFlowData}
                    className="px-3 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg transition-colors flex items-center space-x-2 text-sm"
                  >
                    {copied ? (
                      <>
                        <Check className="w-4 h-4" />
                        <span>Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        <span>Copy JSON</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              <div className="relative">
                <pre className="bg-slate-900/50 border border-slate-700 rounded-lg p-4 overflow-x-auto max-h-96 text-xs text-gray-300 font-mono">
                  {JSON.stringify(alert.flow_data, null, 2)}
                </pre>
              </div>

              <div className="mt-3 flex items-start space-x-2 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                <FileJson className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <p className="text-xs text-blue-300">
                  This is the original network flow data captured by
                  CICFlowMeter. You can copy it to analyze in the Threat
                  Intelligence workbench or use it for further investigation.
                </p>
              </div>
            </motion.div>
          )}

          {/* Model Analysis */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
          >
            <h2 className="text-xl font-bold text-white mb-4">
              Model Analysis
            </h2>

            {/* Binary Classification */}
            <div className="mb-6">
              <div className="flex items-center space-x-2 mb-2">
                <Shield className="w-5 h-5 text-blue-400" />
                <h3 className="text-lg font-semibold text-white">
                  Binary Classification
                </h3>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400">Label:</span>
                  <span
                    className={`font-semibold ${
                      alert.model_output.binary.is_malicious
                        ? "text-red-400"
                        : "text-green-400"
                    }`}
                  >
                    {alert.model_output.binary.label}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Confidence:</span>
                  <span className="text-white font-semibold">
                    {(alert.model_output.binary.confidence * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Multiclass Classification */}
            <div className="mb-6">
              <div className="flex items-center space-x-2 mb-2">
                <Activity className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-semibold text-white">
                  Attack Type Classification
                </h3>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-gray-400">Detected Type:</span>
                  <span className="text-white font-semibold">
                    {alert.model_output.multiclass.label}
                  </span>
                </div>
                <div className="space-y-2">
                  {Object.entries(alert.model_output.multiclass.probabilities)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 5)
                    .map(([type, prob]) => (
                      <div key={type}>
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="text-gray-400">{type}</span>
                          <span className="text-white">
                            {(prob * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-linear-to-r from-purple-500 to-pink-500"
                            style={{ width: `${prob * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>

            {/* Anomaly Detection */}
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-5 h-5 text-orange-400" />
                <h3 className="text-lg font-semibold text-white">
                  Anomaly Detection
                </h3>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400">Status:</span>
                  <span
                    className={`font-semibold ${
                      alert.model_output.anomaly.is_anomaly
                        ? "text-red-400"
                        : "text-green-400"
                    }`}
                  >
                    {alert.model_output.anomaly.is_anomaly
                      ? "Anomaly Detected"
                      : "Normal"}
                  </span>
                </div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400">Anomaly Score:</span>
                  <span className="text-white font-semibold">
                    {alert.model_output.anomaly.anomaly_score.toFixed(6)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Threshold:</span>
                  <span className="text-white font-semibold">
                    {alert.model_output.anomaly.threshold.toFixed(6)}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Assignment Info */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
          >
            <div className="flex items-center space-x-2 mb-4">
              <User className="w-5 h-5 text-blue-400" />
              <h3 className="text-lg font-semibold text-white">Assignment</h3>
            </div>
            {alert.assigned_user ? (
              <div className="bg-slate-900/50 rounded-lg p-4">
                <p className="text-sm text-gray-400 mb-2">Assigned to:</p>
                <p className="text-white font-semibold mb-1">
                  {alert.assigned_user.first_name}{" "}
                  {alert.assigned_user.last_name}
                </p>
                <p className="text-sm text-gray-400">
                  {alert.assigned_user.email}
                </p>
                <p className="text-sm text-gray-400">
                  {alert.assigned_user.job_title}
                </p>
                <p className="text-sm text-gray-400">
                  {alert.assigned_user.department}
                </p>
              </div>
            ) : (
              <p className="text-gray-400 text-sm">Not assigned</p>
            )}
          </motion.div>

          {/* Timeline */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
          >
            <div className="flex items-center space-x-2 mb-4">
              <Clock className="w-5 h-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Timeline</h3>
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-400 mb-1">Created</p>
                <p className="text-white text-sm">
                  {new Date(alert.created_at).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-400 mb-1">Last Updated</p>
                <p className="text-white text-sm">
                  {new Date(alert.updated_at).toLocaleString()}
                </p>
              </div>
            </div>
          </motion.div>

          {/* Threat Level */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className={`bg-slate-800/50 border ${colors.border} rounded-xl p-6`}
          >
            <div className="flex items-center space-x-2 mb-4">
              <AlertTriangle className={`w-5 h-5 ${colors.text}`} />
              <h3 className="text-lg font-semibold text-white">Threat Level</h3>
            </div>
            <div className="text-center">
              <p className={`text-3xl font-bold ${colors.text}`}>
                {alert.model_output.threat_level}
              </p>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Alert Actions Dialog */}
      {showActions && (
        <AlertActionsDialog
          alert={alert}
          onClose={() => setShowActions(false)}
        />
      )}
    </div>
  );
}
