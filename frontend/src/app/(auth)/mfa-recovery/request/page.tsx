"use client";

import { useInitiateMfaRecoveryMutation } from "@/hooks/useAuthMutations";
import { normalizeError } from "@/lib/api/apiClient";
import {
  MfaRecoveryInitiateSchema,
  type MfaRecoveryInitiate,
} from "@/types/auth";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { ArrowLeft, Loader2, Mail, Shield } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

export default function MfaRecoveryRequestPage() {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const initiateMfaRecoveryMutation = useInitiateMfaRecoveryMutation();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<MfaRecoveryInitiate>({
    resolver: zodResolver(MfaRecoveryInitiateSchema),
  });

  const onSubmit = async (data: MfaRecoveryInitiate) => {
    try {
      await initiateMfaRecoveryMutation.mutateAsync(data);
      setIsSubmitted(true);
      toast.success("If the email exists, a recovery link has been sent.");
    } catch (error) {
      toast.error(normalizeError(error).message);
    }
  };

  if (isSubmitted) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6 text-center"
      >
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4">
          <Mail className="w-10 h-10 text-blue-400" />
        </div>

        <h2 className="text-3xl font-bold text-white">Check Your Email</h2>
        <p className="text-gray-400 text-lg">
          We&apos;ve sent an MFA recovery link to your email address
        </p>

        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 space-y-4 text-left">
          <p className="text-gray-300">
            Follow the instructions in the email to recover access to your
            account. The recovery link will expire in{" "}
            {process.env.NEXT_PUBLIC_MFA_RECOVERY_EXPIRY_HOURS || 1} hour(s).
          </p>
        </div>

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

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-amber-500/10 border border-amber-500/20 mb-4">
          <Shield className="w-8 h-8 text-amber-400" />
        </div>
        <h2 className="text-3xl font-bold text-white">MFA Recovery</h2>
        <p className="text-gray-400 mt-2">
          Enter your email to receive MFA recovery instructions
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
              {...register("email")}
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
          className="w-full py-3 px-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white font-medium rounded-lg hover:from-amber-600 hover:to-orange-600 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all disabled:opacity-50"
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center">
              <Loader2 className="animate-spin h-5 w-5 mr-2" />
              Sending...
            </span>
          ) : (
            "Send Recovery Link"
          )}
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
