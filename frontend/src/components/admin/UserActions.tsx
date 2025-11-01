// Table component for displaying user actions in user table

import React, { useState } from "react";
import { User } from "@/types/auth";
import { MoreVertical, UserCheck, UserX, Trash2, KeyRound } from "lucide-react";
import {
  useActivateUser,
  useDeactivateUser,
  useDeleteUser,
  useForcePasswordReset,
} from "@/hooks/useUserManagement";
import { ConfirmActionDialog } from "./ConfirmActionDialog";
import { normalizeError } from "@/lib/api/apiClient";
import { toast } from "sonner";

interface UserActionsProps {
  user: User;
  onActionComplete: () => void;
}

export const UserActions: React.FC<UserActionsProps> = ({
  user,
  onActionComplete,
}) => {
  const [showMenu, setShowMenu] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    action: "activate" | "deactivate" | "delete" | "reset-password" | null;
  }>({ open: false, action: null });

  const activateMutation = useActivateUser();
  const deactivateMutation = useDeactivateUser();
  const deleteMutation = useDeleteUser();
  const resetPasswordMutation = useForcePasswordReset();

  const handleAction = async () => {
    try {
      switch (confirmDialog.action) {
        case "activate":
          await activateMutation.mutateAsync(user.id);
          break;
        case "deactivate":
          await deactivateMutation.mutateAsync(user.id);
          break;
        case "delete":
          await deleteMutation.mutateAsync(user.id);
          break;
        case "reset-password":
          await resetPasswordMutation.mutateAsync(user.id);
          break;
      }
      setConfirmDialog({ open: false, action: null });
      setShowMenu(false);
      onActionComplete();
    } catch (error) {
      toast.error(normalizeError(error).message);
    }
  };

  const openConfirmDialog = (action: typeof confirmDialog.action) => {
    setConfirmDialog({ open: true, action });
    setShowMenu(false);
  };

  const getDialogContent = () => {
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
  const isLoading =
    activateMutation.isPending ||
    deactivateMutation.isPending ||
    deleteMutation.isPending ||
    resetPasswordMutation.isPending;

  return (
    <>
      <div className="relative" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={() => setShowMenu(!showMenu)}
          className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
        >
          <MoreVertical className="w-5 h-5 text-gray-400" />
        </button>

        {showMenu && (
          <>
            <div
              className="fixed inset-0 z-10"
              onClick={() => setShowMenu(false)}
            />
            <div className="absolute right-0 top-full mt-2 w-56 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-20 overflow-hidden">
              {user.is_active ? (
                <button
                  onClick={() => openConfirmDialog("deactivate")}
                  className="w-full flex items-center space-x-3 px-4 py-3 text-left text-orange-400 hover:bg-slate-700 transition-colors"
                >
                  <UserX className="w-4 h-4" />
                  <span className="text-sm">Deactivate User</span>
                </button>
              ) : (
                <button
                  onClick={() => openConfirmDialog("activate")}
                  className="w-full flex items-center space-x-3 px-4 py-3 text-left text-emerald-400 hover:bg-slate-700 transition-colors"
                >
                  <UserCheck className="w-4 h-4" />
                  <span className="text-sm">Activate User</span>
                </button>
              )}

              <button
                onClick={() => openConfirmDialog("reset-password")}
                className="w-full flex items-center space-x-3 px-4 py-3 text-left text-blue-400 hover:bg-slate-700 transition-colors"
              >
                <KeyRound className="w-4 h-4" />
                <span className="text-sm">Force Password Reset</span>
              </button>

              <div className="border-t border-slate-700" />

              <button
                onClick={() => openConfirmDialog("delete")}
                className="w-full flex items-center space-x-3 px-4 py-3 text-left text-red-400 hover:bg-slate-700 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                <span className="text-sm">Delete User</span>
              </button>
            </div>
          </>
        )}
      </div>

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
        isLoading={isLoading}
      />
    </>
  );
};
