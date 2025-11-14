"use client";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler, // Import Filler for area charts
  TimeScale,
} from "chart.js";
import { Line } from "react-chartjs-2";

// Register all necessary components for Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale,
);

interface AlertsTimeChartProps {
  chartData: {
    day: string;
    count: number;
  }[];
}

export const AlertsTimeChart: React.FC<AlertsTimeChartProps> = ({
  chartData,
}) => {
  const data = {
    labels: chartData.map((d) => d.day),
    datasets: [
      {
        label: "Alerts",
        data: chartData.map((d) => d.count),
        fill: true,
        backgroundColor: "rgba(56, 189, 248, 0.2)", // sky-500 with opacity
        borderColor: "rgb(56, 189, 248)", // sky-500
        pointBackgroundColor: "rgb(56, 189, 248)",
        pointBorderColor: "#fff",
        pointHoverBackgroundColor: "#fff",
        pointHoverBorderColor: "rgb(56, 189, 248)",
        tension: 0.3, // Makes the line smooth
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false, // Hide legend
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
          label: (context: import("chart.js").TooltipItem<"line">) => {
            return `Alerts: ${context.raw}`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          color: "rgb(51 65 85)", // slate-700
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
        grid: {
          color: "rgb(51 65 85)", // slate-700
        },
        ticks: {
          color: "rgb(100 116 139)", // slate-500
          font: {
            size: 12,
          },
          // Ensure only integers are shown on the Y-axis
          callback: function (value: string | number) {
            if (typeof value === "number" && value % 1 === 0) {
              return value;
            }
          },
        },
      },
    },
  };

  return <Line options={options} data={data} />;
};
