import React from "react";
import { User } from "@/types/auth";
import { UserStatusBadge } from "./UserStatusBadge";
import { Skeleton } from "@/components/ui/skeleton";
import { Calendar, Mail } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface UserTableProps {
  users: User[];
  isLoading: boolean;
  onUserClick: (userId: number) => void;
}

export const UserTable: React.FC<UserTableProps> = ({
  users,
  isLoading,
  onUserClick,
}) => {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-20 bg-slate-800" />
        ))}
      </div>
    );
  }

  if (users.length === 0) {
    return (
      <div className="text-center py-12 bg-slate-800/50 border border-slate-700 rounded-xl">
        <p className="text-gray-400 text-lg">No users found</p>
        <p className="text-gray-500 text-sm mt-2">
          Try adjusting your filters or search criteria
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Table */}
      <div className="overflow-x-auto bg-slate-800/50 border border-slate-700 rounded-xl">
        <table className="w-full">
          <thead className="bg-slate-900/50 border-b border-slate-700">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                User
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Department / Role
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Last Login
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {users.map((user) => (
              <tr
                key={user.id}
                className="hover:bg-slate-900/50 transition-colors cursor-pointer"
                onClick={() => onUserClick(user.id)}
              >
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-linear-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white font-semibold">
                      {user.first_name?.[0]}
                      {user.last_name?.[0]}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">
                        {user.first_name} {user.last_name}
                      </p>
                      <div className="flex items-center space-x-1 text-xs text-gray-400">
                        <Mail className="w-3 h-3" />
                        <span>{user.email}</span>
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div>
                    <p className="text-sm text-white">{user.department}</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {user.roles?.map((role) => (
                        <span
                          key={role.id}
                          className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-xs rounded-full border border-emerald-500/30"
                        >
                          {role.name}
                        </span>
                      ))}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <UserStatusBadge
                    isActive={user.is_active}
                    emailVerified={user.email_verified}
                    mfaEnabled={user.mfa_enabled}
                    size="sm"
                  />
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center space-x-1 text-sm text-gray-400">
                    <Calendar className="w-4 h-4" />
                    <span>
                      {user.last_login
                        ? formatDistanceToNow(new Date(user.last_login), {
                            addSuffix: true,
                          })
                        : "Never"}
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
