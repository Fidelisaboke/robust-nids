"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { Users as UsersIcon, UserPlus, Clock, TrendingUp } from "lucide-react";
import {
  useUsers,
  useExportUsers,
  useCreateUser,
  useRecentUsers,
} from "@/hooks/useUserManagement";
import { UserTable } from "@/components/admin/UserTable";
import { UserFilters } from "@/components/admin/UserFilters";
import { UserListParams } from "@/lib/api/usersApi";
import Link from "next/link";
import { useRoles } from "@/hooks/useRoleManagement";
import { toast } from "sonner";
import { normalizeError } from "@/lib/api/apiClient";
import { UserFormDialog } from "@/components/admin/UserFormDialog";
import { UserFormData } from "@/schemas/userForm";
import { User } from "@/types/auth";
import { Pagination } from "@/components/Pagination";

export default function UsersPage() {
  const router = useRouter();
  const [currentPage, setCurrentPage] = useState(1);
  const [filters, setFilters] = useState<UserListParams>({});
  const [userFormOpen, setUserFormOpen] = useState(false);

  const { data: usersData, isLoading } = useUsers({
    ...filters,
    page: currentPage,
    size: 20,
  });

  // Get recent users
  const {
    data: recentUsers,
    isLoading: isRecentUsersLoading,
    error: recentUsersError,
  } = useRecentUsers(7);

  const { data: availableRoles } = useRoles();
  const createUserMutation = useCreateUser();
  const exportMutation = useExportUsers();

  const handleFilterChange = (newFilters: UserListParams) => {
    setFilters(newFilters);
    setCurrentPage(1);
  };

  const handleCreateUser = async (userData: UserFormData) => {
    try {
      await createUserMutation.mutateAsync(userData);
      toast.success("User created successfully");
    } catch (error) {
      const errorMsg = normalizeError(error).message;
      console.log(errorMsg);
      toast.error(errorMsg);
    }
  };

  const handleExport = () => {
    exportMutation.mutate(filters);
  };

  const handleUserClick = (userId: number) => {
    router.push(`/admin/users/${userId}`);
  };

  const stats = [
    {
      name: "Total Users",
      value: usersData?.total || 0,
      icon: UsersIcon,
      color: "text-emerald-400",
      bgColor: "bg-emerald-500/10",
      borderColor: "border-emerald-500/20",
    },
    {
      name: "New This Week",
      value: recentUsers?.items?.length || 0,
      icon: TrendingUp,
      color: "text-blue-400",
      bgColor: "bg-blue-500/10",
      borderColor: "border-blue-500/20",
    },
    {
      name: "Active Sessions",
      value: usersData?.items?.filter((u: User) => u.is_active).length || 0,
      icon: Clock,
      color: "text-purple-400",
      bgColor: "bg-purple-500/10",
      borderColor: "border-purple-500/20",
    },
  ];

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
            <h1 className="text-3xl font-bold text-white">User Management</h1>
            <p className="text-gray-400 mt-2">
              Manage user accounts, roles, and permissions
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/admin/users/pending"
              className="flex items-center space-x-2 px-4 py-2.5 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors"
            >
              <Clock className="w-5 h-5" />
              <span>Pending Requests</span>
            </Link>
            <button
              onClick={() => setUserFormOpen(true)}
              className="flex items-center space-x-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors"
            >
              <UserPlus className="w-5 h-5" />
              <span>Add User</span>
            </button>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={`bg-slate-800/50 border ${stat.borderColor} rounded-xl p-6`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 ${stat.bgColor} rounded-lg`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
              <h3 className="text-2xl font-bold text-white mb-1">
                {stat.value}
              </h3>
              <p className="text-sm text-gray-400">{stat.name}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <UserFilters
          onFilterChange={handleFilterChange}
          onExport={handleExport}
          isExporting={exportMutation.isPending}
        />
      </motion.div>

      {/* Users Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <UserTable
          users={usersData?.items || []}
          isLoading={isLoading}
          onUserClick={handleUserClick}
        />
        <Pagination
          currentPage={currentPage}
          totalPages={usersData?.pages || 1}
          totalItems={usersData?.total || 0}
          itemsPerPage={usersData?.size || 20}
          onPageChange={(page) => setCurrentPage(page)}
        />
      </motion.div>

      {/* User Form Dialog */}
      <UserFormDialog
        open={userFormOpen}
        onOpenChange={setUserFormOpen}
        onSubmit={handleCreateUser}
        availableRoles={availableRoles?.items || []}
        isLoading={createUserMutation.isPending}
      />

      {/* Recent Registrations */}
      {isRecentUsersLoading ? (
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <div className="animate-pulse">...</div>
        </div>
      ) : recentUsersError ? (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
          <p className="text-red-400 text-sm">Error loading recent users.</p>
        </div>
      ) : recentUsers && recentUsers?.items?.length > 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white">
              Recent Registrations
            </h2>
            <Link
              href="/admin/users/pending"
              className="text-sm text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              View All
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentUsers?.items?.slice(0, 6).map((user: User) => (
              <div
                key={user.id}
                onClick={() => handleUserClick(user.id)}
                className="p-4 bg-slate-900/50 rounded-lg hover:bg-slate-900 transition-colors cursor-pointer"
              >
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-10 h-10 rounded-full bg-linear-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white font-semibold">
                    {user.first_name?.[0]}
                    {user.last_name?.[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">
                      {user.first_name} {user.last_name}
                    </p>
                    <p className="text-xs text-gray-400 truncate">
                      {user.email}
                    </p>
                  </div>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-400">{user.department}</span>
                  <span className="text-emerald-400">New</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      ) : (
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 text-center text-gray-400">
          No recent user registrations.
        </div>
      )}
    </div>
  );
}
