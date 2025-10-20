"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Lock, Eye, EyeOff, CheckCircle, Loader2 } from "lucide-react";
import {
  ChangePasswordRequestSchema,
  type ChangePasswordRequest,
} from "@/types/auth";
import { useChangePasswordMutation } from "@/hooks/useAuthMutations";
import { toast } from "sonner";
import { normalizeError } from "@/lib/api/apiClient";

const PASSWORD_SUCCESS_DISPLAY_DURATION = 3000;

export function PasswordSection() {
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordChanged, setPasswordChanged] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ChangePasswordRequest>({
    resolver: zodResolver(ChangePasswordRequestSchema),
  });

  const changePasswordMutation = useChangePasswordMutation();

  const handleChangePassword = async (data: ChangePasswordRequest) => {
    try {
      const response = await changePasswordMutation.mutateAsync(data);
      toast.success(response.detail);
      setPasswordChanged(true);
      setShowChangePassword(false);
      reset();
      setTimeout(
        () => setPasswordChanged(false),
        PASSWORD_SUCCESS_DISPLAY_DURATION,
      );
    } catch (error) {
      toast.error(normalizeError(error).message);
    }
  };

  const handleCancel = () => {
    setShowChangePassword(false);
    reset();
  };

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
      <div className="flex items-start space-x-4">
        <div className="p-3 bg-purple-500/10 rounded-lg">
          <Lock className="w-6 h-6 text-purple-400" />
        </div>
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-white mb-2">Password</h3>
          <p className="text-gray-400 mb-4">
            Change your password regularly to keep your account secure.
          </p>

          {passwordChanged ? (
            <div className="flex items-center space-x-2 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span className="text-green-400 text-sm">
                Password changed successfully!
              </span>
            </div>
          ) : showChangePassword ? (
            <form
              onSubmit={handleSubmit(handleChangePassword)}
              className="space-y-4"
            >
              {/* Current Password */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Current Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type={showCurrentPassword ? "text" : "password"}
                    {...register("current_password")}
                    className="w-full pl-11 pr-11 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="Enter current password"
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
                  >
                    {showCurrentPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
                {errors.current_password && (
                  <p className="mt-1 text-sm text-red-400">
                    {errors.current_password.message}
                  </p>
                )}
              </div>

              {/* New Password */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  New Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type={showNewPassword ? "text" : "password"}
                    {...register("new_password")}
                    className="w-full pl-11 pr-11 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="Enter new password"
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
                  >
                    {showNewPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
                {errors.new_password && (
                  <p className="mt-1 text-sm text-red-400">
                    {errors.new_password.message}
                  </p>
                )}
              </div>

              {/* Confirm Password */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Confirm New Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    {...register("confirm_password")}
                    className="w-full pl-11 pr-11 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="Confirm new password"
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
                {errors.confirm_password && (
                  <p className="mt-1 text-sm text-red-400">
                    {errors.confirm_password.message}
                  </p>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3 pt-2">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <span className="flex items-center">
                      <Loader2 className="animate-spin h-4 w-4 mr-2" />
                      Changing...
                    </span>
                  ) : (
                    "Change Password"
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleCancel}
                  disabled={isSubmitting}
                  className="px-6 py-2.5 bg-slate-700 text-gray-300 font-medium rounded-lg hover:bg-slate-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-slate-500 transition-all disabled:opacity-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <button
              onClick={() => setShowChangePassword(true)}
              className="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            >
              Change Password
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
