"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Save,
  RotateCcw,
  Server,
  Shield,
  Bell,
  Mail,
  Database,
  AlertTriangle,
} from "lucide-react";
import { toast } from "sonner";

export default function SystemConfigPage() {
  const [hasChanges, setHasChanges] = useState(false);

  // Mock configuration state
  const [config, setConfig] = useState({
    // System Settings
    systemName: "NIDS - Network Intrusion Detection System",
    maintenanceMode: false,
    sessionTimeout: 30,
    maxLoginAttempts: 5,

    // Security Settings
    passwordMinLength: 12,
    requireMfa: false,
    passwordExpiry: 90,

    // Alert Settings
    alertRetention: 365,
    criticalAlertNotify: true,
    alertThreshold: 10,

    // Email Settings
    smtpHost: "smtp.example.com",
    smtpPort: 587,
    smtpSender: "nids@example.com",

    // Database Settings
    backupFrequency: "daily",
    retentionPeriod: 90,
  });

  const handleSave = () => {
    // Implement save logic here
    toast.success("Configuration saved successfully");
    setHasChanges(false);
  };

  const handleReset = () => {
    // Implement reset logic here
    toast.info("Configuration reset to defaults");
    setHasChanges(false);
  };

  const handleChange = (field: string, value: unknown) => {
    setConfig((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white">
              System Configuration
            </h1>
            <p className="text-gray-400 mt-2">
              Manage system-wide settings and preferences
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleReset}
              disabled={!hasChanges}
              className="flex items-center space-x-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-900 disabled:cursor-not-allowed text-white rounded-lg transition-colors border border-slate-700"
            >
              <RotateCcw className="w-5 h-5" />
              <span>Reset</span>
            </button>
            <button
              onClick={handleSave}
              disabled={!hasChanges}
              className="flex items-center space-x-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              <Save className="w-5 h-5" />
              <span>Save Changes</span>
            </button>
          </div>
        </div>
      </motion.div>

      {/* Unsaved Changes Banner */}
      {hasChanges && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-4"
        >
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-5 h-5 text-orange-400" />
            <p className="text-orange-400">
              You have unsaved changes. Don&apost;t forget to save your
              configuration.
            </p>
          </div>
        </motion.div>
      )}

      {/* System Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <Server className="w-5 h-5 text-emerald-400" />
          <h2 className="text-xl font-bold text-white">System Settings</h2>
        </div>
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              System Name
            </label>
            <input
              type="text"
              value={config.systemName}
              onChange={(e) => handleChange("systemName", e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
            <div>
              <p className="text-white font-medium">Maintenance Mode</p>
              <p className="text-sm text-gray-400">
                Temporarily disable system access for maintenance
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={config.maintenanceMode}
                onChange={(e) =>
                  handleChange("maintenanceMode", e.target.checked)
                }
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-800 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
            </label>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Session Timeout (minutes)
              </label>
              <input
                type="number"
                value={config.sessionTimeout}
                onChange={(e) =>
                  handleChange("sessionTimeout", parseInt(e.target.value))
                }
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Max Login Attempts
              </label>
              <input
                type="number"
                value={config.maxLoginAttempts}
                onChange={(e) =>
                  handleChange("maxLoginAttempts", parseInt(e.target.value))
                }
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Security Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <Shield className="w-5 h-5 text-emerald-400" />
          <h2 className="text-xl font-bold text-white">Security Settings</h2>
        </div>
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Minimum Password Length
              </label>
              <input
                type="number"
                value={config.passwordMinLength}
                onChange={(e) =>
                  handleChange("passwordMinLength", parseInt(e.target.value))
                }
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Password Expiry (days)
              </label>
              <input
                type="number"
                value={config.passwordExpiry}
                onChange={(e) =>
                  handleChange("passwordExpiry", parseInt(e.target.value))
                }
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
            <div>
              <p className="text-white font-medium">
                Require MFA for All Users
              </p>
              <p className="text-sm text-gray-400">
                Force multi-factor authentication for enhanced security
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={config.requireMfa}
                onChange={(e) => handleChange("requireMfa", e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-800 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
            </label>
          </div>
        </div>
      </motion.div>

      {/* Alert Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <Bell className="w-5 h-5 text-emerald-400" />
          <h2 className="text-xl font-bold text-white">Alert Settings</h2>
        </div>
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Alert Retention (days)
              </label>
              <input
                type="number"
                value={config.alertRetention}
                onChange={(e) =>
                  handleChange("alertRetention", parseInt(e.target.value))
                }
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Alert Threshold (per hour)
              </label>
              <input
                type="number"
                value={config.alertThreshold}
                onChange={(e) =>
                  handleChange("alertThreshold", parseInt(e.target.value))
                }
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
            <div>
              <p className="text-white font-medium">
                Critical Alert Notifications
              </p>
              <p className="text-sm text-gray-400">
                Send immediate notifications for critical alerts
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={config.criticalAlertNotify}
                onChange={(e) =>
                  handleChange("criticalAlertNotify", e.target.checked)
                }
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-800 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
            </label>
          </div>
        </div>
      </motion.div>

      {/* Email Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <Mail className="w-5 h-5 text-emerald-400" />
          <h2 className="text-xl font-bold text-white">Email Settings</h2>
        </div>
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                SMTP Host
              </label>
              <input
                type="text"
                value={config.smtpHost}
                onChange={(e) => handleChange("smtpHost", e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                SMTP Port
              </label>
              <input
                type="number"
                value={config.smtpPort}
                onChange={(e) =>
                  handleChange("smtpPort", parseInt(e.target.value))
                }
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Sender Email Address
            </label>
            <input
              type="email"
              value={config.smtpSender}
              onChange={(e) => handleChange("smtpSender", e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>
      </motion.div>

      {/* Database Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <Database className="w-5 h-5 text-emerald-400" />
          <h2 className="text-xl font-bold text-white">Database Settings</h2>
        </div>
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Backup Frequency
              </label>
              <select
                value={config.backupFrequency}
                onChange={(e) =>
                  handleChange("backupFrequency", e.target.value)
                }
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="hourly">Hourly</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Retention Period (days)
              </label>
              <input
                type="number"
                value={config.retentionPeriod}
                onChange={(e) =>
                  handleChange("retentionPeriod", parseInt(e.target.value))
                }
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
