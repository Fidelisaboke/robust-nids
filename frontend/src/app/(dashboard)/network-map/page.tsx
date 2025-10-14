"use client";

import { motion } from "framer-motion";
import { Server, Globe, AlertCircle } from "lucide-react";

export default function NetworkMapPage() {
  const nodes = [
    { id: 1, name: "Gateway", type: "gateway", x: 50, y: 20, status: "online" },
    {
      id: 2,
      name: "Firewall",
      type: "security",
      x: 50,
      y: 40,
      status: "online",
    },
    {
      id: 3,
      name: "Web Server",
      type: "server",
      x: 30,
      y: 60,
      status: "online",
    },
    {
      id: 4,
      name: "Database",
      type: "database",
      x: 50,
      y: 80,
      status: "online",
    },
    {
      id: 5,
      name: "API Server",
      type: "server",
      x: 70,
      y: 60,
      status: "warning",
    },
  ];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-white">Network Topology</h1>
        <p className="text-gray-400 mt-2">
          Visual representation of your network infrastructure
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 relative h-[600px]"
      >
        <svg className="w-full h-full">
          {/* Connections */}
          <line
            x1="50%"
            y1="20%"
            x2="50%"
            y2="40%"
            stroke="#3b82f6"
            strokeWidth="2"
          />
          <line
            x1="50%"
            y1="40%"
            x2="30%"
            y2="60%"
            stroke="#3b82f6"
            strokeWidth="2"
          />
          <line
            x1="50%"
            y1="40%"
            x2="70%"
            y2="60%"
            stroke="#f59e0b"
            strokeWidth="2"
          />
          <line
            x1="30%"
            y1="60%"
            x2="50%"
            y2="80%"
            stroke="#3b82f6"
            strokeWidth="2"
          />
        </svg>

        {nodes.map((node, index) => (
          <motion.div
            key={node.id}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 + 0.3 }}
            className="absolute transform -translate-x-1/2 -translate-y-1/2"
            style={{ left: `${node.x}%`, top: `${node.y}%` }}
          >
            <div
              className={`p-4 rounded-xl border-2 ${node.status === "online" ? "border-green-500 bg-green-500/10" : "border-yellow-500 bg-yellow-500/10"}`}
            >
              <div className="flex flex-col items-center space-y-2">
                {node.type === "gateway" && (
                  <Globe className="w-6 h-6 text-blue-400" />
                )}
                {node.type === "security" && (
                  <AlertCircle className="w-6 h-6 text-purple-400" />
                )}
                {node.type === "server" && (
                  <Server className="w-6 h-6 text-cyan-400" />
                )}
                {node.type === "database" && (
                  <Server className="w-6 h-6 text-green-400" />
                )}
                <span className="text-xs font-medium text-white whitespace-nowrap">
                  {node.name}
                </span>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
