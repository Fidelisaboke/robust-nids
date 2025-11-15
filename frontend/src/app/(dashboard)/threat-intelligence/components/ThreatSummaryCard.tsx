import React from "react";
import { AlertTriangle, Shield, Activity } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface BinaryPrediction {
  label: string;
  confidence: number;
  is_malicious: boolean;
}

interface MulticlassPrediction {
  label: string;
  confidence: number;
  probabilities: Record<string, number>;
}

interface AnomalyDetection {
  is_anomaly: boolean;
  anomaly_score: number;
  threshold: number;
}

interface UnifiedPredictionResponse {
  timestamp: string;
  threat_level: "Low" | "Medium" | "High" | "Critical";
  binary: BinaryPrediction;
  multiclass: MulticlassPrediction;
  anomaly: AnomalyDetection;
}

interface ThreatSummaryCardProps {
  prediction: UnifiedPredictionResponse;
}

export const ThreatSummaryCard: React.FC<ThreatSummaryCardProps> = ({
  prediction,
}) => {
  const getThreatLevelConfig = (level: string) => {
    switch (level) {
      case "Critical":
        return {
          color: "bg-red-500",
          textColor: "text-red-400",
          borderColor: "border-red-500/50",
          bgGlow: "bg-red-500/10",
          icon: AlertTriangle,
          pulse: true,
        };
      case "High":
        return {
          color: "bg-orange-500",
          textColor: "text-orange-400",
          borderColor: "border-orange-500/50",
          bgGlow: "bg-orange-500/10",
          icon: AlertTriangle,
          pulse: false,
        };
      case "Medium":
        return {
          color: "bg-yellow-500",
          textColor: "text-yellow-400",
          borderColor: "border-yellow-500/50",
          bgGlow: "bg-yellow-500/10",
          icon: Shield,
          pulse: false,
        };
      default:
        return {
          color: "bg-green-500",
          textColor: "text-green-400",
          borderColor: "border-green-500/50",
          bgGlow: "bg-green-500/10",
          icon: Shield,
          pulse: false,
        };
    }
  };

  const config = getThreatLevelConfig(prediction.threat_level);
  const ThreatIcon = config.icon;

  const anomalyPercentage =
    (prediction.anomaly.anomaly_score / prediction.anomaly.threshold) * 100;
  const isAnomalous = prediction.anomaly.is_anomaly;

  return (
    <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-xl p-6 space-y-6">
      {/* Threat Level Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div
            className={`relative p-4 rounded-xl ${config.bgGlow} border ${config.borderColor}`}
          >
            <ThreatIcon className={`w-8 h-8 ${config.textColor}`} />
            {config.pulse && (
              <>
                <div
                  className={`absolute inset-0 ${config.color} opacity-30 rounded-xl animate-ping`}
                />
                <div
                  className={`absolute inset-0 ${config.color} opacity-20 rounded-xl animate-pulse`}
                />
              </>
            )}
          </div>
          <div>
            <h3 className="text-2xl font-bold text-white">
              {prediction.threat_level} Threat
            </h3>
            <p className="text-sm text-gray-400">
              {new Date(prediction.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
        <div
          className={`px-4 py-2 rounded-lg border ${config.borderColor} ${config.bgGlow}`}
        >
          <span className={`text-lg font-semibold ${config.textColor}`}>
            {prediction.threat_level.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Three Engine Votes */}
      <div className="grid grid-cols-1 2xl:grid-cols-2 gap-4">
        {/* Binary Classifier */}
        <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center space-x-2 mb-3">
            <Shield className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-gray-400">Label</span>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span
                className={`text-lg font-bold ${
                  prediction.binary.is_malicious
                    ? "text-red-400"
                    : "text-green-400"
                }`}
              >
                {prediction.binary.label}
              </span>
              <Badge
                className={
                  prediction.binary.is_malicious
                    ? "bg-red-500/20 text-red-400 border-red-500/50"
                    : "bg-green-500/20 text-green-400 border-green-500/50"
                }
              >
                {(prediction.binary.confidence * 100).toFixed(1)}%
              </Badge>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full transition-all ${
                  prediction.binary.is_malicious ? "bg-red-500" : "bg-green-500"
                }`}
                style={{ width: `${prediction.binary.confidence * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Multiclass Classifier */}
        <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center space-x-2 mb-3">
            <Activity className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-medium text-gray-400">
              Traffic Type
            </span>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between space-x-2">
              <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/50 text-sm font-semibold">
                {prediction.multiclass.label}
              </Badge>
              <span className="text-sm text-gray-400">
                {(prediction.multiclass.confidence * 100).toFixed(1)}%
              </span>
            </div>
            <div className="space-y-1">
              {Object.entries(prediction.multiclass.probabilities)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 3)
                .map(([attack, prob]) => (
                  <div key={attack} className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500 w-20 truncate">
                      {attack}
                    </span>
                    <div className="flex-1 bg-slate-800 rounded-full h-1 overflow-hidden">
                      <div
                        className="h-full bg-purple-500/50"
                        style={{ width: `${prob * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 w-10 text-right">
                      {(prob * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
            </div>
          </div>
        </div>

        {/* Anomaly Detector */}
        <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center space-x-2 mb-3">
            <AlertTriangle className="w-4 h-4 text-cyan-400" />
            <span className="text-sm font-medium text-gray-400">
              Anomaly Detector
            </span>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span
                className={`text-lg font-bold ${
                  isAnomalous ? "text-red-400" : "text-green-400"
                }`}
              >
                {isAnomalous ? "Anomalous" : "Normal"}
              </span>
              <Badge
                className={
                  isAnomalous
                    ? "bg-red-500/20 text-red-400 border-red-500/50"
                    : "bg-green-500/20 text-green-400 border-green-500/50"
                }
              >
                {prediction.anomaly.anomaly_score.toFixed(4)}
              </Badge>
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-500">Score vs Threshold</span>
                <span className="text-gray-500">
                  {prediction.anomaly.threshold.toFixed(4)}
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden relative">
                <div
                  className={`h-full transition-all ${
                    isAnomalous ? "bg-red-500" : "bg-green-500"
                  }`}
                  style={{
                    width: `${Math.min(anomalyPercentage, 100)}%`,
                  }}
                />
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-yellow-400"
                  style={{ left: "100%" }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
