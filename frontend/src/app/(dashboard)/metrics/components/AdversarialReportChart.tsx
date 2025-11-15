"use client";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { AdversarialMetric } from "@/hooks/useNids";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

// Define chart colors
const CHART_COLORS = {
  baseline: "#3b82f6", // Blue
  attacked: "#ef4444", // Red
  robust: "#22c55e", // Green
};

interface AdversarialReportChartProps {
  chartData: AdversarialMetric[];
}

export const AdversarialReportChart: React.FC<AdversarialReportChartProps> = ({
  chartData,
}) => {
  const data = {
    labels: chartData.map((d) => d.model),
    datasets: [
      {
        label: "Model Accuracy",
        data: chartData.map((d) => d.accuracy * 100), // Convert to %
        // Assign color based on model name
        backgroundColor: chartData.map((d) =>
          d.model.includes("Attacked)")
            ? d.model.includes("Baseline")
              ? CHART_COLORS.attacked
              : CHART_COLORS.robust
            : CHART_COLORS.baseline,
        ),
        borderRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false, // We use colors, no legend needed
      },
      tooltip: {
        enabled: true,
        mode: "index" as const,
        intersect: false,
        backgroundColor: "rgb(15 23 42 / 0.9)", // slate-900
        borderColor: "rgb(51 65 85)", // slate-700
        borderWidth: 1,
        titleFont: {
          size: 14,
          weight: "bold" as const,
        },
        bodyFont: {
          size: 12,
        },
        callbacks: {
          label: (context: import("chart.js").TooltipItem<"bar">) => {
            return `Accuracy: ${(context.raw as number).toFixed(2)}%`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false, // Cleaner look
        },
        ticks: {
          color: "rgb(100 116 139)", // slate-500
          font: {
            size: 12,
          },
        },
      },
      y: {
        beginAtZero: true,
        max: 105, // Give 5% padding at top
        grid: {
          color: "rgb(51 65 85)", // slate-700
        },
        ticks: {
          color: "rgb(100 116 139)", // slate-500
          font: {
            size: 12,
          },
          callback: (value: string | number) => `${value}%`, // Add % sign
        },
      },
    },
  };

  return <Bar options={options} data={data} />;
};
