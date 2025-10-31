import React from "react";
import { User } from "@/types/auth";
import { UserStatusBadge } from "./UserStatusBadge";
import {
  Mail,
  Phone,
  Building,
  Briefcase,
  Calendar,
  Clock,
  Shield,
  MapPin,
  Key,
  Users,
} from "lucide-react";
import { format } from "date-fns";
import { Badge } from "@/components/ui/badge";

interface UserDetailsCardProps {
  user: User;
}

export const UserDetailsCard: React.FC<UserDetailsCardProps> = ({ user }) => {
  // const getRoleVariant = (roleName: string) => {
  //   const variants: { [key: string]: "default" | "secondary" | "destructive" | "outline" } = {
  //     admin: "destructive",
  //     analyst: "default",
  //     viewer: "secondary",
  //     auditor: "outline",
  //   };
  //   return variants[roleName.toLowerCase()] || "secondary";
  // };

  const getRoleColor = (roleName: string) => {
    const colors: { [key: string]: string } = {
      admin: "bg-red-500/20 text-red-300 border-red-500/30",
      analyst: "bg-blue-500/20 text-blue-300 border-blue-500/30",
      viewer: "bg-slate-500/20 text-slate-300 border-slate-500/30",
      auditor: "bg-purple-500/20 text-purple-300 border-purple-500/30",
    };
    return (
      colors[roleName.toLowerCase()] ||
      "bg-slate-500/20 text-slate-300 border-slate-500/30"
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Profile Card */}
      <div className="lg:col-span-1">
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <div className="flex flex-col items-center text-center">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white text-3xl font-semibold mb-4">
              {user.first_name?.[0]}
              {user.last_name?.[0]}
            </div>
            <h2 className="text-2xl font-bold text-white mb-1">
              {user.first_name} {user.last_name}
            </h2>
            <p className="text-gray-400 text-sm mb-4">@{user.username}</p>
            <UserStatusBadge
              isActive={user.is_active}
              emailVerified={user.email_verified}
              mfaEnabled={user.mfa_enabled}
            />
          </div>

          <div className="mt-6 pt-6 border-t border-slate-700 space-y-3">
            <div className="flex items-center space-x-3 text-sm">
              <Mail className="w-4 h-4 text-gray-400" />
              <span className="text-gray-300">{user.email}</span>
            </div>
            {user.phone && (
              <div className="flex items-center space-x-3 text-sm">
                <Phone className="w-4 h-4 text-gray-400" />
                <span className="text-gray-300">{user.phone}</span>
              </div>
            )}
            {user.department && (
              <div className="flex items-center space-x-3 text-sm">
                <Building className="w-4 h-4 text-gray-400" />
                <span className="text-gray-300">{user.department}</span>
              </div>
            )}
            {user.job_title && (
              <div className="flex items-center space-x-3 text-sm">
                <Briefcase className="w-4 h-4 text-gray-400" />
                <span className="text-gray-300">{user.job_title}</span>
              </div>
            )}
            <div className="flex items-center space-x-3 text-sm">
              <MapPin className="w-4 h-4 text-gray-400" />
              <span className="text-gray-300">{user.timezone}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Details Cards */}
      <div className="lg:col-span-2 space-y-6">
        {/* Account Information */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Account Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-gray-400">Account Status</label>
              <p className="text-white font-medium mt-1">
                {user.is_active ? "Active" : "Inactive"}
              </p>
            </div>
            <div>
              <label className="text-sm text-gray-400">Email Verified</label>
              <p className="text-white font-medium mt-1">
                {user.email_verified ? "Yes" : "No"}
                {user.email_verified_at && (
                  <span className="text-xs text-gray-400 ml-2">
                    ({format(new Date(user.email_verified_at), "MMM d, yyyy")})
                  </span>
                )}
              </p>
            </div>
            <div>
              <label className="text-sm text-gray-400">MFA Status</label>
              <p className="text-white font-medium mt-1">
                {user.mfa_enabled ? `Enabled (${user.mfa_method})` : "Disabled"}
              </p>
            </div>
            <div>
              <label className="text-sm text-gray-400">Profile Completed</label>
              <p className="text-white font-medium mt-1">
                {user.profile_completed ? "Yes" : "No"}
              </p>
            </div>
            <div>
              <label className="text-sm text-gray-400">Member Since</label>
              <div className="flex items-center space-x-2 mt-1">
                <Calendar className="w-4 h-4 text-gray-400" />
                <p className="text-white font-medium">
                  {format(new Date(user.created_at), "MMM d, yyyy")}
                </p>
              </div>
            </div>
            <div>
              <label className="text-sm text-gray-400">Last Login</label>
              <div className="flex items-center space-x-2 mt-1">
                <Clock className="w-4 h-4 text-gray-400" />
                <p className="text-white font-medium">
                  {user.last_login
                    ? format(new Date(user.last_login), "MMM d, yyyy HH:mm")
                    : "Never"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Roles & Permissions */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Shield className="w-5 h-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">
                Roles & Permissions
              </h3>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <Users className="w-4 h-4" />
              <span>{user.roles?.length || 0} role(s)</span>
            </div>
          </div>

          {user.roles && user.roles.length > 0 ? (
            <div className="space-y-4">
              {/* Role Badges - Quick Overview */}
              <div className="flex flex-wrap gap-2">
                {user.roles.map((role) => (
                  <Badge
                    key={role.id}
                    variant="secondary"
                    className={getRoleColor(role.name)}
                  >
                    {role.name}
                  </Badge>
                ))}
              </div>

              {/* Detailed Role Information */}
              <div className="space-y-3">
                {user.roles.map((role) => (
                  <div
                    key={role.id}
                    className="p-4 bg-slate-900/50 rounded-lg border border-slate-700"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Key className="w-4 h-4 text-purple-400" />
                          <p className="text-white font-medium">{role.name}</p>
                          <Badge
                            variant="outline"
                            className="bg-purple-500/10 text-purple-300 border-purple-500/30 text-xs"
                          >
                            Active
                          </Badge>
                        </div>
                        {role.description && (
                          <p className="text-sm text-gray-400">
                            {role.description}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Permissions */}
                    {role.permissions && role.permissions.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-700">
                        <p className="text-sm text-gray-400 mb-2">
                          Permissions:
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {role.permissions.map((permission, index) => (
                            <span
                              key={index}
                              className="text-xs bg-slate-800 text-gray-300 px-2 py-1 rounded border border-slate-700"
                            >
                              {permission.name}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Shield className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400">No roles assigned</p>
              <p className="text-sm text-gray-500 mt-1">
                This user doesn&apos;t have any roles assigned yet.
              </p>
            </div>
          )}
        </div>

        {/* Security Information */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Security Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {user.last_profile_update && (
              <div>
                <label className="text-sm text-gray-400">
                  Last Profile Update
                </label>
                <div className="flex items-center space-x-2 mt-1">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <p className="text-white font-medium">
                    {format(new Date(user.last_profile_update), "MMM d, yyyy")}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
