"use client";

import { ReactNode } from "react";
import { motion } from "framer-motion";

interface SettingsLayoutProps {
  children: ReactNode;
  title: string;
  description: string;
}

export function SettingsLayout({
  children,
  title,
  description,
}: SettingsLayoutProps) {
  return (
    <div className="max-w-7xl space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold text-white mb-2">{title}</h1>
        <p className="text-gray-400">{description}</p>
      </motion.div>
      {children}
    </div>
  );
}
