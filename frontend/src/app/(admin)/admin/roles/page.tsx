"use client";

import React from "react";
import { motion } from "framer-motion";
import { Shield, Users, Plus, Edit, Trash2, Lock, Unlock } from "lucide-react";

export default function RolesPage() {
  // Mock roles data - replace with actual API call
  const roles = [
    {
      id: 1,
      name: "Admin",
      description: "Full system access with all permissions",
      userCount: 3,
      permissions: [
        "user_management",
        "role_management",
        "system_config",
        "audit_logs",
        "network_monitoring",
        "threat_intelligence",
      ],
      color: "emerald",
    },
    {
      id: 2,
      name: "Security Analyst",
      description: "Monitor threats and manage security alerts",
      userCount: 8,
      permissions: [
        "view_alerts",
        "manage_alerts",
        "threat_intelligence",
        "network_monitoring",
        "generate_reports",
      ],
      color: "blue",
    },
    {
      id: 3,
      name: "Network Engineer",
      description: "Manage network configuration and monitoring",
      userCount: 5,
      permissions: [
        "network_monitoring",
        "network_config",
        "view_alerts",
        "generate_reports",
      ],
      color: "purple",
    },
    {
      id: 4,
      name: "Viewer",
      description: "Read-only access to dashboards and reports",
      userCount: 12,
      permissions: ["view_dashboard", "view_reports"],
      color: "gray",
    },
  ];

  const permissionsList = [
    { id: "user_management", name: "User Management", category: "Admin" },
    { id: "role_management", name: "Role Management", category: "Admin" },
    { id: "system_config", name: "System Configuration", category: "Admin" },
    { id: "audit_logs", name: "Audit Logs", category: "Admin" },
    {
      id: "network_monitoring",
      name: "Network Monitoring",
      category: "Network",
    },
    {
      id: "network_config",
      name: "Network Configuration",
      category: "Network",
    },
    {
      id: "threat_intelligence",
      name: "Threat Intelligence",
      category: "Security",
    },
    { id: "view_alerts", name: "View Alerts", category: "Security" },
    { id: "manage_alerts", name: "Manage Alerts", category: "Security" },
    { id: "view_dashboard", name: "View Dashboard", category: "General" },
    { id: "view_reports", name: "View Reports", category: "General" },
    { id: "generate_reports", name: "Generate Reports", category: "General" },
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, string> = {
      emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
      blue: "text-blue-400 bg-blue-500/10 border-blue-500/20",
      purple: "text-purple-400 bg-purple-500/10 border-purple-500/20",
      gray: "text-gray-400 bg-gray-500/10 border-gray-500/20",
    };
    return colors[color] || colors.gray;
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
              Roles & Permissions
            </h1>
            <p className="text-gray-400 mt-2">
              Manage user roles and access permissions
            </p>
          </div>
          <button className="flex items-center space-x-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors">
            <Plus className="w-5 h-5" />
            <span>Create Role</span>
          </button>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {roles.map((role, index) => (
          <motion.div
            key={role.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className={`bg-slate-800/50 border ${getColorClasses(
              role.color,
            )} rounded-xl p-6`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 bg-${role.color}-500/10 rounded-lg`}>
                <Shield className={`w-6 h-6 text-${role.color}-400`} />
              </div>
            </div>
            <h3 className="text-xl font-bold text-white mb-1">{role.name}</h3>
            <p className="text-sm text-gray-400 mb-3">{role.userCount} users</p>
          </motion.div>
        ))}
      </div>

      {/* Roles List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="space-y-4"
      >
        {roles.map((role) => (
          <div
            key={role.id}
            className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-emerald-500/30 transition-colors"
          >
            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
              {/* Role Info */}
              <div className="flex-1">
                <div className="flex items-start space-x-4">
                  <div className="mt-1">
                    <div
                      className={`w-12 h-12 rounded-lg ${getColorClasses(
                        role.color,
                      )} flex items-center justify-center`}
                    >
                      <Shield className="w-6 h-6" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-1">
                      {role.name}
                    </h3>
                    <p className="text-gray-400 mb-3">{role.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-400 mb-4">
                      <div className="flex items-center space-x-2">
                        <Users className="w-4 h-4" />
                        <span>{role.userCount} users</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Lock className="w-4 h-4" />
                        <span>{role.permissions.length} permissions</span>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {role.permissions.map((perm) => {
                        const permission = permissionsList.find(
                          (p) => p.id === perm,
                        );
                        return (
                          <span
                            key={perm}
                            className="px-3 py-1 bg-slate-900/50 text-gray-300 text-xs rounded-full border border-slate-700"
                          >
                            {permission?.name || perm}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                <button className="p-2 hover:bg-slate-700 rounded-lg transition-colors group">
                  <Edit className="w-5 h-5 text-gray-400 group-hover:text-emerald-400" />
                </button>
                <button className="p-2 hover:bg-slate-700 rounded-lg transition-colors group">
                  <Trash2 className="w-5 h-5 text-gray-400 group-hover:text-red-400" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </motion.div>

      {/* All Permissions Reference */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <Unlock className="w-5 h-5 text-emerald-400" />
          <h2 className="text-xl font-bold text-white">
            Available Permissions
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {["Admin", "Network", "Security", "General"].map((category) => (
            <div key={category} className="space-y-2">
              <h4 className="text-sm font-semibold text-emerald-400">
                {category}
              </h4>
              <div className="space-y-2">
                {permissionsList
                  .filter((p) => p.category === category)
                  .map((permission) => (
                    <div
                      key={permission.id}
                      className="flex items-center space-x-2 p-2 bg-slate-900/50 rounded text-sm text-gray-300"
                    >
                      <Lock className="w-4 h-4 text-gray-500" />
                      <span>{permission.name}</span>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
