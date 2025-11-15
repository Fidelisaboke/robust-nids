"use client";

import React, { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import {
  UserPlus,
  UserIcon,
  Mail,
  Phone,
  Building,
  Briefcase,
  Shield,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { User, Role } from "@/types/auth";
import { userFormSchema, type UserFormData } from "@/schemas/userForm";

interface UserFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  user?: User;
  availableRoles: Role[];
  onSubmit: (data: UserFormData) => Promise<void>;
  isLoading?: boolean;
}

export function UserFormDialog({
  open,
  onOpenChange,
  user,
  availableRoles,
  onSubmit,
  isLoading = false,
}: UserFormDialogProps) {
  const isEditMode = !!user;

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    setValue,
    getValues,
    reset,
  } = useForm<UserFormData>({
    resolver: zodResolver(userFormSchema),
    defaultValues: {
      email: "",
      username: "",
      first_name: "",
      last_name: "",
      phone: "",
      department: "",
      job_title: "",
      is_active: true,
      send_welcome_email: true,
      role_ids: [],
    },
    mode: "onChange",
  });

  // Watch role_ids to show selected roles
  const selectedRoleIds = watch("role_ids");
  const isActive = watch("is_active");
  const sendWelcomeEmail = watch("send_welcome_email");

  // Initialize form when opening or when user data changes
  useEffect(() => {
    if (open) {
      if (user) {
        // Edit mode
        reset({
          email: user.email || "",
          username: user.username || "",
          first_name: user.first_name || "",
          last_name: user.last_name || "",
          phone: user.phone || "",
          department: user.department || "",
          job_title: user.job_title || "",
          is_active: user.is_active ?? true,
          send_welcome_email: false,
          role_ids: user.roles?.map((role: Role) => role.id) || [],
        });
      } else {
        // Create mode
        reset({
          email: "",
          username: "",
          first_name: "",
          last_name: "",
          phone: "",
          department: "",
          job_title: "",
          is_active: true,
          send_welcome_email: true,
          role_ids: [],
        });
      }
    }
  }, [open, user, reset]);

  const handleRoleToggle = (roleId: number) => {
    const currentRoles = getValues("role_ids");
    const newRoles = currentRoles.includes(roleId)
      ? currentRoles.filter((id) => id !== roleId)
      : [...currentRoles, roleId];

    setValue("role_ids", newRoles, { shouldValidate: true });
  };

  const onFormSubmit = async (data: UserFormData) => {
    try {
      await onSubmit(data);
      onOpenChange(false);
    } catch {
      // Error handling is done in the parent component
    }
  };

  const ErrorMessage = ({ message }: { message?: string }) => {
    if (!message) return null;

    return (
      <div className="flex items-center space-x-1 mt-1 text-sm text-red-400">
        <AlertCircle className="w-3 h-3" />
        <span>{message}</span>
      </div>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-slate-800 border-slate-700 max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center space-x-3">
            <div
              className={`p-2 rounded-lg ${isEditMode ? "bg-blue-500/10" : "bg-emerald-500/10"}`}
            >
              {isEditMode ? (
                <UserIcon className="w-5 h-5 text-blue-400" />
              ) : (
                <UserPlus className="w-5 h-5 text-emerald-400" />
              )}
            </div>
            <div>
              <DialogTitle className="text-white">
                {isEditMode ? "Edit User" : "Create New User"}
              </DialogTitle>
              <DialogDescription className="text-gray-400">
                {isEditMode
                  ? `Update ${user.first_name} ${user.last_name}'s information`
                  : "Add a new user to the system"}
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
              <UserIcon className="w-4 h-4 text-gray-400" />
              <span>Basic Information</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name" className="text-gray-300">
                  First Name *
                </Label>
                <Input
                  id="first_name"
                  placeholder="John"
                  className="bg-slate-700 border-slate-600 text-white"
                  {...register("first_name")}
                />
                <ErrorMessage message={errors.first_name?.message} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="last_name" className="text-gray-300">
                  Last Name *
                </Label>
                <Input
                  id="last_name"
                  placeholder="Doe"
                  className="bg-slate-700 border-slate-600 text-white"
                  {...register("last_name")}
                />
                <ErrorMessage message={errors.last_name?.message} />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-gray-300">
                  Email Address *
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="john.doe@example.com"
                    className="bg-slate-700 border-slate-600 text-white pl-10"
                    disabled={isEditMode}
                    {...register("email")}
                  />
                </div>
                <ErrorMessage message={errors.email?.message} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="username" className="text-gray-300">
                  Username *
                </Label>
                <Input
                  id="username"
                  placeholder="johndoe"
                  className="bg-slate-700 border-slate-600 text-white"
                  disabled={isEditMode}
                  {...register("username")}
                />
                <ErrorMessage message={errors.username?.message} />
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Phone className="w-4 h-4 text-gray-400" />
              <span>Contact Information</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="phone" className="text-gray-300">
                  Phone Number
                </Label>
                <div className="relative">
                  <Phone className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="+1 (555) 123-4567"
                    className="bg-slate-700 border-slate-600 text-white pl-10"
                    {...register("phone")}
                  />
                </div>
                <ErrorMessage message={errors.phone?.message} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="department" className="text-gray-300">
                  Department
                </Label>
                <div className="relative">
                  <Building className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  <Input
                    id="department"
                    placeholder="IT Security"
                    className="bg-slate-700 border-slate-600 text-white pl-10"
                    {...register("department")}
                  />
                </div>
                <ErrorMessage message={errors.department?.message} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="job_title" className="text-gray-300">
                Job Title
              </Label>
              <div className="relative">
                <Briefcase className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                <Input
                  id="job_title"
                  placeholder="Security Analyst"
                  className="bg-slate-700 border-slate-600 text-white pl-10"
                  {...register("job_title")}
                />
              </div>
              <ErrorMessage message={errors.job_title?.message} />
            </div>
          </div>

          {/* Roles & Permissions */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Shield className="w-4 h-4 text-gray-400" />
              <span>Roles & Permissions</span>
            </h3>

            {/* Selected Roles */}
            {selectedRoleIds.length > 0 && (
              <div className="space-y-2">
                <Label className="text-sm text-gray-300">Selected Roles</Label>
                <div className="flex flex-wrap gap-2">
                  {selectedRoleIds.map((roleId) => {
                    const role = availableRoles.find((r) => r.id === roleId);
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
            <div className="space-y-2">
              <Label className="text-sm text-gray-300">Assign Roles *</Label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-48 overflow-y-auto">
                {availableRoles.map((role) => (
                  <div
                    key={role.id}
                    className={`p-3 rounded-lg border transition-all cursor-pointer ${
                      selectedRoleIds.includes(role.id)
                        ? "bg-purple-500/10 border-purple-500/50"
                        : "bg-slate-700/50 border-slate-600 hover:bg-slate-700"
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <Checkbox
                        checked={selectedRoleIds.includes(role.id)}
                        onCheckedChange={() => handleRoleToggle(role.id)}
                        className="data-[state=checked]:bg-purple-600 data-[state=checked]:border-purple-600"
                      />
                      <div className="flex-1 min-w-0">
                        <Label className="font-medium text-white cursor-pointer">
                          {role.name}
                        </Label>
                        {role.description && (
                          <p className="text-sm text-gray-400 mt-1">
                            {role.description}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <ErrorMessage message={errors.role_ids?.message} />
            </div>
          </div>

          {/* Settings */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Settings</h3>

            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <Checkbox
                  id="is_active"
                  checked={isActive}
                  onCheckedChange={(checked) =>
                    setValue("is_active", checked as boolean)
                  }
                  className="data-[state=checked]:bg-emerald-600 data-[state=checked]:border-emerald-600"
                />
                <Label
                  htmlFor="is_active"
                  className="text-gray-300 cursor-pointer"
                >
                  Account is active
                </Label>
              </div>
              <p className="text-sm text-gray-500 ml-7">
                User will be able to access the system immediately
              </p>

              {!isEditMode && (
                <>
                  <div className="flex items-center space-x-3">
                    <Checkbox
                      id="send_welcome_email"
                      checked={sendWelcomeEmail}
                      onCheckedChange={(checked) =>
                        setValue("send_welcome_email", checked as boolean)
                      }
                      className="data-[state=checked]:bg-blue-600 data-[state=checked]:border-blue-600"
                    />
                    <Label
                      htmlFor="send_welcome_email"
                      className="text-gray-300 cursor-pointer"
                    >
                      Send welcome email
                    </Label>
                  </div>
                  <p className="text-sm text-gray-500 ml-7">
                    User will receive setup instructions via email
                  </p>
                </>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
              className="bg-slate-700 text-white hover:bg-slate-600 border-slate-600"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading || !isValid}
              className={
                isEditMode
                  ? "bg-blue-600 hover:bg-blue-700"
                  : "bg-emerald-600 hover:bg-emerald-700"
              }
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {isEditMode ? "Updating..." : "Creating..."}
                </>
              ) : isEditMode ? (
                "Update User"
              ) : (
                "Create User"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
