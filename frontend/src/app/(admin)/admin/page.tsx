"use client";

import React, { useMemo } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  Users,
  UserCheck,
  Clock,
  Shield,
  Activity,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  FileText,
  Settings,
  BarChart3,
} from "lucide-react";
import {
  useUsers,
  usePendingRegistrations,
  useAuditLogs,
} from "@/hooks/useUserManagement";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { useAuth } from "@/contexts/AuthContext";
import { getRecentUsers } from "@/lib/utils";

export default function AdminDashboardPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { data: usersData } = useUsers({ size: 100 });
  const { data: pendingData } = usePendingRegistrations(1, 10);
  const { data: auditData } = useAuditLogs(1, 10);

  const recentUsers = useMemo(
    () => getRecentUsers(usersData?.items, 7),
    [usersData],
  );

  const stats = [
    {
      name: "Total Users",
      value: usersData?.total || 0,
      change: recentUsers.length || 0,
      changeText: "new this week",
      changeType: "increase",
      icon: Users,
      color: "text-emerald-400",
      bgColor: "bg-emerald-500/10",
      borderColor: "border-emerald-500/20",
      href: "/admin/users",
    },
    {
      name: "Active Users",
      value: usersData?.items?.filter((u) => u.is_active).length || 0,
      change: Math.round(
        ((usersData?.items?.filter((u) => u.is_active).length || 0) /
          (usersData?.total || 1)) *
          100,
      ),
      changeText: "% of total",
      changeType: "neutral",
      icon: UserCheck,
      color: "text-blue-400",
      bgColor: "bg-blue-500/10",
      borderColor: "border-blue-500/20",
      href: "/admin/users",
    },
    {
      name: "Pending Requests",
      value: pendingData?.total || 0,
      change: pendingData?.total || 0,
      changeText: "awaiting review",
      changeType:
        pendingData?.total !== undefined && pendingData.total > 0
          ? "alert"
          : "neutral",
      icon: Clock,
      color: "text-orange-400",
      bgColor: "bg-orange-500/10",
      borderColor: "border-orange-500/20",
      href: "/admin/users/pending",
    },
    {
      name: "Admin Actions",
      value: auditData?.total || 0,
      change: auditData?.logs?.length || 0,
      changeText: "recent actions",
      changeType: "neutral",
      icon: Shield,
      color: "text-purple-400",
      bgColor: "bg-purple-500/10",
      borderColor: "border-purple-500/20",
      href: "/admin/audit-logs",
    },
  ];

  const quickActions = [
    {
      title: "User Management",
      description: "View and manage all system users",
      icon: Users,
      color: "emerald",
      href: "/admin/users",
    },
    {
      title: "Pending Approvals",
      description: "Review new registration requests",
      icon: Clock,
      color: "orange",
      href: "/admin/users/pending",
      badge: pendingData?.total || 0,
    },
    {
      title: "Roles & Permissions",
      description: "Manage user roles and access control",
      icon: Shield,
      color: "blue",
      href: "/admin/roles",
    },
    {
      title: "Audit Logs",
      description: "Track administrative actions",
      icon: FileText,
      color: "purple",
      href: "/admin/audit-logs",
    },
    {
      title: "System Config",
      description: "Configure system settings",
      icon: Settings,
      color: "gray",
      href: "/admin/system-config",
    },
    {
      title: "Analytics",
      description: "View system analytics and reports",
      icon: BarChart3,
      color: "teal",
      href: "/admin/users",
    },
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, { text: string; bg: string; border: string }> =
      {
        emerald: {
          text: "text-emerald-400",
          bg: "bg-emerald-500/10",
          border: "border-emerald-500/20",
        },
        blue: {
          text: "text-blue-400",
          bg: "bg-blue-500/10",
          border: "border-blue-500/20",
        },
        orange: {
          text: "text-orange-400",
          bg: "bg-orange-500/10",
          border: "border-orange-500/20",
        },
        purple: {
          text: "text-purple-400",
          bg: "bg-purple-500/10",
          border: "border-purple-500/20",
        },
        gray: {
          text: "text-gray-400",
          bg: "bg-gray-500/10",
          border: "border-gray-500/20",
        },
        teal: {
          text: "text-teal-400",
          bg: "bg-teal-500/10",
          border: "border-teal-500/20",
        },
      };
    return colors[color] || colors.gray;
  };

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white">
              Welcome back, {user?.first_name || "Admin"}!
            </h1>
            <p className="text-gray-400 mt-2">
              Here&apos;s an overview of your system administration dashboard.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="flex items-center space-x-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors border border-slate-700"
            >
              <Activity className="w-5 h-5" />
              <span>Main Dashboard</span>
            </Link>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              onClick={() => router.push(stat.href)}
              className={`bg-slate-800/50 border ${stat.borderColor} rounded-xl p-6 hover:scale-105 hover:border-emerald-500/50 transition-all cursor-pointer`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 ${stat.bgColor} rounded-lg`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                {stat.changeType === "increase" && (
                  <TrendingUp className="w-5 h-5 text-emerald-400" />
                )}
                {stat.changeType === "decrease" && (
                  <TrendingDown className="w-5 h-5 text-red-400" />
                )}
                {stat.changeType === "alert" && stat.change > 0 && (
                  <AlertTriangle className="w-5 h-5 text-orange-400" />
                )}
              </div>
              <h3 className="text-3xl font-bold text-white mb-1">
                {stat.value}
              </h3>
              <p className="text-sm text-gray-400">{stat.name}</p>
              <div className="mt-2 flex items-center space-x-2">
                <span
                  className={`text-xs font-semibold ${
                    stat.changeType === "increase"
                      ? "text-emerald-400"
                      : stat.changeType === "alert"
                        ? "text-orange-400"
                        : "text-gray-400"
                  }`}
                >
                  {stat.change}
                </span>
                <span className="text-xs text-gray-500">{stat.changeText}</span>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            const colorClasses = getColorClasses(action.color);
            return (
              <motion.div
                key={action.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5 + index * 0.05 }}
              >
                <Link
                  href={action.href}
                  className={`block bg-slate-800/50 border ${colorClasses.border} rounded-xl p-6 hover:bg-slate-800 hover:border-emerald-500/50 transition-all group`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 ${colorClasses.bg} rounded-lg`}>
                      <Icon className={`w-6 h-6 ${colorClasses.text}`} />
                    </div>
                    {action.badge !== undefined && action.badge > 0 && (
                      <span className="px-2.5 py-1 bg-orange-500/20 text-orange-400 text-xs font-semibold rounded-full border border-orange-500/30">
                        {action.badge}
                      </span>
                    )}
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-emerald-400 transition-colors">
                    {action.title}
                  </h3>
                  <p className="text-sm text-gray-400 mb-4">
                    {action.description}
                  </p>
                  <div className="flex items-center space-x-2 text-sm text-emerald-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span>View</span>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </Link>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Recent Activity Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Users */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white">Recent Users</h2>
            <Link
              href="/admin/users"
              className="text-sm text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              View All
            </Link>
          </div>
          <div className="space-y-3">
            {recentUsers && recentUsers.length > 0 ? (
              recentUsers.slice(0, 5).map((recentUser) => (
                <div
                  key={recentUser.id}
                  onClick={() => router.push(`/admin/users/${recentUser.id}`)}
                  className="flex items-center space-x-3 p-3 bg-slate-900/50 rounded-lg hover:bg-slate-900 transition-colors cursor-pointer"
                >
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white font-semibold">
                    {recentUser.first_name?.[0]}
                    {recentUser.last_name?.[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">
                      {recentUser.first_name} {recentUser.last_name}
                    </p>
                    <p className="text-xs text-gray-400 truncate">
                      {recentUser.email}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-emerald-400 font-medium">New</p>
                    <p className="text-xs text-gray-500">
                      {formatDistanceToNow(new Date(recentUser.created_at), {
                        addSuffix: true,
                      })}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-center text-gray-400 py-8">No recent users</p>
            )}
          </div>
        </motion.div>

        {/* Recent Admin Actions */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.9 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white">Recent Actions</h2>
            <Link
              href="/admin/audit-logs"
              className="text-sm text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              View All
            </Link>
          </div>
          <div className="space-y-3">
            {auditData && auditData.logs.length > 0 ? (
              auditData.logs.slice(0, 5).map((log) => {
                const getActionColor = (action: string) => {
                  if (action.includes("delete") || action.includes("reject")) {
                    return "text-red-400 bg-red-500/10";
                  } else if (
                    action.includes("approve") ||
                    action.includes("activate")
                  ) {
                    return "text-emerald-400 bg-emerald-500/10";
                  } else if (action.includes("deactivate")) {
                    return "text-orange-400 bg-orange-500/10";
                  } else {
                    return "text-blue-400 bg-blue-500/10";
                  }
                };

                return (
                  <div
                    key={log.id}
                    className="p-3 bg-slate-900/50 rounded-lg hover:bg-slate-900 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${getActionColor(
                          log.action,
                        )}`}
                      >
                        {log.action}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatDistanceToNow(new Date(log.timestamp), {
                          addSuffix: true,
                        })}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400">
                      by <span className="text-white">{log.admin_email}</span>
                    </p>
                  </div>
                );
              })
            ) : (
              <p className="text-center text-gray-400 py-8">
                No recent actions
              </p>
            )}
          </div>
        </motion.div>
      </div>

      {/* System Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <Activity className="w-5 h-5 text-emerald-400" />
          <h2 className="text-xl font-bold text-white">System Overview</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-4 bg-slate-900/50 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">User Verification</span>
              <span className="text-sm font-semibold text-emerald-400">
                {Math.round(
                  ((usersData?.items?.filter((u) => u.email_verified).length ||
                    0) /
                    (usersData?.total || 1)) *
                    100,
                )}
                %
              </span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all"
                style={{
                  width: `${Math.round(
                    ((usersData?.items?.filter((u) => u.email_verified)
                      .length || 0) /
                      (usersData?.total || 1)) *
                      100,
                  )}%`,
                }}
              />
            </div>
          </div>
          <div className="p-4 bg-slate-900/50 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">MFA Adoption</span>
              <span className="text-sm font-semibold text-blue-400">
                {Math.round(
                  ((usersData?.items?.filter((u) => u.mfa_enabled).length ||
                    0) /
                    (usersData?.total || 1)) *
                    100,
                )}
                %
              </span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all"
                style={{
                  width: `${Math.round(
                    ((usersData?.items?.filter((u) => u.mfa_enabled).length ||
                      0) /
                      (usersData?.total || 1)) *
                      100,
                  )}%`,
                }}
              />
            </div>
          </div>
          <div className="p-4 bg-slate-900/50 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">Active Users</span>
              <span className="text-sm font-semibold text-purple-400">
                {Math.round(
                  ((usersData?.items?.filter((u) => u.is_active).length || 0) /
                    (usersData?.total || 1)) *
                    100,
                )}
                %
              </span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all"
                style={{
                  width: `${Math.round(
                    ((usersData?.items?.filter((u) => u.is_active).length ||
                      0) /
                      (usersData?.total || 1)) *
                      100,
                  )}%`,
                }}
              />
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
