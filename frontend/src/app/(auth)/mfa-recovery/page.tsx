"use client";

import { Suspense } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { useCompleteMfaRecoveryMutation } from "@/hooks/useAuthMutations";
import { normalizeError } from "@/lib/api/apiClient";
import { motion } from "framer-motion";
import { CheckCircle, Loader2, XCircle } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

type RecoveryState = "processing" | "success" | "error";

export default function MfaRecoveryPage() {
  return (
    <Suspense fallback={<Skeleton className="h-96 w-full" />}>
      <MfaRecoveryPageContent />
    </Suspense>
  );
}

export function MfaRecoveryPageContent() {
  const REDIRECT_DELAY_MS = 3000;

  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");
  const [recoveryState, setRecoveryState] =
    useState<RecoveryState>("processing");
  const [errorMessage, setErrorMessage] = useState("");
  const { mutateAsync: completeMfaRecovery } = useCompleteMfaRecoveryMutation();

  useEffect(() => {
    const runMfaRecovery = async () => {
      if (!token) {
        setRecoveryState("error");
        setErrorMessage("Invalid recovery link");
        return;
      }

      try {
        await completeMfaRecovery({ mfa_recovery_token: token });
        setRecoveryState("success");
        toast.success("MFA has been disabled successfully");

        setTimeout(() => {
          router.push("/login");
        }, REDIRECT_DELAY_MS);
      } catch (error) {
        setRecoveryState("error");
        setErrorMessage(normalizeError(error).message);
        toast.error("Recovery failed");
      }
    };

    runMfaRecovery();
  }, [token, router, completeMfaRecovery]);

  const renderContent = () => {
    switch (recoveryState) {
      case "processing":
        return (
          <div className="space-y-6 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4">
              <Loader2 className="w-10 h-10 text-blue-400 animate-spin" />
            </div>
            <h2 className="text-3xl font-bold text-white">
              Processing Recovery
            </h2>
            <p className="text-gray-400">
              Please wait while we process your MFA recovery...
            </p>
          </div>
        );

      case "success":
        return (
          <div className="space-y-6 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-500/10 border border-green-500/20 mb-4">
              <CheckCircle className="w-10 h-10 text-green-400" />
            </div>
            <h2 className="text-3xl font-bold text-white">Recovery Complete</h2>
            <p className="text-gray-400">
              MFA has been disabled for your account.
            </p>

            <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4">
              <p className="text-green-400 text-sm">
                You can now log in without MFA. Redirecting to login...
              </p>
            </div>

            <Link
              href="/login"
              className="inline-block w-full py-3 px-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-medium rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all"
            >
              Go to Login
            </Link>
          </div>
        );

      case "error":
        return (
          <div className="space-y-6 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-500/10 border border-red-500/20 mb-4">
              <XCircle className="w-10 h-10 text-red-400" />
            </div>
            <h2 className="text-3xl font-bold text-white">Recovery Failed</h2>
            <p className="text-gray-400">{errorMessage}</p>

            <div className="space-y-3">
              <Link
                href="/mfa-recovery/request"
                className="inline-block w-full py-3 px-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all"
              >
                Request New Recovery Link
              </Link>
              <Link
                href="/login"
                className="inline-block w-full py-3 px-4 border border-slate-700 text-slate-300 font-medium rounded-lg hover:bg-slate-800 hover:border-slate-600 transition-all"
              >
                Back to Login
              </Link>
            </div>
          </div>
        );
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {renderContent()}
    </motion.div>
  );
}
