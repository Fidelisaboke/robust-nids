import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { Info } from "lucide-react";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

interface FeatureContribution {
  feature: string;
  value: number;
  shap_value: number;
}

interface ExplanationResponse {
  status: string;
  base_value: number;
  contributions: FeatureContribution[];
}

interface ShapExplanationChartProps {
  explanation: ExplanationResponse;
}

export const ShapExplanationChart: React.FC<ShapExplanationChartProps> = ({
  explanation,
}) => {
  // Sort contributions by absolute SHAP value for better visualization
  const sortedContributions = [...explanation.contributions].sort(
    (a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value),
  );

  // Take top features (up to 15) for clarity
  const maxFeatures = Math.min(15, sortedContributions.length);
  const topContributions = sortedContributions.slice(0, maxFeatures);

  const chartData = {
    labels: topContributions.map((c) => c.feature),
    datasets: [
      {
        label: "SHAP Impact",
        data: topContributions.map((c) => c.shap_value),
        backgroundColor: topContributions.map(
          (c) =>
            c.shap_value > 0
              ? "rgba(239, 68, 68, 0.8)" // Red for positive (malicious)
              : "rgba(34, 197, 94, 0.8)", // Green for negative (benign)
        ),
        borderColor: topContributions.map((c) =>
          c.shap_value > 0 ? "rgba(239, 68, 68, 1)" : "rgba(34, 197, 94, 1)",
        ),
        borderWidth: 1,
      },
    ],
  };

  const options: ChartOptions<"bar"> = {
    indexAxis: "y" as const,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
      tooltip: {
        backgroundColor: "rgba(15, 23, 42, 0.95)",
        titleColor: "rgb(226, 232, 240)",
        bodyColor: "rgb(203, 213, 225)",
        borderColor: "rgb(71, 85, 105)",
        borderWidth: 1,
        padding: 12,
        displayColors: false,
        callbacks: {
          title: (context) => {
            if (!context || context.length === 0) return "Unknown";
            const index = context[0].dataIndex;
            return topContributions[index]?.feature || "Unknown feature";
          },
          label: (context) => {
            const index = context.dataIndex;
            const contribution = topContributions[index];
            if (!contribution) return ["No data available"];
            return [
              `SHAP Value: ${contribution.shap_value.toFixed(4)}`,
              `Feature Value: ${contribution.value}`,
              `Impact: ${contribution.shap_value > 0 ? "Towards Malicious" : "Towards Benign"}`,
            ];
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          color: "rgba(71, 85, 105, 0.3)",
        },
        ticks: {
          color: "rgb(148, 163, 184)",
          font: {
            size: 11,
          },
        },
        title: {
          display: true,
          text: "SHAP Value (Impact on Prediction)",
          color: "rgb(203, 213, 225)",
          font: {
            size: 12,
            weight: "bold",
          },
        },
      },
      y: {
        grid: {
          display: false,
        },
        ticks: {
          color: "rgb(148, 163, 184)",
          font: {
            size: 11,
          },
          autoSkip: false,
        },
      },
    },
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-xl p-6 space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-xl font-bold text-white mb-1">
            SHAP Feature Attribution
          </h3>
          <p className="text-sm text-gray-400">
            Top features influencing the prediction decision
          </p>
        </div>
        <div className="flex items-center space-x-2 px-3 py-1.5 bg-slate-900/50 rounded-lg border border-slate-700">
          <Info className="w-4 h-4 text-blue-400" />
          <span className="text-xs text-gray-400">
            Base: {explanation.base_value.toFixed(4)}
          </span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center space-x-6 pb-2">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-red-500 rounded" />
          <span className="text-xs text-gray-400">Towards Malicious</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-green-500 rounded" />
          <span className="text-xs text-gray-400">Towards Benign</span>
        </div>
      </div>

      {/* Chart Container */}
      <div className="h-[600px] bg-slate-900/30 rounded-lg p-4">
        <Bar data={chartData} options={options} />
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-700">
        <div className="text-center">
          <p className="text-sm text-gray-400 mb-1">Total Features</p>
          <p className="text-2xl font-bold text-white">
            {explanation.contributions.length}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-400 mb-1">Positive Impact</p>
          <p className="text-2xl font-bold text-red-400">
            {explanation.contributions.filter((c) => c.shap_value > 0).length}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-400 mb-1">Negative Impact</p>
          <p className="text-2xl font-bold text-green-400">
            {explanation.contributions.filter((c) => c.shap_value < 0).length}
          </p>
        </div>
      </div>
    </div>
  );
};
