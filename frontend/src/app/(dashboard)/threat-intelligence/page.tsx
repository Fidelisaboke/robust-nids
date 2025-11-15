"use client";

import React, { useEffect, useState } from "react";
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
  Shield,
  Zap,
  CheckCircle,
  XCircle,
} from "lucide-react";
import { ThreatSummaryCard } from "./components/ThreatSummaryCard";
import { ShapExplanationChart } from "./components/ShapExplanationChart";
import {
  useNidsAnalysis,
  useRobustnessDemo,
  type NetworkFlowFeatures,
  type RobustnessResult,
} from "@/hooks/useNids";
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

const ADVERSARIAL_EXAMPLE = {
  src_ip: "127.0.0.1",
  dst_ip: "127.0.0.1",
  src_port: 57441,
  dst_port: 22,
  protocol: 2048,
  timestamp: "2025-11-11 00:41:01",
  flow_duration: 1e-6,
  flow_byts_s: 188000000.0,
  flow_pkts_s: 3000000.0,
  fwd_pkts_s: 2000000.0,
  bwd_pkts_s: 1000000.0,
  tot_fwd_pkts: 2,
  tot_bwd_pkts: 1,
  totlen_fwd_pkts: 128,
  totlen_bwd_pkts: 60,
  fwd_pkt_len_max: 64,
  fwd_pkt_len_min: 64,
  fwd_pkt_len_mean: 64.0,
  fwd_pkt_len_std: 0.0,
  bwd_pkt_len_max: 60,
  bwd_pkt_len_min: 60,
  bwd_pkt_len_mean: 60.0,
  bwd_pkt_len_std: 0.0,
  syn_flag_cnt: 2,
  rst_flag_cnt: 1,
  ack_flag_cnt: 1,
  init_fwd_win_byts: 1024,
  init_bwd_win_byts: 0,
};

