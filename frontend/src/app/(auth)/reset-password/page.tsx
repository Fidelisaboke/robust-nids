"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { CheckCircle, Eye, EyeOff, Lock, Shield } from "lucide-react";
import {
  type ResetPasswordRequest,
  ResetPasswordRequestSchema,
} from "@/types/auth";
import { toast } from "sonner";
import { normalizeError } from "@/lib/api/apiClient";
import { zodResolver } from "@hookform/resolvers/zod";
import { useResetPasswordMutation } from "@/hooks/useAuthMutations";

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");
  const [mfaRequired, setMfaRequired] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const resetPasswordMutation = useResetPasswordMutation();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordRequest>({
    resolver: zodResolver(ResetPasswordRequestSchema),
    defaultValues: { token: token || "" },
  });

  const password = watch("new_password");

  useEffect(() => {
    if (!token) {
      toast.error("Invalid reset link");
      router.push("/forgot-password");
    }
  }, [token, router]);

  const onSubmit = async (data: ResetPasswordRequest) => {
    try {
      const response = await resetPasswordMutation.mutateAsync(data);
      toast.success(response.detail);
      setIsSuccess(true);
      setTimeout(() => router.push("/login"), 2000);
    } catch (error) {
      const normalized = normalizeError(error);
      if (normalized.message.includes("MFA verification required")) {
        setMfaRequired(true);
        toast.error(
          "MFA Verification Required. Please complete MFA to proceed.",
        );
      } else {
        toast.error(normalizeError(error).message);
      }
    }
  };

  if (isSuccess) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6 text-center"
      >
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-500/10 border border-green-500/20 mb-4">
          <CheckCircle className="w-10 h-10 text-green-400" />
        </div>
        <h2 className="text-3xl font-bold text-white">Password Reset!</h2>
        <p className="text-gray-400">Redirecting to login...</p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white">New Password</h2>
        <p className="text-gray-400 mt-2">Create your new password</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            New Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type={showPassword ? "text" : "password"}
              {...register("new_password", {
                required: "Password is required",
                minLength: { value: 8, message: "Minimum 8 characters" },
              })}
              className="w-full pl-11 pr-11 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
            >
              {showPassword ? (
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

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Confirm Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type={showConfirm ? "text" : "password"}
              {...register("confirm_password", {
                required: "Please confirm password",
                validate: (value) =>
                  value === password || "Passwords do not match",
              })}
              className="w-full pl-11 pr-11 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
            <button
              type="button"
              onClick={() => setShowConfirm(!showConfirm)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
            >
              {showConfirm ? (
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

        {mfaRequired && (
          <div className="space-y-4">
            <div className="text-center">
              <Shield className="w-8 h-8 text-blue-400 mx-auto mb-2" />
              <p className="text-sm text-gray-400">MFA Verification Required</p>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-300 mb-2">
                Enter MFA Code from your authenticator app to continue.
              </label>
              <input
                type="text"
                inputMode="numeric"
                maxLength={6}
                {...register("mfa_code", {
                  required: mfaRequired ? "MFA code is required" : false,
                })}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white text-center text-xl font-mono tracking-[0.5em] focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="000000"
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full py-3 px-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all disabled:opacity-50"
        >
          Reset Password
        </button>
      </form>
    </motion.div>
  );
}
