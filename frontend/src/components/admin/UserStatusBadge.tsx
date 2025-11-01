import React from "react";
import { CheckCircle, XCircle, Clock, Mail, Shield } from "lucide-react";

interface UserStatusBadgeProps {
  isActive: boolean;
  emailVerified: boolean;
  mfaEnabled?: boolean;
  size?: "sm" | "md";
}

export const UserStatusBadge: React.FC<UserStatusBadgeProps> = ({
  isActive,
  emailVerified,
  mfaEnabled = false,
  size = "md",
}) => {
  const sizeClasses = {
    sm: "px-2 py-1 text-xs",
    md: "px-3 py-1.5 text-sm",
  };

  const iconSize = size === "sm" ? "w-3 h-3" : "w-4 h-4";

  return (
    <div className="flex items-center gap-2">
      {/* Active Status */}
      <span
        className={`inline-flex items-center gap-1.5 rounded-full font-medium ${sizeClasses[size]} ${
          isActive
            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
            : "bg-red-500/10 text-red-400 border border-red-500/20"
        }`}
      >
        {isActive ? (
          <CheckCircle className={iconSize} />
        ) : (
          <XCircle className={iconSize} />
        )}
        {isActive ? "Active" : "Inactive"}
      </span>

      {/* Email Verification */}
      {emailVerified ? (
        <span
          className={`inline-flex items-center gap-1.5 rounded-full font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20 ${sizeClasses[size]}`}
        >
          <Mail className={iconSize} />
          Verified
        </span>
      ) : (
        <span
          className={`inline-flex items-center gap-1.5 rounded-full font-medium bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 ${sizeClasses[size]}`}
        >
          <Clock className={iconSize} />
          Pending
        </span>
      )}

      {/* MFA Status */}
      {mfaEnabled && (
        <span
          className={`inline-flex items-center gap-1.5 rounded-full font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20 ${sizeClasses[size]}`}
        >
          <Shield className={iconSize} />
          MFA
        </span>
      )}
    </div>
  );
};