export default function ThreatIntelligencePage() {
  const [jsonInput, setJsonInput] = useState(
    JSON.stringify(EXAMPLE_FLOW, null, 2),
  );
  const [currentFeatures, setCurrentFeatures] =
    useState<NetworkFlowFeatures | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [jsonError, setJsonError] = useState<string | null>(null);

  // Robustness demo state
  const [robustnessInput, setRobustnessInput] = useState(
    JSON.stringify(ADVERSARIAL_EXAMPLE, null, 2),
  );
  const [robustnessError, setRobustnessError] = useState<string | null>(null);

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

  const robustnessDemo = useRobustnessDemo();

  // Get threat intelligence features from sessionStorage
  useEffect(() => {
    const storedFlow = sessionStorage.getItem("threat-intelligence-flow");
    if (storedFlow) {
      setJsonInput(storedFlow);
      sessionStorage.removeItem("threat-intelligence-flow");
    }
  }, []);

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
    setRobustnessInput(JSON.stringify(ADVERSARIAL_EXAMPLE, null, 2));
    setRobustnessError(null);
    resetPrediction();
    resetExplanation();
    robustnessDemo.reset();
  };

  const handleLoadExample = () => {
    setJsonInput(JSON.stringify(EXAMPLE_FLOW, null, 2));
    setJsonError(null);
  };

  const handleRunRobustnessDemo = async () => {
    setRobustnessError(null);

    try {
      const features = JSON.parse(robustnessInput);
      await robustnessDemo.mutateAsync(features);
    } catch (error) {
      if (error instanceof SyntaxError) {
        setRobustnessError("Invalid JSON format. Please check your input.");
      } else {
        setRobustnessError(
          error instanceof Error ? error.message : "Demo failed",
        );
      }
    }
  };

  const getResultIcon = (result: RobustnessResult) => {
    if (result.input_type === "Normal Flow") {
      return <CheckCircle className="w-5 h-5 text-green-400" />;
    }
    if (
      result.model_name.includes("Vulnerable") &&
      result.predicted_label === "Benign"
    ) {
      return <XCircle className="w-5 h-5 text-red-400" />;
    }
    if (
      result.model_name.includes("Robust") &&
      result.predicted_label === "Malicious"
    ) {
      return <Shield className="w-5 h-5 text-green-400" />;
    }
    return <AlertCircle className="w-5 h-5 text-yellow-400" />;
  };

  const getResultBadge = (result: RobustnessResult) => {
    if (result.input_type === "Normal Flow") {
      return "bg-green-500/10 border-green-500/20 text-green-400";
    }
    if (
      result.model_name.includes("Vulnerable") &&
      result.predicted_label === "Benign"
    ) {
      return "bg-red-500/10 border-red-500/20 text-red-400";
    }
    if (
      result.model_name.includes("Robust") &&
      result.predicted_label === "Malicious"
    ) {
      return "bg-green-500/10 border-green-500/20 text-green-400";
    }
    return "bg-yellow-500/10 border-yellow-500/20 text-yellow-400";
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
            Manual threat analysis and explainability workbench
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
                  <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
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
                <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
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
            <AlertCircle className="w-5 h-5 text-orange-400 shrink-0 mt-0.5" />
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

      {/* Adversarial Robustness Demo Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-linear-to-br from-purple-500/5 to-blue-500/5 border border-purple-500/20 rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-2">
          <Shield className="w-6 h-6 text-purple-400" />
          <h2 className="text-2xl font-bold text-white">
            Adversarial Robustness Demo
          </h2>
        </div>
        <p className="text-gray-400 text-sm mb-6">
          See how our adversarially-trained model defends against evasion
          attacks (FGSM)
        </p>

        {/* Input Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-400">
                  Malicious Network Flow (for attack)
                </label>
                <Button
                  onClick={() =>
                    setRobustnessInput(
                      JSON.stringify(ADVERSARIAL_EXAMPLE, null, 2),
                    )
                  }
                  size="sm"
                  variant="ghost"
                  className="text-xs text-purple-400 hover:text-purple-300"
                >
                  <Sparkles className="w-4 h-4 mr-1" />
                  Load Example
                </Button>
              </div>
              <textarea
                value={robustnessInput}
                onChange={(e) => setRobustnessInput(e.target.value)}
                className={`w-full h-[300px] px-4 py-3 bg-slate-900/50 border ${
                  robustnessError ? "border-red-500" : "border-slate-700"
                } rounded-lg text-gray-300 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 resize-none`}
                placeholder="Paste malicious flow JSON here..."
                spellCheck={false}
              />
            </div>

            {robustnessError && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-start space-x-2 p-3 bg-red-500/10 border border-red-500/50 rounded-lg"
              >
                <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <p className="text-sm text-red-400">{robustnessError}</p>
              </motion.div>
            )}

            <Button
              onClick={handleRunRobustnessDemo}
              disabled={robustnessDemo.isPending || !robustnessInput.trim()}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white"
            >
              {robustnessDemo.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Running Demo...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Run Robustness Demo
                </>
              )}
            </Button>
          </div>

          {/* Info Panel */}
          <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              How It Works
            </h3>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-green-500/20 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                  <span className="text-xs font-bold text-green-400">1</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-white mb-1">
                    Control Test
                  </p>
                  <p className="text-xs text-gray-400">
                    Baseline model analyzes original malicious flow
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-red-500/20 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                  <span className="text-xs font-bold text-red-400">2</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-white mb-1">
                    FGSM Attack
                  </p>
                  <p className="text-xs text-gray-400">
                    Apply adversarial perturbations to evade detection
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-purple-500/20 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                  <span className="text-xs font-bold text-purple-400">3</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-white mb-1">
                    Robust Defense
                  </p>
                  <p className="text-xs text-gray-400">
                    Adversarially-trained model defeats the attack
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-6 p-4 bg-purple-500/10 border border-purple-500/20 rounded-lg">
              <p className="text-xs text-purple-300">
                <strong>Note:</strong> Use a known malicious network flow for
                best demonstration results. The demo will show how baseline
                models can be fooled but robust models remain resilient.
              </p>
            </div>
          </div>
        </div>

        {/* Results Table */}
        <AnimatePresence mode="wait">
          {robustnessDemo.data ? (
            <motion.div
              key="demo-results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {/* Results Cards */}
              <div className="space-y-3">
                {robustnessDemo.data.results.map((result, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`bg-slate-800/50 border ${getResultBadge(result)} rounded-lg p-4`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 flex-1">
                        {getResultIcon(result)}
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-1">
                            <span className="text-sm font-semibold text-white">
                              Step {index + 1}:
                            </span>
                            <span className="text-xs px-2 py-1 bg-slate-700 rounded text-gray-300">
                              {result.model_name}
                            </span>
                            <span className="text-xs px-2 py-1 bg-slate-700 rounded text-gray-300">
                              {result.input_type}
                            </span>
                          </div>
                          <p className="text-sm text-gray-400">
                            {index === 0 &&
                              "Control: Baseline correctly identifies original malicious flow"}
                            {index === 1 &&
                              "Attack: Baseline is fooled by adversarial perturbation (FGSM)"}
                            {index === 2 &&
                              "Defense: Robust model sees through the attack"}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p
                          className={`text-lg font-bold ${
                            result.predicted_label === "Malicious"
                              ? "text-red-400"
                              : "text-green-400"
                          }`}
                        >
                          {result.predicted_label}
                        </p>
                        <p className="text-xs text-gray-500">
                          {(result.confidence * 100).toFixed(2)}% confidence
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Technical Details */}
              {robustnessDemo.data.adversarial_sample_preview && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                  className="bg-slate-900/50 border border-slate-700 rounded-lg p-4"
                >
                  <h3 className="text-sm font-semibold text-gray-400 mb-2 flex items-center">
                    <FileJson className="w-4 h-4 mr-2" />
                    Adversarial Sample Preview
                  </h3>
                  <code className="text-xs text-gray-500 font-mono">
                    {robustnessDemo.data.adversarial_sample_preview}
                  </code>
                </motion.div>
              )}

              {/* Summary */}
              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-700">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-400">✓</p>
                  <p className="text-xs text-gray-400 mt-1">
                    Baseline (Control)
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-400">✗</p>
                  <p className="text-xs text-gray-400 mt-1">
                    Baseline (Attacked)
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-400">✓</p>
                  <p className="text-xs text-gray-400 mt-1">Robust Model</p>
                </div>
              </div>
            </motion.div>
          ) : robustnessDemo.error ? (
            <motion.div
              key="demo-error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-red-500/10 border border-red-500/50 rounded-lg p-6 text-center"
            >
              <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-red-400 mb-2">
                Demo Failed
              </h3>
              <p className="text-sm text-red-400/80">
                {robustnessDemo.error.message}
              </p>
            </motion.div>
          ) : (
            <motion.div
              key="demo-placeholder"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-slate-800/30 border border-slate-700 rounded-lg p-12 text-center"
            >
              <Shield className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-400 mb-2">
                Robustness Test Ready
              </h3>
              <p className="text-sm text-gray-500">
                Click &quot;Run Demo&quot; to see how our model defends against
                adversarial attacks
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
