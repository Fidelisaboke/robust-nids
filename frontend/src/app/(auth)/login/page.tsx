"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import Link from "next/link";
import { Mail, Lock, Loader2 } from "lucide-react";
import { useLoginMutation } from "@/hooks/useAuthMutations";
import { useAuth } from "@/contexts/AuthContext";
import { LoginRequestSchema, type LoginRequest } from "@/types/auth";
import { normalizeError } from "@/lib/api/apiClient";
import { toast } from "sonner";

export default function LoginPage() {
  const router = useRouter();
  const { login, saveMfaChallengeToken, user } = useAuth();
  const loginMutation = useLoginMutation();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginRequest>({
    resolver: zodResolver(LoginRequestSchema),
  });

  const onSubmit = async (data: LoginRequest) => {
    try {
      const response = await loginMutation.mutateAsync(data);

      // Check if email is verified
      if ("email_verified" in response && !response.email_verified) {
        toast.info("Please verify your email before logging in.");
        sessionStorage.setItem("unverified_email", response.email);
        router.push(
          `/verify-email/required?email=${encodeURIComponent(response.email)}`,
        );
        return;
      }
      // Check if MFA is required
      if ("mfa_required" in response && response.mfa_required) {
        saveMfaChallengeToken(response.mfa_challenge_token);
        router.push("/login/verify-mfa");
      } else if ("access_token" in response && "refresh_token" in response) {
        // Login successful without MFA
        login(response.access_token, response.refresh_token);
        router.push("/dashboard");
      }
    } catch (error) {
      toast.error(`Login failed: ${normalizeError(error).message}`);
    }
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-3xl font-bold text-white">Sign In</h2>
        <p className="text-gray-400 mt-2">
          Enter your credentials to access your account
        </p>
      </motion.div>

      <motion.form
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-5"
      >
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-gray-300 mb-2"
          >
            Email Address
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              id="email"
              type="email"
              {...register("email")}
              className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="admin@example.com"
            />
          </div>
          {errors.email && (
            <p className="mt-1 text-sm text-red-400">{errors.email.message}</p>
          )}
        </div>

        <div>
          <label
            htmlFor="password"
            className="block text-sm font-medium text-gray-300 mb-2"
          >
            Password
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              id="password"
              type="password"
              {...register("password")}
              className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
          </div>
          {errors.password && (
            <p className="mt-1 text-sm text-red-400">
              {errors.password.message}
            </p>
          )}
        </div>

        <div className="flex items-center justify-between">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              className="w-4 h-4 rounded border-gray-600 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-900 bg-slate-800"
            />
            <span className="ml-2 text-sm text-gray-400">Remember me</span>
          </label>

          <Link
            href="/reset-password"
            className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            Forgot password?
          </Link>
        </div>

        <button
          type="submit"
          disabled={loginMutation.isPending}
          className="w-full py-3 px-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loginMutation.isPending ? (
            <span className="flex items-center justify-center">
              <Loader2 className="animate-spin h-5 w-5 mr-2" />
              Signing in...
            </span>
          ) : (
            "Sign In"
          )}
        </button>
      </motion.form>

      <div className="pt-4 border-t border-slate-700">
        <p className="text-sm text-gray-400 text-center">
          Need help accessing your account?{" "}
          <Link
            href="/verify-email"
            className="text-blue-400 hover:text-blue-300 transition-colors"
          >
            Contact Support
          </Link>
        </p>
      </div>
    </div>
  );
}
