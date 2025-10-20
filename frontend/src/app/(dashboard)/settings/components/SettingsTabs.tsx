"use client";

import { motion } from "framer-motion";

interface Tab {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface SettingsTabsProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  tabs: Tab[];
  children: React.ReactNode;
}

export function SettingsTabs({
  activeTab,
  onTabChange,
  tabs,
  children,
}: SettingsTabsProps) {
  return (
    <div className="mt-8 flex flex-col lg:flex-row gap-6">
      {/* Sidebar Tabs */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="lg:w-64 space-y-2"
      >
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                activeTab === tab.id
                  ? "bg-blue-500/20 border border-blue-500/50 text-blue-400"
                  : "bg-slate-800/50 border border-slate-700 text-gray-400 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{tab.label}</span>
            </button>
          );
        })}
      </motion.div>

      {/* Content Area */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="flex-1"
      >
        {children}
      </motion.div>
    </div>
  );
}
