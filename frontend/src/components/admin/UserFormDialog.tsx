import React, { useEffect } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2 } from "lucide-react";
import { User } from "@/types/auth";
import { Role } from "@/lib/api/rolesApi"; // Adjust to your Role type
import { useRoles } from "@/hooks/useRoleManagement"; // Import your hook

// Zod schema for validation
const formSchema = z.object({
  first_name: z.string().min(2, "First name is required"),
  last_name: z.string().min(2, "Last name is required"),
  email: z.email(),
  department: z.string().optional(),
  password: z
    .string()
    .optional()
    .refine((val) => val === "" || !val || val.length >= 8, {
      message: "Password must be at least 8 characters",
    }),
  role_ids: z.array(z.number()).min(1, "At least one role must be selected"),
});

export type UserFormData = z.infer<typeof formSchema>;

interface UserFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  user?: User | null;
  onSubmit: (values: UserFormData) => void;
  isLoading?: boolean;
}

export const UserFormDialog: React.FC<UserFormDialogProps> = ({
  open,
  onOpenChange,
  user,
  onSubmit,
  isLoading,
}) => {
  const isEditMode = Boolean(user);

  const { data: allRoles, isLoading: isLoadingRoles } = useRoles();

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<UserFormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      email: "",
      department: "",
      password: "",
      role_ids: [],
    },
  });

  // Populate form when in edit mode or clear for create mode
  useEffect(() => {
    if (open) {
      if (isEditMode && user) {
        reset({
          first_name: user.first_name,
          last_name: user.last_name,
          email: user.email,
          department: user.department || "",
          password: "", // Always clear password field
          role_ids: user.roles.map((role: Role) => role.id), // Set role IDs
        });
      } else {
        // Reset form for create mode
        reset({
          first_name: "",
          last_name: "",
          email: "",
          department: "",
          password: "",
          role_ids: [],
        });
      }
    }
  }, [user, isEditMode, open, reset]);

  // Handle form submission
  const onValidSubmit = (data: UserFormData) => {
    const payload = { ...data };

    // If in edit mode and password is empty, don't send it
    if (isEditMode && !payload.password) {
      delete payload.password;
    }

    onSubmit(payload);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-slate-800 border-slate-700 text-white sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>
            {isEditMode ? "Edit User" : "Create New User"}
          </DialogTitle>
          <DialogDescription className="text-gray-400">
            {isEditMode
              ? "Update the user's details."
              : "Fill in the form to add a new user."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onValidSubmit)} className="space-y-4 pt-4">
          <div className="grid grid-cols-2 gap-4">
            {/* First Name */}
            <div className="space-y-2">
              <Label htmlFor="firstName" className="text-white">
                First Name
              </Label>
              <Input
                id="firstName"
                placeholder="John"
                className="bg-slate-900 border-slate-700"
                {...register("first_name")}
              />
              {errors.first_name && (
                <p className="text-sm text-red-400">
                  {errors.first_name.message}
                </p>
              )}
            </div>
            {/* Last Name */}
            <div className="space-y-2">
              <Label htmlFor="lastName" className="text-white">
                Last Name
              </Label>
              <Input
                id="lastName"
                placeholder="Doe"
                className="bg-slate-900 border-slate-700"
                {...register("last_name")}
              />
              {errors.last_name && (
                <p className="text-sm text-red-400">
                  {errors.last_name.message}
                </p>
              )}
            </div>
          </div>

          {/* Email */}
          <div className="space-y-2">
            <Label htmlFor="email" className="text-white">
              Email
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="john.doe@example.com"
              className="bg-slate-900 border-slate-700"
              {...register("email")}
            />
            {errors.email && (
              <p className="text-sm text-red-400">{errors.email.message}</p>
            )}
          </div>

          {/* Department */}
          <div className="space-y-2">
            <Label htmlFor="department" className="text-white">
              Department
            </Label>
            <Input
              id="department"
              placeholder="Engineering"
              className="bg-slate-900 border-slate-700"
              {...register("department")}
            />
            {errors.department && (
              <p className="text-sm text-red-400">
                {errors.department.message}
              </p>
            )}
          </div>

          {/* Password */}
          <div className="space-y-2">
            <Label htmlFor="password" className="text-white">
              Password
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="********"
              className="bg-slate-900 border-slate-700"
              {...register("password")}
            />
            {isEditMode && (
              <p className="text-xs text-gray-400 mt-1">
                Leave blank to keep current password.
              </p>
            )}
            {errors.password && (
              <p className="text-sm text-red-400">{errors.password.message}</p>
            )}
          </div>

          {/* Roles Checkbox Group */}
          <div className="space-y-2">
            <Label className="text-white">Roles</Label>
            {isLoadingRoles ? (
              <div className="space-y-2">
                <Skeleton className="h-5 w-1/3 bg-slate-700" />
                <Skeleton className="h-5 w-1/2 bg-slate-700" />
              </div>
            ) : (
              <Controller
                name="role_ids"
                control={control}
                render={({ field }) => (
                  <div className="max-h-40 overflow-y-auto rounded-md border border-slate-700 bg-slate-900 p-4 space-y-3">
                    {allRoles?.map((role) => (
                      <div
                        key={role.id}
                        className="flex items-center space-x-3"
                      >
                        <Checkbox
                          id={`role-${role.id}`}
                          checked={field.value?.includes(role.id)}
                          onCheckedChange={(checked: boolean) => {
                            const currentIds = field.value || [];
                            if (checked) {
                              field.onChange([...currentIds, role.id]);
                            } else {
                              field.onChange(
                                currentIds.filter((id) => id !== role.id),
                              );
                            }
                          }}
                          className="border-slate-500 data-[state=checked]:bg-emerald-600 data-[state=checked]:border-emerald-600"
                        />
                        <label
                          htmlFor={`role-${role.id}`}
                          className="text-sm font-medium text-white leading-none cursor-pointer"
                        >
                          {role.name}
                          {role.description && (
                            <p className="text-xs text-gray-400">
                              {role.description}
                            </p>
                          )}
                        </label>
                      </div>
                    ))}
                  </div>
                )}
              />
            )}
            {errors.role_ids && (
              <p className="text-sm text-red-400 mt-1">
                {errors.role_ids.message}
              </p>
            )}
          </div>

          {/* 9. Dialog Footer with Submit Button */}
          <DialogFooter className="pt-4">
            <DialogClose asChild>
              <Button
                type="button"
                variant="outline"
                className="bg-slate-700 text-white hover:bg-slate-600 border-slate-600"
                disabled={isLoading}
              >
                Cancel
              </Button>
            </DialogClose>
            <Button
              type="submit"
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
              disabled={isLoading || isLoadingRoles}
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : isEditMode ? (
                "Save Changes"
              ) : (
                "Create User"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
