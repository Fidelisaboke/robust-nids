"use client";

import React, { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Edit,
  Shield,
  UserCheck,
  UserX,
  KeyRound,
  Trash2,
  Activity,
} from "lucide-react";
import { useRoles } from "@/hooks/useRoleManagement";
import {
  useUpdateUser,
  useUpdateUserRoles,
  useUser,
  useUserActivity,
} from "@/hooks/useUserManagement";
import { UserDetailsCard } from "@/components/admin/UserDetailsCard";
import { ConfirmActionDialog } from "@/components/admin/ConfirmActionDialog";
import { RoleUpdateDialog } from "@/components/admin/RoleUpdateDialog";
import {
  useActivateUser,
  useDeactivateUser,
  useDeleteUser,
  useForcePasswordReset,
} from "@/hooks/useUserManagement";
import { Skeleton } from "@/components/ui/skeleton";
import { format } from "date-fns";
import { toast } from "sonner";
import { normalizeError } from "@/lib/api/apiClient";
import { UserFormData } from "@/schemas/userForm";
import { UserFormDialog } from "@/components/admin/UserFormDialog";

export default function UserDetailPage() {
  const params = useParams();
  const router = useRouter();
  const userId = parseInt(params.id as string);

  const { data: user, isLoading } = useUser(userId);
  const { data: activityData } = useUserActivity(userId, 1, 10);
  const { data: availableRoles } = useRoles();

  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    action: "activate" | "deactivate" | "delete" | "reset-password" | null;
  }>({ open: false, action: null });

  const [userFormOpen, setUserFormOpen] = useState<boolean>(false);
  const [roleUpdateDialog, setRoleUpdateDialog] = useState<boolean>(false);

  const activateMutation = useActivateUser();
  const deactivateMutation = useDeactivateUser();
  const deleteMutation = useDeleteUser();
  const resetPasswordMutation = useForcePasswordReset();
  const updateUserMutation = useUpdateUser();
  const updateRolesMutation = useUpdateUserRoles();

  // Handle confirm dialog action
  const handleAction = async () => {
    let response = null;
    try {
      switch (confirmDialog.action) {
        case "activate":
          response = await activateMutation.mutateAsync(userId);
          break;
        case "deactivate":
          response = await deactivateMutation.mutateAsync(userId);
          break;
        case "delete":
          await deleteMutation.mutateAsync(userId);
          router.push("/admin/users");
          break;
        case "reset-password":
          response = await resetPasswordMutation.mutateAsync(userId);
          break;
      }
      if (response) toast.success(response?.detail);
      setConfirmDialog({ open: false, action: null });
    } catch (error) {
      toast.error(normalizeError(error).message);
    }
  };

  // Handle user form submission
  const handleUpdateUser = async (userData: UserFormData) => {
    try {
      await updateUserMutation.mutateAsync({ id: userId, data: userData });
      toast.success("User updated successfully");
      setUserFormOpen(false);
    } catch (error) {
      toast.error(normalizeError(error).message);
    }
  };

  // Handle role update
  const handleRoleUpdate = async (roleIds: number[]) => {
    try {
      const response = await updateRolesMutation.mutateAsync({
        id: userId,
        role_ids: roleIds,
      });
      toast.success(response.detail);
      setRoleUpdateDialog(false);
    } catch (error) {
      toast.error(normalizeError(error).message);
    }
  };

  const openConfirmDialog = (action: typeof confirmDialog.action) => {
    setConfirmDialog({ open: true, action });
  };

  const getDialogContent = () => {
    if (!user)
      return {
        title: "",
        description: "",
        confirmText: "",
        variant: "default" as const,
      };

    switch (confirmDialog.action) {
      case "activate":
        return {
          title: "Activate User",
          description: `Are you sure you want to activate ${user.first_name} ${user.last_name}? They will regain access to the system.`,
          confirmText: "Activate",
          variant: "default" as const,
        };
      case "deactivate":
        return {
          title: "Deactivate User",
          description: `Are you sure you want to deactivate ${user.first_name} ${user.last_name}? They will lose access to the system.`,
          confirmText: "Deactivate",
          variant: "destructive" as const,
        };
      case "delete":
        return {
          title: "Delete User",
          description: `Are you sure you want to permanently delete ${user.first_name} ${user.last_name}? This action cannot be undone.`,
          confirmText: "Delete",
          variant: "destructive" as const,
        };
      case "reset-password":
        return {
          title: "Force Password Reset",
          description: `Are you sure you want to force a password reset for ${user.first_name} ${user.last_name}? They will be required to set a new password on next login.`,
          confirmText: "Reset Password",
          variant: "default" as const,
        };
      default:
        return {
          title: "",
          description: "",
          confirmText: "",
          variant: "default" as const,
        };
    }
  };

  const dialogContent = getDialogContent();
  const isActionLoading =
    activateMutation.isPending ||
    deactivateMutation.isPending ||
    deleteMutation.isPending ||
    resetPasswordMutation.isPending;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64 bg-slate-800" />
        <Skeleton className="h-96 bg-slate-800" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400 text-lg">User not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-6 h-6 text-gray-400" />
            </button>
            <div>
              <h1 className="text-3xl font-bold text-white">User Details</h1>
              <p className="text-gray-400 mt-2">
                View and manage user information
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setUserFormOpen(true)}
              className="flex items-center space-x-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors border border-slate-700"
            >
              <Edit className="w-4 h-4" />
              <span>Edit User</span>
            </button>
            <button
              onClick={() => setRoleUpdateDialog(true)}
              className="flex items-center space-x-2 px-4 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
            >
              <Shield className="w-4 h-4" />
              <span>Update Roles</span>
            </button>
            {user.is_active ? (
              <button
                onClick={() => openConfirmDialog("deactivate")}
                className="flex items-center space-x-2 px-4 py-2.5 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors"
              >
                <UserX className="w-4 h-4" />
                <span>Deactivate</span>
              </button>
            ) : (
              <button
                onClick={() => openConfirmDialog("activate")}
                className="flex items-center space-x-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors"
              >
                <UserCheck className="w-4 h-4" />
                <span>Activate</span>
              </button>
            )}
            <button
              onClick={() => openConfirmDialog("reset-password")}
              className="flex items-center space-x-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              <KeyRound className="w-4 h-4" />
              <span>Reset Password</span>
            </button>
            <button
              onClick={() => openConfirmDialog("delete")}
              className="p-2.5 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.div>

      {/* User Details */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <UserDetailsCard user={user} />
      </motion.div>

      {/* User Form Dialog */}
      <UserFormDialog
        open={userFormOpen}
        onOpenChange={setUserFormOpen}
        user={user}
        availableRoles={availableRoles?.items || []}
        onSubmit={handleUpdateUser}
        isLoading={updateUserMutation.isPending}
      />

      {/* Activity Log */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <Activity className="w-5 h-5 text-emerald-400" />
          <h3 className="text-lg font-semibold text-white">Recent Activity</h3>
        </div>
        {activityData && activityData.logs.length > 0 ? (
          <div className="space-y-3">
            {activityData.logs.map(
              (log: {
                id: number;
                action: string;
                ip_address: string;
                timestamp: string;
              }) => (
                <div
                  key={log.id}
                  className="p-4 bg-slate-900/50 rounded-lg border border-slate-700"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-white font-medium">{log.action}</p>
                      <p className="text-sm text-gray-400 mt-1">
                        IP: {log.ip_address}
                      </p>
                    </div>
                    <span className="text-xs text-gray-400">
                      {format(new Date(log.timestamp), "MMM d, yyyy HH:mm")}
                    </span>
                  </div>
                </div>
              ),
            )}
          </div>
        ) : (
          <p className="text-gray-400 text-center py-8">No activity logs</p>
        )}
      </motion.div>

      {/* Confirmation Dialog */}
      <ConfirmActionDialog
        open={confirmDialog.open}
        onOpenChange={(open) =>
          setConfirmDialog({ open, action: confirmDialog.action })
        }
        onConfirm={handleAction}
        title={dialogContent.title}
        description={dialogContent.description}
        confirmText={dialogContent.confirmText}
        variant={dialogContent.variant}
        isLoading={isActionLoading}
      />

      {/* Role Update Dialog */}
      <RoleUpdateDialog
        open={roleUpdateDialog}
        onOpenChange={setRoleUpdateDialog}
        user={user}
        availableRoles={availableRoles?.items}
        onUpdateRoles={handleRoleUpdate}
        isLoading={updateRolesMutation.isPending}
      />
    </div>
  );
}
