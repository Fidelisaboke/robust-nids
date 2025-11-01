"use client";

import { useForm } from "react-hook-form";
import { motion } from "framer-motion";
import { Mail, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { useForgotPasswordMutation } from "@/hooks/useAuthMutations";
import { normalizeError } from "@/lib/api/apiClient";

export default function ForgotPasswordPage() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<{ email: string }>();
  const forgotPasswordMutation = useForgotPasswordMutation();

  const onSubmit = async (data: { email: string }) => {
    try {
      const response = await forgotPasswordMutation.mutateAsync(data.email);
      toast.success(response.detail);
    } catch (error) {
      toast.error(normalizeError(error).message);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white">Reset Password</h2>
        <p className="text-gray-400 mt-2">
          Enter your email to receive reset instructions
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Email Address
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="email"
              {...register("email", { required: "Email is required" })}
              className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="admin@example.com"
            />
          </div>
          {errors.email && (
            <p className="mt-1 text-sm text-red-400">{errors.email.message}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full py-3 px-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all disabled:opacity-50"
        >
          Send Reset Instructions
        </button>
      </form>

      <Link
        href="/login"
        className="inline-flex items-center justify-center w-full py-3 px-4 border border-slate-700 text-slate-300 font-medium rounded-lg hover:bg-slate-800 hover:border-slate-600 transition-all"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Login
      </Link>
    </motion.div>
  );
}
