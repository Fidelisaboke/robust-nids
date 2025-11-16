import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { AlertCircle, Shield, Loader2 } from "lucide-react";
import { toast } from "sonner";
import type { User } from "@/types/auth";
import type { Role } from "@/lib/api/rolesApi";

interface RoleUpdateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  user: User | undefined;
  availableRoles: Role[] | undefined;
  onUpdateRoles: (roleIds: number[]) => Promise<void>;
  isLoading?: boolean;
}

export function RoleUpdateDialog({
  open,
  onOpenChange,
  user,
  availableRoles,
  onUpdateRoles,
  isLoading = false,
}: RoleUpdateDialogProps) {
  const [selectedRoleIds, setSelectedRoleIds] = useState<number[]>([]);

  // Initialize with user's current roles
  useEffect(() => {
    if (open && user) {
      setSelectedRoleIds(user.roles.map((role) => role.id));
    }
  }, [open, user]);

  const handleRoleToggle = (roleId: number) => {
    setSelectedRoleIds((prev) => {
      if (prev.includes(roleId)) {
        return prev.filter((id) => id !== roleId);
      } else {
        return [...prev, roleId];
      }
    });
  };

  const handleSubmit = async () => {
    if (selectedRoleIds.length === 0) {
      toast.error("User must have at least one role");
      return;
    }

    try {
      await onUpdateRoles(selectedRoleIds);
    } catch {
      // Error handling is done in the parent component
    }
  };

  const getRoleDescription = (roleName: string) => {
    const descriptions: { [key: string]: string } = {
      admin: "Full system access including user management",
      analyst: "Security monitoring and alert management",
      viewer: "Read-only access to security data",
      auditor: "Access to logs and compliance reports",
    };
    return (
      descriptions[roleName.toLowerCase()] ||
      "Custom role with specific permissions"
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-slate-800 border-slate-700 max-w-md">
        <DialogHeader>
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-500/10 rounded-lg">
              <Shield className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <DialogTitle className="text-white">
                Update User Roles
              </DialogTitle>
              <DialogDescription className="text-gray-400">
                {user?.first_name} {user?.last_name}
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4">
          <div className="text-sm text-gray-400">
            Select the roles you want to assign to this user. Users can have
            multiple roles.
          </div>

          {/* Current Selection */}
          {selectedRoleIds.length > 0 && (
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-300">
                Selected Roles
              </Label>
              <div className="flex flex-wrap gap-2">
                {selectedRoleIds.map((roleId) => {
                  const role = (availableRoles ?? []).find(
                    (r) => r.id === roleId,
                  );
                  return role ? (
                    <Badge
                      key={roleId}
                      variant="secondary"
                      className="bg-purple-500/20 text-purple-300 border-purple-500/30"
                    >
                      {role.name}
                    </Badge>
                  ) : null;
                })}
              </div>
            </div>
          )}

          {/* Role Selection */}
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {(availableRoles ?? []).map((role) => (
              <div
                key={role.id}
                className={`p-3 rounded-lg border transition-all ${
                  selectedRoleIds.includes(role.id)
                    ? "bg-purple-500/10 border-purple-500/50"
                    : "bg-slate-700/50 border-slate-600 hover:bg-slate-700"
                }`}
              >
                <div className="flex items-start space-x-3">
                  <Checkbox
                    id={`role-${role.id}`}
                    checked={selectedRoleIds.includes(role.id)}
                    onCheckedChange={() => handleRoleToggle(role.id)}
                    className="data-[state=checked]:bg-purple-600 data-[state=checked]:border-purple-600 mt-0.5"
                  />
                  <div className="flex-1 min-w-0">
                    <Label
                      htmlFor={`role-${role.id}`}
                      className="font-medium text-white cursor-pointer"
                    >
                      {role.name}
                    </Label>
                    <p className="text-sm text-gray-400 mt-1">
                      {getRoleDescription(role.name)}
                    </p>

                    {/* Permissions Preview */}
                    {role.permissions && role.permissions.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-slate-600">
                        <div className="flex flex-wrap gap-1">
                          {role.permissions
                            .slice(0, 3)
                            .map((permission, index) => (
                              <span
                                key={index}
                                className="text-xs bg-slate-600 text-gray-300 px-2 py-1 rounded"
                              >
                                {permission.name}
                              </span>
                            ))}
                          {role.permissions.length > 3 && (
                            <span className="text-xs text-gray-400">
                              +{role.permissions.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Warning for role changes */}
          <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3">
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-amber-200">
                Changing roles will immediately affect this user&apos;s
                permissions and access levels.
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
            className="bg-slate-700 text-white hover:bg-slate-600 border-slate-600"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isLoading || selectedRoleIds.length === 0}
            className="bg-purple-600 hover:bg-purple-700 text-white"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Updating...
              </>
            ) : (
              "Update Roles"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
