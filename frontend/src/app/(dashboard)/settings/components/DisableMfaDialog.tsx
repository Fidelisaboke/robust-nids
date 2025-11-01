"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Loader2, AlertTriangle, Smartphone, Key } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { normalizeError } from "@/lib/api/apiClient";
import { useDisableMfaMutation } from "@/hooks/useAuthMutations";
import { VerifyMfaRequest, VerifyMfaRequestSchema } from "@/types/auth";

interface DisableMfaDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function DisableMfaDialog({
  open,
  onOpenChange,
  onSuccess,
}: DisableMfaDialogProps) {
  const [step, setStep] = useState<"confirm" | "verify">("confirm");
  const disableMfaMutation = useDisableMfaMutation();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<VerifyMfaRequest>({
    resolver: zodResolver(VerifyMfaRequestSchema),
  });

  const handleClose = () => {
    onOpenChange(false);
    setTimeout(() => {
      setStep("confirm");
      reset();
    }, 300);
  };

  const handleConfirm = () => {
    setStep("verify");
  };

  const onSubmit = async (data: VerifyMfaRequest) => {
    try {
      await disableMfaMutation.mutateAsync(data);

      toast.success("MFA has been disabled successfully");
      handleClose();
      onSuccess?.();
    } catch (error) {
      toast.error(normalizeError(error).message);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md bg-slate-800/95 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-0 overflow-hidden [&>button]:text-gray-400 [&>button]:hover:text-white [&>button]:hover:bg-slate-700 [&>button]:absolute [&>button]:right-4 [&>button]:top-4">
        <AnimatePresence mode="wait">
          {step === "confirm" ? (
            <motion.div
              key="confirm"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              <DialogHeader className="p-6 pb-4">
                <div className="flex items-center justify-between">
                  <DialogTitle className="text-xl font-bold text-white flex items-center space-x-3">
                    <div className="p-2 bg-amber-500/10 rounded-lg">
                      <AlertTriangle className="w-6 h-6 text-amber-400" />
                    </div>
                    <span>Disable Two-Factor Authentication</span>
                  </DialogTitle>
                </div>
                <DialogDescription className="text-gray-400 mt-2">
                  This action will remove the extra security layer from your
                  account.
                </DialogDescription>
              </DialogHeader>

              <div className="px-6 pb-6 space-y-4">
                {/* Security Warning */}
                <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <AlertTriangle className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" />
                    <div className="space-y-2">
                      <p className="text-amber-400 font-medium text-sm">
                        Security Impact
                      </p>
                      <ul className="text-amber-300 text-sm space-y-1">
                        <li>• Your account will be less secure</li>
                        <li>• Password-only authentication</li>
                        <li>• Requires verification code to proceed</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Verification Requirements */}
                <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-4">
                  <p className="text-gray-300 text-sm font-medium mb-2">
                    You&apos;ll need:
                  </p>
                  <div className="flex items-center space-x-3 text-sm text-gray-400">
                    <Smartphone className="w-4 h-4 text-blue-400" />
                    <span>Your authenticator app</span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-3 pt-2">
                  <button
                    onClick={handleConfirm}
                    className="flex-1 py-3 px-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white font-medium rounded-lg hover:from-amber-600 hover:to-orange-600 focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all"
                  >
                    Continue to Verify
                  </button>
                  <button
                    onClick={handleClose}
                    className="flex-1 py-3 px-4 bg-slate-700 text-gray-300 font-medium rounded-lg hover:bg-slate-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-slate-500 transition-all"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="verify"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              <DialogHeader className="p-6 pb-4">
                <div className="flex items-center justify-between">
                  <DialogTitle className="text-xl font-bold text-white flex items-center space-x-3">
                    <div className="p-2 bg-blue-500/10 rounded-lg">
                      <Key className="w-6 h-6 text-blue-400" />
                    </div>
                    <span>Verify Your Identity</span>
                  </DialogTitle>
                </div>
                <DialogDescription className="text-gray-400 mt-2">
                  Enter the 6-digit code from your authenticator app to disable
                  MFA.
                </DialogDescription>
              </DialogHeader>

              <form
                onSubmit={handleSubmit(onSubmit)}
                className="px-6 pb-6 space-y-4"
              >
                {/* Code Input */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-300">
                    Verification Code
                  </label>
                  <input
                    type="text"
                    inputMode="numeric"
                    maxLength={6}
                    {...register("code")}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white text-center text-2xl font-mono tracking-[0.5em] placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="000000"
                    autoComplete="one-time-code"
                  />
                  {errors.code && (
                    <p className="text-red-400 text-sm text-center">
                      {errors.code.message}
                    </p>
                  )}
                </div>

                {/* Help Text */}
                <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-3">
                  <p className="text-gray-400 text-sm text-center">
                    Open your authenticator app to get the 6-digit code
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-3 pt-2">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex-1 py-3 px-4 bg-gradient-to-r from-red-500 to-pink-500 text-white font-medium rounded-lg hover:from-red-600 hover:to-pink-600 focus:outline-none focus:ring-2 focus:ring-red-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? (
                      <span className="flex items-center justify-center">
                        <Loader2 className="animate-spin h-5 w-5 mr-2" />
                        Disabling...
                      </span>
                    ) : (
                      "Disable MFA"
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => setStep("confirm")}
                    disabled={isSubmitting}
                    className="flex-1 py-3 px-4 bg-slate-700 text-gray-300 font-medium rounded-lg hover:bg-slate-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-slate-500 transition-all disabled:opacity-50"
                  >
                    Back
                  </button>
                </div>
              </form>
            </motion.div>
          )}
        </AnimatePresence>
      </DialogContent>
    </Dialog>
  );
}
