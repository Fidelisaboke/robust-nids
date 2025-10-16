"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Shield,
  Loader2,
  AlertCircle,
  CheckCircle,
  User,
  Bell,
  Lock,
} from "lucide-react";
import {
  useSetupMfaMutation,
  useCurrentUser,
  useDisableMfaMutation,
} from "@/hooks/useAuthMutations";
import { normalizeError } from "@/lib/api/apiClient";

export default function SettingsPage() {
  const router = useRouter();
  const { data: user, isLoading: userLoading } = useCurrentUser();
  const [activeTab, setActiveTab] = useState<
    "profile" | "security" | "notifications"
  >("security");

  const setupMfaMutation = useSetupMfaMutation();
  const disableMfaMutation = useDisableMfaMutation();

  const handleEnableMfa = async () => {
    try {
      router.push("/totp-setup");
    } catch (error) {
      console.error("Failed to setup MFA:", normalizeError(error));
    }
  };

  const handleDisableMfa = async () => {};

  const tabs = [
    { id: "profile" as const, label: "Profile", icon: User },
    { id: "security" as const, label: "Security", icon: Lock },
    { id: "notifications" as const, label: "Notifications", icon: Bell },
  ];

  if (userLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">
            Manage your account settings and preferences
          </p>
        </motion.div>

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
                  onClick={() => setActiveTab(tab.id)}
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
            {activeTab === "profile" && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 space-y-6">
                <h2 className="text-2xl font-bold text-white">
                  Profile Information
                </h2>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      value={user?.first_name || ""}
                      readOnly
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      value={user?.last_name || ""}
                      readOnly
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={user?.email || ""}
                      readOnly
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Username
                    </label>
                    <input
                      type="text"
                      value={user?.username || ""}
                      readOnly
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Department
                    </label>
                    <input
                      type="text"
                      value={user?.department || ""}
                      readOnly
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Job Title
                    </label>
                    <input
                      type="text"
                      value={user?.job_title || ""}
                      readOnly
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === "security" && (
              <div className="space-y-6">
                {/* MFA Section */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4">
                      <div className="p-3 bg-blue-500/10 rounded-lg">
                        <Shield className="w-6 h-6 text-blue-400" />
                      </div>

                      <div className="flex-1">
                        <h3 className="text-xl font-semibold text-white mb-2">
                          Two-Factor Authentication
                        </h3>
                        <p className="text-gray-400 mb-4">
                          Add an extra layer of security to your account by
                          requiring a code from your authenticator app.
                        </p>

                        {/* MFA Status */}
                        {user?.mfa_enabled ? (
                          <div className="space-y-3 mb-4">
                            <div className="flex items-center space-x-2">
                              <div className="w-2 h-2 rounded-full bg-emerald-400" />
                              <span className="text-sm text-emerald-400 font-medium">
                                Enabled
                              </span>
                            </div>

                            <div className="text-sm text-gray-400 space-y-1">
                              <p>
                                <span className="text-gray-300 font-medium">
                                  Method:
                                </span>{" "}
                                {user?.mfa_method?.toUpperCase() || "TOTP"}
                              </p>
                              {user?.mfa_configured_at && (
                                <p>
                                  <span className="text-gray-300 font-medium">
                                    Configured on:
                                  </span>{" "}
                                  {new Date(
                                    user?.mfa_configured_at,
                                  ).toLocaleString()}
                                </p>
                              )}
                            </div>

                            <button
                              onClick={handleDisableMfa}
                              disabled={disableMfaMutation.isPending}
                              className="px-6 py-2.5 bg-red-600/90 text-white font-medium rounded-lg hover:bg-red-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {disableMfaMutation.isPending ? (
                                <span className="flex items-center">
                                  <Loader2 className="animate-spin h-4 w-4 mr-2" />
                                  Disabling...
                                </span>
                              ) : (
                                "Disable MFA"
                              )}
                            </button>
                          </div>
                        ) : (
                          <>
                            <div className="flex items-center space-x-2 mb-4">
                              <div className="w-2 h-2 rounded-full bg-amber-400" />
                              <span className="text-sm text-gray-400">
                                Not Enabled
                              </span>
                            </div>

                            {setupMfaMutation.isError && (
                              <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 flex items-start space-x-2">
                                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                                <div className="flex-1">
                                  <p className="text-red-400 text-sm font-medium">
                                    Setup Failed
                                  </p>
                                  <p className="text-red-300 text-sm mt-1">
                                    {
                                      normalizeError(setupMfaMutation.error)
                                        .message
                                    }
                                  </p>
                                </div>
                              </div>
                            )}

                            <button
                              onClick={handleEnableMfa}
                              disabled={setupMfaMutation.isPending}
                              className="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {setupMfaMutation.isPending ? (
                                <span className="flex items-center">
                                  <Loader2 className="animate-spin h-4 w-4 mr-2" />
                                  Setting up...
                                </span>
                              ) : (
                                "Enable MFA"
                              )}
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Password Section */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                  <div className="flex items-start space-x-4">
                    <div className="p-3 bg-purple-500/10 rounded-lg">
                      <Lock className="w-6 h-6 text-purple-400" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-white mb-2">
                        Password
                      </h3>
                      <p className="text-gray-400 mb-4">
                        Change your password regularly to keep your account
                        secure.
                      </p>
                      <button className="px-6 py-2.5 bg-slate-700 hover:bg-slate-600 text-white font-medium rounded-lg transition-all">
                        Change Password
                      </button>
                    </div>
                  </div>
                </div>

                {/* Active Sessions */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                  <h3 className="text-xl font-semibold text-white mb-4">
                    Active Sessions
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
                      <div>
                        <p className="text-white font-medium">
                          Current Session
                        </p>
                        <p className="text-sm text-gray-400">
                          {user?.last_login
                            ? new Date(user.last_login).toLocaleString()
                            : "Unknown"}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-5 h-5 text-green-400" />
                        <span className="text-sm text-green-400">Active</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "notifications" && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 space-y-6">
                <h2 className="text-2xl font-bold text-white">
                  Notification Preferences
                </h2>

                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
                    <div>
                      <p className="text-white font-medium">
                        Email Notifications
                      </p>
                      <p className="text-sm text-gray-400">
                        Receive alerts via email
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={user?.preferences?.notifications?.email}
                        readOnly
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
                    <div>
                      <p className="text-white font-medium">
                        Browser Notifications
                      </p>
                      <p className="text-sm text-gray-400">
                        Get push notifications in your browser
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={user?.preferences?.notifications?.browser}
                        readOnly
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
                    <div>
                      <p className="text-white font-medium">Critical Alerts</p>
                      <p className="text-sm text-gray-400">
                        High-priority security alerts
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={
                          user?.preferences?.notifications?.critical_alerts
                        }
                        readOnly
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
