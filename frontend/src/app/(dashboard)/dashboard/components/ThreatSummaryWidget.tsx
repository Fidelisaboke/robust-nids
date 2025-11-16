import React from "react";
import { motion } from "framer-motion";
import { AlertTriangle, Shield, Activity, TrendingUp } from "lucide-react";
import { useLiveThreats } from "@/hooks/useNids";

export const ThreatSummaryWidget: React.FC = () => {
  const { data: threats } = useLiveThreats();

  // Calculate threat statistics
  const stats = React.useMemo(() => {
    if (!threats || threats.length === 0) {
      return {
        critical: 0,
        high: 0,
        total: 0,
        anomalies: 0,
      };
    }

    return {
      critical: threats.filter((t) => t.threat_level === "Critical").length,
      high: threats.filter((t) => t.threat_level === "High").length,
      total: threats.length,
      anomalies: threats.filter((t) => t.anomaly.is_anomaly).length,
    };
  }, [threats]);

  const summaryCards = [
    {
      label: "Critical",
      value: stats.critical,
      icon: AlertTriangle,
      color: "text-red-400",
      bgColor: "bg-red-500/10",
      borderColor: "border-red-500/30",
      animate: stats.critical > 0,
    },
    {
      label: "High Priority",
      value: stats.high,
      icon: Shield,
      color: "text-orange-400",
      bgColor: "bg-orange-500/10",
      borderColor: "border-orange-500/30",
      animate: false,
    },
    {
      label: "Active Threats",
      value: stats.total,
      icon: Activity,
      color: "text-blue-400",
      bgColor: "bg-blue-500/10",
      borderColor: "border-blue-500/30",
      animate: false,
    },
    {
      label: "Anomalies",
      value: stats.anomalies,
      icon: TrendingUp,
      color: "text-purple-400",
      bgColor: "bg-purple-500/10",
      borderColor: "border-purple-500/30",
      animate: false,
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {summaryCards.map((card, index) => {
        const Icon = card.icon;
        return (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className={`relative bg-slate-800/50 backdrop-blur-xl border ${card.borderColor} rounded-xl p-4 overflow-hidden`}
          >
            {/* Background Glow Effect */}
            <div
              className={`absolute inset-0 ${card.bgColor} opacity-0 hover:opacity-100 transition-opacity duration-300`}
            />

            {/* Content */}
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2 ${card.bgColor} rounded-lg`}>
                  <Icon
                    className={`w-5 h-5 ${card.color} ${card.animate ? "animate-pulse" : ""}`}
                  />
                </div>
                {card.animate && card.value > 0 && (
                  <motion.div
                    animate={{
                      scale: [1, 1.2, 1],
                      opacity: [1, 0.8, 1],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                    className="w-2 h-2 bg-red-500 rounded-full"
                  />
                )}
              </div>
              <div className="space-y-1">
                <p className={`text-3xl font-bold ${card.color}`}>
                  {card.value}
                </p>
                <p className="text-sm text-gray-400">{card.label}</p>
              </div>
            </div>

            {/* Animated Border for Critical */}
            {card.animate && card.value > 0 && (
              <motion.div
                className="absolute inset-0 border-2 border-red-500 rounded-xl"
                animate={{
                  opacity: [0.3, 0.6, 0.3],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
            )}
          </motion.div>
        );
      })}
    </div>
  );
};
