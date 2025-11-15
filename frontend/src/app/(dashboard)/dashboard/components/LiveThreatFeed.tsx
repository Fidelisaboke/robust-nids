import React, { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertTriangle,
  Activity,
  Clock,
  Wifi,
  WifiOff,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { UnifiedPredictionResponse, useLiveThreats } from "@/hooks/useNids";
import { Badge } from "@/components/ui/badge";

// Helper function to format relative time
const formatRelativeTime = (timestamp: string): string => {
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now.getTime() - then.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);

  if (diffSecs < 60) return `${diffSecs}s ago`;
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return then.toLocaleString();
};

export const LiveThreatFeed: React.FC = () => {
  const { data: threats, isLoading, isError, error } = useLiveThreats();
  const previousThreatsRef = useRef<string[]>([]);

  // Track which threats are new for animation purposes
  const newThreatIds = useRef<Set<string>>(new Set());
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (threats) {
      // Clear any existing timer first to prevent stale updates
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
      const currentIds = threats.map(
        (t: UnifiedPredictionResponse) => t.id || t.timestamp,
      );
      const previousIds = previousThreatsRef.current;

      // Find new threats that weren't in the previous list
      const newIds = currentIds.filter(
        (id: string) => !previousIds.includes(id),
      );
      newThreatIds.current = new Set(newIds);

      // Update the reference
      previousThreatsRef.current = currentIds;

      // Clear new threat tracking after animation completes
      timerRef.current = setTimeout(() => {
        newThreatIds.current.clear();
      }, 1000);

      return () => {
        if (timerRef.current) {
          clearTimeout(timerRef.current);
        }
      };
    }
  }, [threats]);

  const getThreatConfig = (level: string) => {
    switch (level) {
      case "Critical":
        return {
          color: "text-red-400",
          bgColor: "bg-red-500/20",
          borderColor: "border-red-500/50",
          dotColor: "bg-red-500",
        };
      case "High":
        return {
          color: "text-orange-400",
          bgColor: "bg-orange-500/20",
          borderColor: "border-orange-500/50",
          dotColor: "bg-orange-500",
        };
      case "Medium":
        return {
          color: "text-yellow-400",
          bgColor: "bg-yellow-500/20",
          borderColor: "border-yellow-500/50",
          dotColor: "bg-yellow-500",
        };
      default:
        return {
          color: "text-green-400",
          bgColor: "bg-green-500/20",
          borderColor: "border-green-500/50",
          dotColor: "bg-green-500",
        };
    }
  };

  if (isLoading) {
    return (
      <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-white">
              Live Threat Monitor
            </h2>
          </div>
          <div className="flex items-center space-x-2 text-blue-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-xs">Loading...</span>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-white">
              Live Threat Monitor
            </h2>
          </div>
          <div className="flex items-center space-x-2 text-red-400">
            <WifiOff className="w-4 h-4" />
            <span className="text-xs">Disconnected</span>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center h-64 space-y-3">
          <AlertCircle className="w-12 h-12 text-red-400" />
          <p className="text-sm text-red-400">
            {error?.message || "Failed to load threat feed"}
          </p>
        </div>
      </div>
    );
  }

  const isEmpty = !threats || threats.length === 0;

  return (
    <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-semibold text-white">
            Live Threat Monitor
          </h2>
        </div>
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Wifi className="w-4 h-4 text-green-400" />
            <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          </div>
          <span className="text-xs text-green-400">Live</span>
        </div>
      </div>

      {/* Threat Feed */}
      <div className="max-h-[400px] overflow-y-auto space-y-2 pr-2 custom-scrollbar">
        {isEmpty ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center justify-center h-64 space-y-3"
          >
            <div className="p-4 bg-green-500/10 rounded-full">
              <Activity className="w-12 h-12 text-green-400" />
            </div>
            <div className="text-center">
              <h3 className="text-lg font-semibold text-green-400 mb-1">
                All Clear
              </h3>
              <p className="text-sm text-gray-400">
                No active threats detected in the network
              </p>
            </div>
          </motion.div>
        ) : (
          <AnimatePresence initial={false}>
            {threats.map((threat: UnifiedPredictionResponse) => {
              const config = getThreatConfig(threat.threat_level);
              const threatId = threat.id || threat.timestamp;
              const isNew = newThreatIds.current.has(threatId);

              return (
                <motion.div
                  key={threatId}
                  layout
                  initial={
                    isNew
                      ? { opacity: 0, y: -20, scale: 0.95 }
                      : { opacity: 1, y: 0, scale: 1 }
                  }
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, x: -100, scale: 0.95 }}
                  transition={{
                    duration: 0.3,
                    layout: { duration: 0.2 },
                  }}
                  className={`relative flex items-start space-x-3 p-3 bg-slate-900/50 rounded-lg border ${
                    isNew ? config.borderColor : "border-slate-800"
                  } hover:bg-slate-900 transition-colors cursor-pointer`}
                >
                  {/* Threat Level Indicator */}
                  <div className="flex-shrink-0 mt-1">
                    <div
                      className={`w-2 h-2 rounded-full ${config.dotColor} ${
                        threat.threat_level === "Critical"
                          ? "animate-pulse"
                          : ""
                      }`}
                    />
                  </div>

                  {/* Threat Details */}
                  <div className="flex-1 min-w-0 space-y-1">
                    {/* Header Row */}
                    <div className="flex items-center justify-between gap-2">
                      <Badge
                        className={`${config.bgColor} ${config.color} border ${config.borderColor} text-xs font-semibold`}
                      >
                        {threat.threat_level}
                      </Badge>
                      <div className="flex items-center space-x-1 text-xs text-gray-400">
                        <Clock className="w-3 h-3" />
                        <span>{formatRelativeTime(threat.timestamp)}</span>
                      </div>
                    </div>

                    {/* Attack Type & Classification */}
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-white">
                        {threat.multiclass.label}
                      </span>
                      <span className="text-xs text-gray-500">•</span>
                      <span className="text-xs text-gray-400">
                        {(threat.binary.confidence * 100).toFixed(1)}%
                        confidence
                      </span>
                    </div>

                    {/* IP Addresses */}
                    <div className="flex items-center space-x-2 text-xs">
                      <span className="text-gray-500">From:</span>
                      <span className="text-blue-400 font-mono">
                        {threat.src_ip}
                      </span>
                      <span className="text-gray-600">→</span>
                      <span className="text-gray-500">To:</span>
                      <span className="text-purple-400 font-mono">
                        {threat.dst_ip}
                      </span>
                    </div>

                    {/* Status Indicators */}
                    <div className="flex items-center space-x-3 text-xs">
                      <div className="flex items-center space-x-1">
                        <span className="text-gray-500">Binary:</span>
                        <span
                          className={
                            threat.binary.is_malicious
                              ? "text-red-400"
                              : "text-green-400"
                          }
                        >
                          {threat.binary.label}
                        </span>
                      </div>
                      {threat.anomaly.is_anomaly && (
                        <>
                          <span className="text-gray-600">•</span>
                          <div className="flex items-center space-x-1">
                            <AlertTriangle className="w-3 h-3 text-orange-400" />
                            <span className="text-orange-400">Anomaly</span>
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  {/* New Indicator */}
                  {isNew && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="absolute -top-1 -right-1 px-2 py-0.5 bg-blue-500 text-white text-xs font-bold rounded-full"
                    >
                      NEW
                    </motion.div>
                  )}
                </motion.div>
              );
            })}
          </AnimatePresence>
        )}
      </div>

      {/* Footer Stats */}
      {!isEmpty && (
        <div className="mt-4 pt-4 border-t border-slate-700 flex items-center justify-between text-xs text-gray-400">
          <span>Showing {threats.length} active threat(s)</span>
          <span>Updates every 2s</span>
        </div>
      )}

      {/* Custom Scrollbar Styles */}
      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(15, 23, 42, 0.5);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(71, 85, 105, 0.5);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(71, 85, 105, 0.8);
        }
      `}</style>
    </div>
  );
};
