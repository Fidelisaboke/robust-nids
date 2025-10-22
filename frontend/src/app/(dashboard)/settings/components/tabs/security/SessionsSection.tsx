"use client";

import {
  CheckCircle,
  AlertCircle,
  Monitor,
  MapPin,
  Calendar,
} from "lucide-react";
import { User } from "@/types/auth";

const DEFAULT_LOCATION = "Unknown";

interface SessionsSectionProps {
  user: User | undefined;
}

export function SessionsSection({ user }: SessionsSectionProps) {
  const formatLastLogin = (lastLogin: string | null) => {
    if (!lastLogin) return "Never logged in";

    const date = new Date(lastLogin);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return "Yesterday";
    if (diffDays <= 7) return `${diffDays} days ago`;

    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getSessionStatus = (lastLogin: string | null) => {
    if (!lastLogin)
      return { status: "inactive", label: "Inactive", color: "text-gray-400" };

    const date = new Date(lastLogin);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffMinutes = Math.ceil(diffTime / (1000 * 60));

    if (diffMinutes <= 5)
      return { status: "active", label: "Active", color: "text-green-400" };
    if (diffMinutes <= 60)
      return { status: "recent", label: "Recent", color: "text-amber-400" };

    return { status: "inactive", label: "Inactive", color: "text-gray-400" };
  };

  const sessionStatus = getSessionStatus(user?.last_login || null);

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
      <h3 className="text-xl font-semibold text-white mb-4">Active Sessions</h3>

      <div className="space-y-4">
        {/* Current Session */}
        <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-4 flex-1">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Monitor className="w-5 h-5 text-blue-400" />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-2">
                  <p className="text-white font-medium truncate">
                    Current Session
                  </p>
                  <div
                    className={`flex items-center space-x-1 ${sessionStatus.color}`}
                  >
                    {sessionStatus.status === "active" ? (
                      <CheckCircle className="w-4 h-4" />
                    ) : (
                      <AlertCircle className="w-4 h-4" />
                    )}
                    <span className="text-sm font-medium">
                      {sessionStatus.label}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center space-x-2 text-gray-400">
                    <Calendar className="w-4 h-4" />
                    <span>
                      Last activity: {formatLastLogin(user?.last_login || null)}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2 text-gray-400">
                    <MapPin className="w-4 h-4" />
                    <span className="truncate">
                      Location: {DEFAULT_LOCATION}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Session Information */}
        <div className="bg-slate-900/30 border border-slate-600 rounded-lg p-4">
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-300 mb-2">
              Session Information
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-400 mb-1">Session Duration</p>
                <p className="text-white">
                  {user?.last_login ? "Since first login" : "No active session"}
                </p>
              </div>

              <div>
                <p className="text-gray-400 mb-1">Security Status</p>
                <p className="text-green-400">
                  {sessionStatus.status === "active" ? "Secure" : "Normal"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Security Notice */}
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-blue-400 font-medium text-sm mb-1">
                Session Security
              </p>
              <p className="text-blue-300 text-sm">
                Your session is protected by your password and MFA (if enabled).
                For maximum security, log out when using shared devices.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
