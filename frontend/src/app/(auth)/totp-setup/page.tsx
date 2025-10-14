"use client";

import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, Copy, Check, Loader2, Download } from "lucide-react";
import Image from "next/image";
import {
  useMfaSetupQuery,
  useEnableMfaMutation,
} from "@/hooks/useAuthMutations";
import { EnableMfaRequestSchema, type EnableMfaRequest } from "@/types/auth";
import { normalizeError } from "@/lib/api/apiClient";
import { toast } from "sonner";

export default function TotpSetupPage() {
  const router = useRouter();
  const [copiedSecret, setCopiedSecret] = useState(false);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [showBackupCodes, setShowBackupCodes] = useState(false);
  const queryClient = useQueryClient();

  const { data: mfaSetup, isLoading } = useMfaSetupQuery();
  const enableMfaMutation = useEnableMfaMutation();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<EnableMfaRequest>({
    resolver: zodResolver(EnableMfaRequestSchema),
  });

  const copyToClipboard = async (text: string, type: "secret" | "code") => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === "secret") {
        setCopiedSecret(true);
        setTimeout(() => setCopiedSecret(false), 2000);
      } else {
        setCopiedCode(text);
        setTimeout(() => setCopiedCode(null), 2000);
      }
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  const downloadBackupCodes = () => {
    const content = backupCodes.join("\n");
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "nids-backup-codes.txt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const onSubmit = async (data: EnableMfaRequest) => {
    if (!mfaSetup) return;

    try {
      const response = await enableMfaMutation.mutateAsync({
        verification_code: data.verification_code,
        temp_secret: mfaSetup.secret,
      });

      setBackupCodes(response.backup_codes);
      setShowBackupCodes(true);
    } catch (error) {
      const normalized = normalizeError(error);
      toast.error(normalized.message);
    }
  };

  const handleComplete = () => {
    router.push("/dashboard");
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    );
  }

  if (!mfaSetup) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <AnimatePresence mode="wait">
        {!showBackupCodes ? (
          <motion.div
            key="setup"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4">
                <Shield className="w-8 h-8 text-blue-400" />
              </div>
              <h2 className="text-3xl font-bold text-white">
                Set Up Two-Factor Authentication
              </h2>
              <p className="text-gray-400 mt-2">
                Scan the QR code with your authenticator app
              </p>
            </div>

            {/* QR Code */}
            <div className="bg-white p-6 rounded-xl mx-auto w-fit">
              <Image
                src={mfaSetup.qr_code}
                alt="MFA QR Code"
                width={256}
                height={256}
                className="w-64 h-64"
                priority
                unoptimized
              />
            </div>

            {/* Secret Key */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <p className="text-sm text-gray-400 mb-2">
                Or enter this code manually:
              </p>
              <div className="flex items-center justify-between bg-slate-900/50 rounded-lg p-3">
                <code className="text-white font-mono text-sm">
                  {mfaSetup.secret}
                </code>
                <button
                  type="button"
                  onClick={() => copyToClipboard(mfaSetup.secret, "secret")}
                  className="ml-3 p-2 text-gray-400 hover:text-white hover:bg-slate-700 rounded transition-colors"
                >
                  {copiedSecret ? (
                    <Check className="w-4 h-4 text-green-400" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Verification Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label
                  htmlFor="verification_code"
                  className="block text-sm font-medium text-gray-300 mb-2"
                >
                  Enter the 6-digit code from your authenticator app
                </label>
                <input
                  id="verification_code"
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  {...register("verification_code")}
                  className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white text-center text-2xl font-mono tracking-[0.5em] placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="000000"
                />
                {errors.verification_code && (
                  <p className="mt-2 text-sm text-red-400 text-center">
                    {errors.verification_code.message}
                  </p>
                )}
              </div>

              {/* Regenerate QR Code Button */}
              <button
                type="button"
                onClick={() =>
                  queryClient.invalidateQueries({ queryKey: ["mfa-setup"] })
                }
                className="text-sm text-blue-400 hover:underline"
              >
                Regenerate QR Code
              </button>

              <button
                type="submit"
                disabled={enableMfaMutation.isPending}
                className="w-full py-3 px-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {enableMfaMutation.isPending ? (
                  <span className="flex items-center justify-center">
                    <Loader2 className="animate-spin h-5 w-5 mr-2" />
                    Verifying...
                  </span>
                ) : (
                  "Enable Two-Factor Authentication"
                )}
              </button>
            </form>
          </motion.div>
        ) : (
          <motion.div
            key="backup"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/10 border border-green-500/20 mb-4">
                <Check className="w-8 h-8 text-green-400" />
              </div>
              <h2 className="text-3xl font-bold text-white">
                MFA Enabled Successfully!
              </h2>
              <p className="text-gray-400 mt-2">
                Save these backup codes in a secure location
              </p>
            </div>

            <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4">
              <p className="text-amber-400 text-sm font-medium">⚠️ Important</p>
              <p className="text-amber-300 text-sm mt-1">
                Each backup code can only be used once. Store them securely -
                you&apos;ll need them if you lose access to your authenticator
                app.
              </p>
            </div>

            {/* Backup Codes */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-gray-300">
                  Your Backup Codes
                </p>
                <button
                  type="button"
                  onClick={downloadBackupCodes}
                  className="flex items-center space-x-2 px-3 py-1.5 text-sm bg-slate-700 hover:bg-slate-600 text-white rounded transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {backupCodes.map((code, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between bg-slate-900/50 rounded-lg p-3"
                  >
                    <code className="text-white font-mono text-sm">{code}</code>
                    <button
                      type="button"
                      onClick={() => copyToClipboard(code, "code")}
                      className="ml-2 p-1.5 text-gray-400 hover:text-white hover:bg-slate-700 rounded transition-colors"
                    >
                      {copiedCode === code ? (
                        <Check className="w-3.5 h-3.5 text-green-400" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <button
              type="button"
              onClick={handleComplete}
              className="w-full py-3 px-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all"
            >
              Continue to Dashboard
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
