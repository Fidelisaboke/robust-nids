"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Search, Download, Shield, User, Clock } from "lucide-react";
import { useAuditLogs } from "@/hooks/useUserManagement";
import { Skeleton } from "@/components/ui/skeleton";
import { format } from "date-fns";

export default function AuditLogsPage() {
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const { data: logsData, isLoading } = useAuditLogs(currentPage, 50);

  const filteredLogs = logsData?.logs.filter(
    (log) =>
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.admin_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.target_user_email?.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const getActionColor = (action: string) => {
    if (action.includes("delete") || action.includes("reject")) {
      return "text-red-400 bg-red-500/10 border-red-500/20";
    } else if (action.includes("approve") || action.includes("activate")) {
      return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
    } else if (action.includes("deactivate")) {
      return "text-orange-400 bg-orange-500/10 border-orange-500/20";
    } else {
      return "text-blue-400 bg-blue-500/10 border-blue-500/20";
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64 bg-slate-800" />
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-24 bg-slate-800" />
        ))}
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
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white">Audit Logs</h1>
            <p className="text-gray-400 mt-2">
              Track all administrative actions and system changes
            </p>
          </div>
          <button className="flex items-center space-x-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors">
            <Download className="w-5 h-5" />
            <span>Export Logs</span>
          </button>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="bg-slate-800/50 border border-emerald-500/20 rounded-xl p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-emerald-500/10 rounded-lg">
                <FileText className="w-6 h-6 text-emerald-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">
                  {logsData?.total || 0}
                </p>
                <p className="text-sm text-gray-400">Total Logs</p>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-slate-800/50 border border-blue-500/20 rounded-xl p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-blue-500/10 rounded-lg">
                <Shield className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">
                  {logsData?.logs.filter((l) => l.action.includes("security"))
                    .length || 0}
                </p>
                <p className="text-sm text-gray-400">Security Events</p>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-slate-800/50 border border-purple-500/20 rounded-xl p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-purple-500/10 rounded-lg">
                <User className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">
                  {new Set(logsData?.logs.map((l) => l.admin_id)).size || 0}
                </p>
                <p className="text-sm text-gray-400">Active Admins</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Search Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="relative"
      >
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search by action, admin email, or target user..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
        />
      </motion.div>

      {/* Logs List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="space-y-3"
      >
        {filteredLogs && filteredLogs.length > 0 ? (
          filteredLogs.map((log) => (
            <div
              key={log.id}
              className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-emerald-500/30 transition-colors"
            >
              <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-start space-x-4">
                    <div className="mt-1">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
                        <Shield className="w-5 h-5 text-white" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold border ${getActionColor(
                            log.action,
                          )}`}
                        >
                          {log.action}
                        </span>
                        <div className="flex items-center space-x-2 text-sm text-gray-400">
                          <Clock className="w-4 h-4" />
                          <span>
                            {format(
                              new Date(log.timestamp),
                              "MMM d, yyyy HH:mm:ss",
                            )}
                          </span>
                        </div>
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2 text-sm">
                          <span className="text-gray-400">Admin:</span>
                          <span className="text-white font-medium">
                            {log.admin_email}
                          </span>
                        </div>
                        {log.target_user_email && (
                          <div className="flex items-center space-x-2 text-sm">
                            <span className="text-gray-400">Target:</span>
                            <span className="text-white font-medium">
                              {log.target_user_email}
                            </span>
                          </div>
                        )}
                        <div className="flex items-center space-x-2 text-sm">
                          <span className="text-gray-400">IP:</span>
                          <span className="text-white">{log.ip_address}</span>
                        </div>
                        {log.details && Object.keys(log.details).length > 0 && (
                          <details className="mt-2">
                            <summary className="text-sm text-emerald-400 cursor-pointer hover:text-emerald-300">
                              View Details
                            </summary>
                            <pre className="mt-2 p-3 bg-slate-900/50 rounded text-xs text-gray-300 overflow-x-auto">
                              {JSON.stringify(log.details, null, 2)}
                            </pre>
                          </details>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12 bg-slate-800/50 border border-slate-700 rounded-xl">
            <p className="text-gray-400 text-lg">No audit logs found</p>
            <p className="text-gray-500 text-sm mt-2">
              {searchTerm
                ? "Try adjusting your search criteria"
                : "Logs will appear here as actions are performed"}
            </p>
          </div>
        )}
      </motion.div>

      {/* Pagination */}
      {logsData && logsData.total > 50 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-900 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            Previous
          </button>
          <span className="text-gray-400">Page {currentPage}</span>
          <button
            onClick={() => setCurrentPage((p) => p + 1)}
            disabled={!logsData || logsData.logs.length < 50}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-900 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
