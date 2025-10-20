"use client";

import { Suspense, useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { CheckCircle, XCircle, Loader2, Mail } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { useVerifyEmailMutation } from "@/hooks/useAuthMutations";
import { normalizeError } from "@/lib/api/apiClient";
import { Skeleton } from "@/components/ui/skeleton";

type VerificationState = "verifying" | "success" | "error";

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<Skeleton className="h-96 w-full" />}>
      <VerifyEmailPageContent />
    </Suspense>
  );
}

function VerifyEmailPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");
  const [verificationState, setVerificationState] =
    useState<VerificationState>("verifying");
  const [errorMessage, setErrorMessage] = useState<string>(
    "An unknown error occurred during verification.",
  );
  const verifyEmailMutation = useVerifyEmailMutation();

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token) {
        setVerificationState("error");
        toast.error("Invalid verification link.");
        setErrorMessage(
          "Invalid verification link. Please check your email and try again.",
        );
        return;
      }

      try {
        const response = await verifyEmailMutation.mutateAsync(token);
        setVerificationState("success");
        toast.success(response.detail);
        sessionStorage.removeItem("unverified_email");

        // Redirect to log in after 3 seconds
        setTimeout(() => {
          router.push("/login?verified=true");
        }, 3000);
      } catch (error) {
        const normalizedErrorMessage = normalizeError(error).message;
        setErrorMessage(normalizedErrorMessage);
        toast.error(`Verification error: ${normalizedErrorMessage}`);
        setVerificationState("error");
      }
    };

    void verifyEmail();
  }, [token, router, verifyEmailMutation]);

  const renderContent = () => {
    switch (verificationState) {
      case "verifying":
        return (
          <div className="space-y-6 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4">
              <Loader2 className="w-10 h-10 text-blue-400 animate-spin" />
            </div>

            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-white">
                Verifying Your Email
              </h1>
              <p className="text-gray-400 text-lg">
                Please wait while we verify your email address...
              </p>
            </div>
          </div>
        );

      case "success":
        return (
          <div className="space-y-6 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-500/10 border border-green-500/20 mb-4">
              <CheckCircle className="w-10 h-10 text-green-400" />
            </div>

            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-white">Email Verified!</h1>
              <p className="text-gray-400 text-lg">
                Your email has been successfully verified.
              </p>
            </div>

            <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4">
              <p className="text-green-400 text-sm">
                ✓ Your account is now fully activated. Redirecting to login...
              </p>
            </div>

            <Link
              href="/login"
              className="inline-block w-full py-3 px-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-medium rounded-lg hover:from-green-600 hover:to-emerald-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all"
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

            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-white">
                Verification Failed
              </h1>
              <p className="text-gray-400 text-lg">{errorMessage}</p>
            </div>

            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
              <p className="text-red-400 text-sm">
                The verification link may be expired or invalid.
              </p>
            </div>

            <div className="space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="w-full py-3 px-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all"
              >
                Try Again
              </button>

              <Link
                href="/verify-email/required"
                className="inline-flex items-center justify-center w-full py-3 px-4 border border-slate-700 text-slate-300 font-medium rounded-lg hover:bg-slate-800 hover:border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all"
              >
                <Mail className="w-4 h-4 mr-2" />
                Request New Verification Email
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
