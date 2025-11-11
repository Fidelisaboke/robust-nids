"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  AlertCircle,
  Loader2,
  ChevronUp,
  Sparkles,
  FileJson,
  Play,
  RotateCcw,
} from "lucide-react";
import { ThreatSummaryCard } from "./components/ThreatSummaryCard";
import { ShapExplanationChart } from "./components/ShapExplanationChart";
import { useNidsAnalysis, type NetworkFlowFeatures } from "@/hooks/useNids";
import { Button } from "@/components/ui/button";

const EXAMPLE_FLOW = {
  src_ip: "192.168.1.100",
  dst_ip: "10.0.0.50",
  src_port: 54321,
  dst_port: 22,
  protocol: 6,
  timestamp: "2025-11-09T12:00:00Z",
  flow_duration: 500,
  flow_byts_s: 3600,
  flow_pkts_s: 30,
  fwd_pkts_s: 20,
  bwd_pkts_s: 10,
  tot_fwd_pkts: 10,
  tot_bwd_pkts: 5,
  totlen_fwd_pkts: 1200,
  totlen_bwd_pkts: 600,
  fwd_pkt_len_max: 150,
  fwd_pkt_len_min: 60,
  fwd_pkt_len_mean: 120,
  fwd_pkt_len_std: 20,
  bwd_pkt_len_max: 140,
  bwd_pkt_len_min: 50,
  bwd_pkt_len_mean: 120,
  bwd_pkt_len_std: 25,
  pkt_len_max: 150,
  pkt_len_min: 50,
  pkt_len_mean: 120,
  pkt_len_std: 22,
  pkt_len_var: 484,
  fwd_header_len: 320,
  bwd_header_len: 160,
  fwd_seg_size_min: 20,
  fwd_act_data_pkts: 8,
  flow_iat_mean: 50,
  flow_iat_max: 80,
  flow_iat_min: 20,
  flow_iat_std: 10,
  fwd_iat_tot: 450,
  fwd_iat_max: 70,
  fwd_iat_min: 15,
  fwd_iat_mean: 45,
  fwd_iat_std: 8,
  bwd_iat_tot: 400,
  bwd_iat_max: 120,
  bwd_iat_min: 30,
  bwd_iat_mean: 80,
  bwd_iat_std: 15,
  fwd_psh_flags: 0,
  bwd_psh_flags: 0,
  fwd_urg_flags: 0,
  bwd_urg_flags: 0,
  fin_flag_cnt: 0,
  syn_flag_cnt: 1,
  rst_flag_cnt: 0,
  psh_flag_cnt: 0,
  ack_flag_cnt: 9,
  urg_flag_cnt: 0,
  ece_flag_cnt: 0,
  down_up_ratio: 0.5,
  pkt_size_avg: 120,
  init_fwd_win_byts: 29200,
  init_bwd_win_byts: 0,
  active_max: 350,
  active_min: 150,
  active_mean: 250,
  active_std: 50,
  idle_max: 0,
  idle_min: 0,
  idle_mean: 0,
  idle_std: 0,
  fwd_byts_b_avg: 0,
  fwd_pkts_b_avg: 0,
  bwd_byts_b_avg: 0,
  bwd_pkts_b_avg: 0,
  fwd_blk_rate_avg: 0,
  bwd_blk_rate_avg: 0,
  fwd_seg_size_avg: 120,
  bwd_seg_size_avg: 120,
  cwr_flag_count: 0,
  subflow_fwd_pkts: 10,
  subflow_bwd_pkts: 5,
  subflow_fwd_byts: 1200,
  subflow_bwd_byts: 600,
};

