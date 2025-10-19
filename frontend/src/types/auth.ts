import { z } from "zod";

// ===== Request DTOs =====

export const LoginRequestSchema = z.object({
  email: z.email("Invalid email address").max(255),
  password: z.string().min(1, "Password is required").max(255),
});

export type LoginRequest = z.infer<typeof LoginRequestSchema>;

export const VerifyMfaRequestSchema = z.object({
  code: z
    .string()
    .length(6, "Code must be 6 digits")
    .regex(/^\d{6}$/, "Code must contain only digits"),
});

export type VerifyMfaRequest = z.infer<typeof VerifyMfaRequestSchema>;

export const EnableMfaRequestSchema = z.object({
  verification_code: z
    .string()
    .length(6, "Code must be 6 digits")
    .regex(/^\d{6}$/, "Code must contain only digits"),
  temp_secret: z
    .string()
    .min(1, "Temporary secret is required")
    .max(255)
    .optional(),
});

export type EnableMfaRequest = z.infer<typeof EnableMfaRequestSchema>;

export const DisableMfaRequestSchema = z.object({
  code: z
    .string()
    .length(6, "Code must be 6 digits")
    .regex(/^\d{6}$/, "Code must contain only digits"),
});

export type DisableMfaRequest = z.infer<typeof DisableMfaRequestSchema>;

export const MfaRecoveryInitiateSchema = z.object({
  email: z.email("Invalid email address").max(255),
});

export type MfaRecoveryInitiate = z.infer<typeof MfaRecoveryInitiateSchema>;

export const MfaRecoveryCompleteSchema = z.object({
  mfa_recovery_token: z.string().min(1, "Recovery token is required").max(500),
});

export type MfaRecoveryComplete = z.infer<typeof MfaRecoveryCompleteSchema>;

export const ResetPasswordRequestSchema = z
  .object({
    token: z.string().min(1, "Token is required").max(500),
    new_password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .max(128),
    confirm_password: z
      .string()
      .min(8, "Confirm Password must be at least 8 characters")
      .max(128),
    mfa_code: z
      .string()
      .length(6, "Code must be 6 digits")
      .regex(/^\d{6}$/, "Code must contain only digits")
      .optional(),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords do not match.",
    path: ["confirm_password"],
  });

export type ResetPasswordRequest = z.infer<typeof ResetPasswordRequestSchema>;

// ===== Response DTOs =====

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface MFARequiredResponse {
  mfa_required: boolean;
  mfa_challenge_token: string;
}

export interface EmailVerificationRequiredResponse {
  email_verified: boolean;
  email: string;
  detail: string;
}

export type LoginResponse =
  | TokenResponse
  | MFARequiredResponse
  | EmailVerificationRequiredResponse;

export interface MfaSetupResponse {
  secret: string;
  qr_code: string;
  totp_uri: string;
}

export interface EnableMfaResponse {
  backup_codes: string[];
  detail: string;
}

export interface DisableMfaResponse {
  detail: string;
}

export interface MfaRecoveryResponse {
  detail: string;
}

export interface UserRole {
  id: number;
  name: string;
  description: string | null;
}

export interface UserPreferences {
  dashboard: {
    default_view: string;
    refresh_interval: number;
    theme: string;
  };
  notifications: {
    email: boolean;
    browser: boolean;
    critical_alerts: boolean;
    high_priority: boolean;
    medium_priority: boolean;
  };
  privacy: {
    show_online_status: boolean;
    share_analytics: boolean;
  };
}

export interface User {
  id: number;
  email: string;
  mfa_enabled: boolean;
  mfa_configured_at: string;
  mfa_method: string;
  username: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  department: string;
  job_title: string;
  timezone: string;
  preferences: UserPreferences;
  profile_completed: boolean;
  last_profile_update: string | null;
  email_verified: boolean;
  email_verified_at: string | null;
  phone_verified: boolean;
  phone_verified_at: string | null;
  roles: UserRole[];
  created_at: string;
  last_login: string;
  is_active: boolean;
}
