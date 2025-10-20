"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import Link from "next/link";
import { Shield, Loader2, ArrowLeft } from "lucide-react";
import { useVerifyMfaMutation } from "@/hooks/useAuthMutations";
import { useAuth } from "@/contexts/AuthContext";
import { VerifyMfaRequestSchema, type VerifyMfaRequest } from "@/types/auth";
import { normalizeError } from "@/lib/api/apiClient";
import { toast } from "sonner";

export default function VerifyMfaPage() {
  const router = useRouter();
  const { login, getMfaChallengeToken, clearMfaChallengeToken } = useAuth();
  const verifyMutation = useVerifyMfaMutation();
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<VerifyMfaRequest>({
    resolver: zodResolver(VerifyMfaRequestSchema),
  });

  const code = watch("code");

  useEffect(() => {
    // Check if MFA challenge token exists
    const mfaToken = getMfaChallengeToken();
    if (!mfaToken) {
      router.push("/login");
    }

    // Auto-focus input
    inputRef.current?.focus();
  }, [router, getMfaChallengeToken]);

  const onSubmit = async (data: VerifyMfaRequest) => {
    const mfaToken = getMfaChallengeToken();

    if (!mfaToken) {
      router.push("/login");
      return;
    }

    try {
      const response = await verifyMutation.mutateAsync({
        code: data,
        mfaChallengeToken: mfaToken,
      });

      if (response.access_token && response.refresh_token) {
        clearMfaChallengeToken();
        login(response.access_token, response.refresh_token);
        router.push("/dashboard");
      }
    } catch (error) {
      const normalizedError = normalizeError(error);
      if (normalizedError.statusCode === 400) {
        toast.error(`Verification Failed: ${normalizeError(error).message}`);
      } else if (
        normalizedError.statusCode === 401 ||
        normalizedError.statusCode === 403
      ) {
        toast.error("MFA challenge expired or invalid. Please log in again.");
        clearMfaChallengeToken();
        router.push("/login");
      } else if (normalizedError.statusCode === 429) {
        toast.error("Too many attempts. Please wait and try again later.");
      } else {
        toast.error(
          `An unexpected error occurred: ${normalizeError(error).message}`,
        );
      }
    }
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4">
          <Shield className="w-8 h-8 text-blue-400" />
        </div>
        <h2 className="text-3xl font-bold text-white">
          Two-Factor Authentication
        </h2>
        <p className="text-gray-400 mt-2">
          Enter the 6-digit code from your authenticator app
        </p>
      </motion.div>

      <motion.form
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-6"
      >
        <div>
          <label
            htmlFor="code"
            className="block text-sm font-medium text-gray-300 mb-3 text-center"
          >
            Authentication Code
          </label>
          <input
            id="code"
            type="text"
            inputMode="numeric"
            maxLength={6}
            {...register("code")}
            ref={(e) => {
              register("code").ref(e);
              inputRef.current = e;
            }}
            className="w-full px-4 py-4 bg-slate-800/50 border border-slate-700 rounded-lg text-white text-center text-3xl font-mono tracking-[0.5em] placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            placeholder="000000"
            autoComplete="one-time-code"
          />
          {errors.code && (
            <p className="mt-2 text-sm text-red-400 text-center">
              {errors.code.message}
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={verifyMutation.isPending || !code || code.length !== 6}
          className="w-full py-3 px-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {verifyMutation.isPending ? (
            <span className="flex items-center justify-center">
              <Loader2 className="animate-spin h-5 w-5 mr-2" />
              Verifying...
            </span>
          ) : (
            "Verify & Sign In"
          )}
        </button>

        <Link
          href="/login"
          className="flex items-center justify-center space-x-2 w-full py-2 text-sm text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to login</span>
        </Link>
      </motion.form>

      <div className="pt-4 border-t border-slate-700">
        <p className="text-sm text-gray-400 text-center">
          Lost access to your authenticator?{" "}
          <Link
            href="/mfa-recovery/request"
            className="text-blue-400 hover:text-blue-300 transition-colors"
          >
            Use recovery options
          </Link>
        </p>
      </div>
    </div>
  );
}
