"use client";

import { motion } from "framer-motion";
import { Mail, AlertCircle, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useState, useEffect, useCallback, Suspense } from "react";
import { toast } from "sonner";
import { useRequestEmailVerificationMutation } from "@/hooks/useAuthMutations";
import { normalizeError } from "@/lib/api/apiClient";
import { useSearchParams } from "next/navigation";
import { Skeleton } from "@/components/ui/skeleton";

export default function VerificationRequiredPage() {
  return (
    <Suspense fallback={<Skeleton className="h-96 w-full" />}>
      <VerificationRequiredPageContent />
    </Suspense>
  );
}

function VerificationRequiredPageContent() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email");
  const [isResending, setIsResending] = useState(false);
  const { mutateAsync: requestEmailVerification } =
    useRequestEmailVerificationMutation();

  const handleResendVerification = useCallback(async () => {
    if (!email) return;

    setIsResending(true);
    try {
      const response = await requestEmailVerification(email);
      toast.success(response.detail);
    } catch (error) {
      const normalizedError = normalizeError(error);
      toast.error(normalizedError.message);
    } finally {
      setIsResending(false);
    }
  }, [email, requestEmailVerification]);

  // Send email verification request when first landing on the page
  useEffect(() => {
    void handleResendVerification();
  }, [handleResendVerification]);

  // Invalid state if no email is provided
  if (!email) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="space-y-6 text-center"
      >
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-500/10 border border-red-500/20 mb-4">
          <AlertCircle className="w-10 h-10 text-red-400" />
        </div>
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-white">Invalid Page</h1>
          <p className="text-gray-400 text-lg">No email address was found.</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 space-y-4 text-left">
          <p className="text-gray-300">
            Please return to the login page and try signing in again.
          </p>
        </div>
        <div className="space-y-4 pt-4">
          <Link
            href="/login"
            className="inline-flex items-center justify-center w-full py-3 px-4 border border-slate-700 text-slate-300 font-medium rounded-lg hover:bg-slate-800 hover:border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Login
          </Link>
        </div>
      </motion.div>
    );
  }

  // Main verified email required state
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6 text-center"
    >
      {/* Alert Icon */}
      <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-amber-500/10 border border-amber-500/20 mb-4">
        <AlertCircle className="w-10 h-10 text-amber-400" />
      </div>

      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-white">Verify Your Email</h1>
        <p className="text-gray-400 text-lg">
          Please verify your email address before signing in
        </p>
      </div>

      {/* Email Display */}
      {email && (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <p className="text-white font-medium">Email sent to:</p>
          <p className="text-blue-400 font-mono text-sm mt-1">{email}</p>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 space-y-4 text-left">
        <p className="text-gray-300">
          We&apos;ve sent a verification link to your email address. You must
          verify your email before you can access your account.
        </p>
      </div>

      {/* Action Buttons */}
      <div className="space-y-4 pt-4">
        <button
          onClick={() => handleResendVerification(email)}
          disabled={isResending || !email}
          className="w-full py-3 px-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white font-medium rounded-lg hover:from-amber-600 hover:to-orange-600 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Mail className="w-5 h-5 inline mr-2" />
          {isResending ? "Sending..." : "Resend Verification Email"}
        </button>

        <Link
          href="/login"
          className="inline-flex items-center justify-center w-full py-3 px-4 border border-slate-700 text-slate-300 font-medium rounded-lg hover:bg-slate-800 hover:border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Login
        </Link>
      </div>
    </motion.div>
  );
}