export default function ThreatIntelligencePage() {
  const [jsonInput, setJsonInput] = useState(
    JSON.stringify(EXAMPLE_FLOW, null, 2),
  );
  const [currentFeatures, setCurrentFeatures] =
    useState<NetworkFlowFeatures | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [jsonError, setJsonError] = useState<string | null>(null);

  const {
    analyzeThreat,
    explainPrediction,
    isPredicting,
    isExplaining,
    predictionError,
    explanationError,
    predictionData,
    explanationData,
    resetPrediction,
    resetExplanation,
  } = useNidsAnalysis();

  const handleAnalyze = async () => {
    setJsonError(null);
    setShowExplanation(false);
    resetExplanation();

    try {
      const features = JSON.parse(jsonInput);
      setCurrentFeatures(features);
      await analyzeThreat(features);
    } catch (error) {
      if (error instanceof SyntaxError) {
        setJsonError("Invalid JSON format. Please check your input.");
      } else {
        setJsonError(
          error instanceof Error ? error.message : "Analysis failed",
        );
      }
    }
  };

  const handleExplain = async () => {
    if (!currentFeatures) return;

    try {
      await explainPrediction(currentFeatures);
      setShowExplanation(true);
    } catch (error) {
      console.error("Explanation failed:", error);
      setShowExplanation(false);
    }
  };

  const handleReset = () => {
    setJsonInput(JSON.stringify(EXAMPLE_FLOW, null, 2));
    setCurrentFeatures(null);
    setShowExplanation(false);
    setJsonError(null);
    resetPrediction();
    resetExplanation();
  };

  const handleLoadExample = () => {
    setJsonInput(JSON.stringify(EXAMPLE_FLOW, null, 2));
    setJsonError(null);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Threat Intelligence
          </h1>
          <p className="text-gray-400">
            Manual threat analysis and SHAP-based explainability
          </p>
        </div>
        <div className="flex items-center space-x-2 px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700">
          <Brain className="w-5 h-5 text-blue-400" />
          <span className="text-sm text-gray-400">AI-Powered Analysis</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Input */}
        <div className="space-y-4">
          <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <FileJson className="w-5 h-5 text-blue-400" />
                <h2 className="text-lg font-semibold text-white">
                  Network Flow Data
                </h2>
              </div>
              <Button
                onClick={handleLoadExample}
                size="sm"
                variant="ghost"
                className="text-xs text-blue-400 hover:text-blue-300"
              >
                <Sparkles className="w-4 h-4 mr-1" />
                Load Example
              </Button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Paste CICFlowMeter JSON features
                </label>
                <textarea
                  value={jsonInput}
                  onChange={(e) => setJsonInput(e.target.value)}
                  className={`w-full h-[500px] px-4 py-3 bg-slate-900/50 border ${
                    jsonError ? "border-red-500" : "border-slate-700"
                  } rounded-lg text-gray-300 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-none`}
                  placeholder="Paste network flow JSON here..."
                  spellCheck={false}
                />
              </div>

              {jsonError && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-start space-x-2 p-3 bg-red-500/10 border border-red-500/50 rounded-lg"
                >
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-400">{jsonError}</p>
                </motion.div>
              )}

              <div className="flex space-x-3">
                <Button
                  onClick={handleAnalyze}
                  disabled={isPredicting || !jsonInput.trim()}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {isPredicting ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Analyze Threat
                    </>
                  )}
                </Button>
                <Button
                  onClick={handleReset}
                  variant="outline"
                  className="border-slate-700 text-gray-400 hover:text-white"
                >
                  <RotateCcw className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Results */}
        <div className="space-y-4">
          <AnimatePresence mode="wait">
            {predictionData ? (
              <motion.div
                key="results"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="space-y-4"
              >
                <ThreatSummaryCard prediction={predictionData} />

                {/* Why Button */}
                <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-xl p-4">
                  <Button
                    onClick={handleExplain}
                    disabled={isExplaining || showExplanation}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                  >
                    {isExplaining ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating Explanation...
                      </>
                    ) : showExplanation ? (
                      <>
                        <ChevronUp className="w-4 h-4 mr-2" />
                        Explanation Loaded
                      </>
                    ) : (
                      <>
                        <Brain className="w-4 h-4 mr-2" />
                        Why? (Show SHAP Analysis)
                      </>
                    )}
                  </Button>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-xl p-12 text-center"
              >
                <div className="flex flex-col items-center space-y-4">
                  <div className="p-4 bg-slate-900/50 rounded-full">
                    <Brain className="w-12 h-12 text-gray-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-400 mb-2">
                      Ready to Analyze
                    </h3>
                    <p className="text-sm text-gray-500">
                      Paste network flow data and click &quot;Analyze
                      Threat&quot; to begin
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {predictionError && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-500/10 border border-red-500/50 rounded-xl p-4"
            >
              <div className="flex items-start space-x-2">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-sm font-semibold text-red-400 mb-1">
                    Analysis Failed
                  </h3>
                  <p className="text-sm text-red-400/80">
                    {predictionError.message}
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Expandable SHAP Explanation */}
      <AnimatePresence>
        {showExplanation && explanationData && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <ShapExplanationChart explanation={explanationData} />
          </motion.div>
        )}
      </AnimatePresence>

      {explanationError && showExplanation && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-orange-500/10 border border-orange-500/50 rounded-xl p-4"
        >
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-orange-400 mb-1">
                Explanation Failed
              </h3>
              <p className="text-sm text-orange-400/80">
                {explanationError.message}
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
