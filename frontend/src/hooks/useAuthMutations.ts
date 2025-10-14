import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { authApi } from "@/lib/api/authApi";
import type {
  LoginRequest,
  VerifyMfaRequest,
  EnableMfaRequest,
  DisableMfaRequest,
  MfaRecoveryInitiate,
  MfaRecoveryComplete,
} from "@/types/auth";

export const AUTH_QUERY_KEYS = {
  currentUser: ["auth", "currentUser"] as const,
  mfaSetup: ["auth", "mfaSetup"] as const,
};

// Login mutation
export const useLoginMutation = () => {
  return useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    retry: false,
  });
};

// Verify MFA mutation
export const useVerifyMfaMutation = () => {
  return useMutation({
    mutationFn: ({
      code,
      mfaChallengeToken,
    }: {
      code: VerifyMfaRequest;
      mfaChallengeToken: string;
    }) => authApi.verifyMfa(code, mfaChallengeToken),
    retry: false,
  });
};

// Setup MFA mutation
export const useSetupMfaMutation = () => {
  return useMutation({
    mutationFn: () => authApi.setupMfa(),
    retry: false,
  });
};

// Enable MFA mutation
export const useEnableMfaMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: EnableMfaRequest) => authApi.enableMfa(data),
    retry: false,
    onSuccess: () => {
      // Invalidate current user query to refresh MFA status
      queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEYS.currentUser });
    },
  });
};

// Disable MFA mutation
export const useDisableMfaMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DisableMfaRequest) => authApi.disableMfa(data),
    retry: false,
    onSuccess: () => {
      // Invalidate current user query to refresh MFA status
      queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEYS.currentUser });
    },
  });
};

// Initiate MFA recovery mutation
export const useInitiateMfaRecoveryMutation = () => {
  return useMutation({
    mutationFn: (data: MfaRecoveryInitiate) =>
      authApi.initiateMfaRecovery(data),
    retry: false,
  });
};

// Complete MFA recovery mutation
export const useCompleteMfaRecoveryMutation = () => {
  return useMutation({
    mutationFn: (data: MfaRecoveryComplete) =>
      authApi.completeMfaRecovery(data),
    retry: false,
  });
};

// Get current user query
export const useCurrentUser = (enabled = true) => {
  return useQuery({
    queryKey: AUTH_QUERY_KEYS.currentUser,
    queryFn: async () => {
      const token = sessionStorage.getItem("access_token");
      if (!token) throw new Error("No token found");
      return authApi.getCurrentUser();
    },
    enabled,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });
};

// Get MFA setup query
export const useMfaSetupQuery = () => {
  return useQuery({
    queryKey: ["mfa-setup"],
    queryFn: () => authApi.setupMfa(),
    retry: false,
  });
};
