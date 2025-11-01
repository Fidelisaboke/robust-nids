"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, Search, Clock, Eye, CheckCircle } from "lucide-react";

export default function AlertsPage() {
  const [filter, setFilter] = useState<
    "all" | "critical" | "high" | "medium" | "low"
  >("all");
  const [searchQuery, setSearchQuery] = useState("");

  const alerts = [
    {
      id: 1,
      severity: "critical",
      title: "SQL Injection Attempt Detected",
      description: "Multiple SQL injection attempts from suspicious IP address",
      source: "192.168.1.45",
      destination: "10.0.0.5:3306",
      timestamp: "2025-10-13T14:23:45Z",
      status: "active",
      category: "Web Attack",
    },
    {
      id: 2,
      severity: "high",
      title: "Brute Force Attack Detected",
      description: "Multiple failed SSH login attempts detected",
      source: "203.0.113.42",
      destination: "10.0.0.10:22",
      timestamp: "2025-10-13T14:15:22Z",
      status: "active",
      category: "Authentication",
    },
    {
      id: 3,
      severity: "high",
      title: "Port Scan Activity",
      description: "Systematic port scanning detected from external source",
      source: "198.51.100.78",
      destination: "10.0.0.0/24",
      timestamp: "2025-10-13T14:05:10Z",
      status: "investigating",
      category: "Reconnaissance",
    },
    {
      id: 4,
      severity: "medium",
      title: "Unusual Outbound Traffic",
      description: "Abnormal data transfer to unknown external server",
      source: "10.0.0.25",
      destination: "185.220.101.15:443",
      timestamp: "2025-10-13T13:45:33Z",
      status: "resolved",
      category: "Data Exfiltration",
    },
    {
      id: 5,
      severity: "medium",
      title: "Malware Signature Match",
      description: "Known malware pattern detected in network traffic",
      source: "10.0.0.18",
      destination: "93.184.216.34:80",
      timestamp: "2025-10-13T13:30:15Z",
      status: "resolved",
      category: "Malware",
    },
    {
      id: 6,
      severity: "low",
      title: "Certificate Expiring Soon",
      description: "SSL certificate will expire in 14 days",
      source: "web-server-01",
      destination: "N/A",
      timestamp: "2025-10-13T12:00:00Z",
      status: "acknowledged",
      category: "Configuration",
    },
  ];

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

  const filteredAlerts = alerts.filter((alert) => {
    const matchesFilter = filter === "all" || alert.severity === filter;
    const matchesSearch =
      alert.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      alert.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const alertCounts = {
    all: alerts.length,
    critical: alerts.filter((a) => a.severity === "critical").length,
    high: alerts.filter((a) => a.severity === "high").length,
    medium: alerts.filter((a) => a.severity === "medium").length,
    low: alerts.filter((a) => a.severity === "low").length,
  };

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
        className="flex flex-col sm:flex-row gap-4"
      >
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            placeholder="Search alerts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          />
        </div>
        <div className="flex gap-2 overflow-x-auto">
          {(["all", "critical", "high", "medium", "low"] as const).map(
            (severity) => (
              <button
                key={severity}
                onClick={() => setFilter(severity)}
                className={`px-4 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
                  filter === severity
                    ? "bg-blue-500 text-white"
                    : "bg-slate-800/50 text-gray-400 hover:bg-slate-700 hover:text-white"
                }`}
              >
                {severity.charAt(0).toUpperCase() + severity.slice(1)} (
                {alertCounts[severity]})
              </button>
            ),
          )}
        </div>
      </motion.div>

      {/* Alerts List */}
      <div className="space-y-4">
        {filteredAlerts.map((alert, index) => {
          const colors = getSeverityColor(alert.severity);
          return (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className={`bg-slate-800/50 border ${colors.border} rounded-xl p-6 hover:scale-[1.01] transition-transform`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start space-x-4 flex-1">
                  <div className={`p-3 ${colors.bg} rounded-lg`}>
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
                    <h3 className="text-lg font-semibold text-white mb-2">
                      {alert.title}
                    </h3>
                    <p className="text-sm text-gray-400 mb-3">
                      {alert.description}
                    </p>
                    <div className="flex flex-wrap gap-4 text-sm">
                      <div className="flex items-center space-x-2">
                        <span className="text-gray-500">Source:</span>
                        <code className="text-gray-300 bg-slate-900/50 px-2 py-1 rounded">
                          {alert.source}
                        </code>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-gray-500">Destination:</span>
                        <code className="text-gray-300 bg-slate-900/50 px-2 py-1 rounded">
                          {alert.destination}
                        </code>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4 text-gray-500" />
                        <span className="text-gray-400">
                          {new Date(alert.timestamp).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <button className="ml-4 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg transition-colors">
                  Investigate
                </button>
              </div>
            </motion.div>
          );
        })}
      </div>

      {filteredAlerts.length === 0 && (
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
    </div>
  );
}
