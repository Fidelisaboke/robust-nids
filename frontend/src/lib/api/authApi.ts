import { apiClient } from "./apiClient";
import type {
  LoginRequest,
  LoginResponse,
  UserRegisterRequest,
  UserRegisterResponse,
  TokenResponse,
  VerifyMfaRequest,
  MfaSetupResponse,
  EnableMfaRequest,
  EnableMfaResponse,
  DisableMfaRequest,
  DisableMfaResponse,
  MfaRecoveryInitiate,
  MfaRecoveryComplete,
  MfaRecoveryResponse,
  User,
  ResetPasswordRequest,
  ChangePasswordRequest,
} from "@/types/auth";

const AUTH_BASE = "/api/v1/auth";

export const authApi = {
  // Login with credentials
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>(
      `${AUTH_BASE}/login`,
      data,
    );
    return response.data;
  },

  // Register a new user
  registerUser: async (
    data: UserRegisterRequest,
  ): Promise<UserRegisterResponse> => {
    const response = await apiClient.post<UserRegisterResponse>(
      `${AUTH_BASE}/register`,
      data,
    );
    return response.data;
  },

  // Request email verification
  requestEmailVerification: async (
    email: string,
  ): Promise<{ detail: string }> => {
    const response = await apiClient.post(`${AUTH_BASE}/verify-email/request`, {
      email,
    });
    return response.data;
  },

  // Verify email with token
  verifyEmail: async (token: string): Promise<{ detail: string }> => {
    const response = await apiClient.post(`${AUTH_BASE}/verify-email`, {
      token,
    });
    return response.data;
  },

  // Verify MFA code (requires mfa_challenge_token in Authorization header)
  verifyMfa: async (
    data: VerifyMfaRequest,
    mfaChallengeToken: string,
  ): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>(
      `${AUTH_BASE}/mfa/verify`,
      data,
      {
        headers: {
          Authorization: `Bearer ${mfaChallengeToken}`,
        },
      },
    );
    return response.data;
  },

  // Refresh access token
  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>(
      `${AUTH_BASE}/refresh`,
      {
        refresh_token: refreshToken,
      },
    );
    return response.data;
  },

  // Get current user info
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>(`${AUTH_BASE}/users/me`);
    return response.data;
  },

  // Setup MFA (get QR code and secret)
  setupMfa: async (): Promise<MfaSetupResponse> => {
    const response = await apiClient.get<MfaSetupResponse>(
      `${AUTH_BASE}/mfa/setup`,
    );
    return response.data;
  },

  // Enable MFA with verification code
  enableMfa: async (data: EnableMfaRequest): Promise<EnableMfaResponse> => {
    const response = await apiClient.post<EnableMfaResponse>(
      `${AUTH_BASE}/mfa/enable`,
      data,
    );
    return response.data;
  },

  // Disable MFA
  disableMfa: async (data: DisableMfaRequest): Promise<DisableMfaResponse> => {
    const response = await apiClient.post<DisableMfaResponse>(
      `${AUTH_BASE}/mfa/disable`,
      data,
    );
    return response.data;
  },

  // Initiate MFA recovery
  initiateMfaRecovery: async (
    data: MfaRecoveryInitiate,
  ): Promise<MfaRecoveryResponse> => {
    const response = await apiClient.post<MfaRecoveryResponse>(
      `${AUTH_BASE}/mfa/recovery/initiate`,
      data,
    );
    return response.data;
  },

  // Complete MFA recovery
  completeMfaRecovery: async (
    data: MfaRecoveryComplete,
  ): Promise<MfaRecoveryResponse> => {
    const response = await apiClient.post<MfaRecoveryResponse>(
      `${AUTH_BASE}/mfa/recovery/complete`,
      data,
    );
    return response.data;
  },

  // Forgot password
  forgotPassword: async (email: string): Promise<{ detail: string }> => {
    const response = await apiClient.post(`${AUTH_BASE}/forgot-password`, {
      email,
    });
    return response.data;
  },

  // Reset password
  resetPassword: async (
    data: ResetPasswordRequest,
  ): Promise<{ detail: string }> => {
    const response = await apiClient.post(`${AUTH_BASE}/reset-password`, data);
    return response.data;
  },

  // Change password
  changePassword: async (
    data: ChangePasswordRequest,
  ): Promise<{ detail: string }> => {
    const response = await apiClient.post(`${AUTH_BASE}/change-password`, data);
    return response.data;
  },

  // Logout (clear tokens)
  logout: async (): Promise<void> => {
    // If backend has logout endpoint, call it here
    // await apiClient.post(`${AUTH_BASE}/logout`);
  },
};
