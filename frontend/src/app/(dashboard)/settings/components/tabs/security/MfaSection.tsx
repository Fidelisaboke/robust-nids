"use client";

import { Shield, Loader2, AlertCircle } from "lucide-react";
import { User } from "@/types/auth";
import { useSetupMfaMutation } from "@/hooks/useAuthMutations";
import { normalizeError } from "@/lib/api/apiClient";
import { useRouter } from "next/navigation";

interface MfaSectionProps {
  user: User | undefined;
  onDisableMfa: () => void;
}

export function MfaSection({ user, onDisableMfa }: MfaSectionProps) {
  const router = useRouter();
  const setupMfaMutation = useSetupMfaMutation();

  const handleEnableMfa = async () => {
    try {
      router.push("/totp-setup");
    } catch (error) {
      console.error("Failed to setup MFA:", normalizeError(error));
    }
  };

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-blue-500/10 rounded-lg">
            <Shield className="w-6 h-6 text-blue-400" />
          </div>

          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white mb-2">
              Two-Factor Authentication
            </h3>
            <p className="text-gray-400 mb-4">
              Add an extra layer of security to your account by requiring a code
              from your authenticator app.
            </p>

            {/* MFA Status */}
            {user?.mfa_enabled ? (
              <div className="space-y-3 mb-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span className="text-sm text-emerald-400 font-medium">
                    Enabled
                  </span>
                </div>

                <div className="text-sm text-gray-400 space-y-1">
                  <p>
                    <span className="text-gray-300 font-medium">Method:</span>{" "}
                    {user?.mfa_method?.toUpperCase() || "TOTP"}
                  </p>
                  {user?.mfa_configured_at && (
                    <p>
                      <span className="text-gray-300 font-medium">
                        Configured on:
                      </span>{" "}
                      {new Date(user?.mfa_configured_at).toLocaleString()}
                    </p>
                  )}
                </div>

                <button
                  onClick={onDisableMfa}
                  className="px-6 py-2.5 bg-red-600/90 text-white font-medium rounded-lg hover:bg-red-700 transition-all"
                >
                  Disable MFA
                </button>
              </div>
            ) : (
              <>
                <div className="flex items-center space-x-2 mb-4">
                  <div className="w-2 h-2 rounded-full bg-amber-400" />
                  <span className="text-sm text-gray-400">Not Enabled</span>
                </div>

                {setupMfaMutation.isError && (
                  <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 flex items-start space-x-2">
                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-red-400 text-sm font-medium">
                        Setup Failed
                      </p>
                      <p className="text-red-300 text-sm mt-1">
                        {normalizeError(setupMfaMutation.error).message}
                      </p>
                    </div>
                  </div>
                )}

                <button
                  onClick={handleEnableMfa}
                  disabled={setupMfaMutation.isPending}
                  className="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {setupMfaMutation.isPending ? (
                    <span className="flex items-center">
                      <Loader2 className="animate-spin h-4 w-4 mr-2" />
                      Setting up...
                    </span>
                  ) : (
                    "Enable MFA"
                  )}
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
