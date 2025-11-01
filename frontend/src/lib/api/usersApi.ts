import { apiClient } from "./apiClient";
import { User } from "@/types/auth";

const USERS_BASE = "/api/v1/users/";

export interface UserListParams {
  page?: number;
  size?: number;
  search?: string;
  created_after?: string;
  role?: string;
  is_active?: boolean;
  email_verified?: boolean;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export interface UserListResponse {
  items: User[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface CreateUserRequest {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  phone?: string;
  department?: string;
  job_title?: string;
  is_active: boolean;
  role_ids: number[];
}

export interface UpdateUserRequest {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  department?: string;
  job_title?: string;
  is_active?: boolean;
  role_ids?: number[];
}

export interface UpdateUserRolesRequest {
  role_ids: number[];
}

export interface PendingRegistration {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  department: string;
  job_title: string;
  created_at: string;
  status: "pending" | "approved" | "rejected";
}

export interface PendingRegistrationsResponse {
  items: PendingRegistration[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface UserActivityLog {
  id: number;
  user_id: number;
  action: string;
  ip_address: string;
  user_agent: string;
  timestamp: string;
  details: Record<string, unknown>;
}

export interface AuditLog {
  id: number;
  admin_id: number;
  admin_email: string;
  action: string;
  target_user_id: number | null;
  target_user_email: string | null;
  ip_address: string;
  timestamp: string;
  details: Record<string, unknown>;
}

export const usersApi = {
  // Get all users with filters and pagination
  getUsers: async (params?: UserListParams): Promise<UserListResponse> => {
    const response = await apiClient.get<UserListResponse>(USERS_BASE, {
      params,
    });
    return response.data;
  },

  // Get single user by ID
  getUserById: async (id: number): Promise<User> => {
    const response = await apiClient.get<User>(`${USERS_BASE}${id}`);
    return response.data;
  },

  // Create new user
  // TODO: Ensure temp passwords are being set after admin creates user
  createUser: async (data: CreateUserRequest): Promise<{ user: User }> => {
    const response = await apiClient.post<{ user: User }>(USERS_BASE, data);
    return response.data;
  },

  // Update user details
  updateUser: async (
    id: number,
    data: UpdateUserRequest,
  ): Promise<{ detail: string; user: User }> => {
    const response = await apiClient.put<{ detail: string; user: User }>(
      `${USERS_BASE}${id}`,
      data,
    );
    return response.data;
  },

  // Delete user
  deleteUser: async (id: number): Promise<{ detail: string }> => {
    const response = await apiClient.delete<{ detail: string }>(
      `${USERS_BASE}${id}`,
    );
    return response.data;
  },

  // Activate user
  activateUser: async (id: number): Promise<{ detail: string }> => {
    const response = await apiClient.post<{ detail: string }>(
      `${USERS_BASE}${id}/activate`,
    );
    return response.data;
  },

  // Deactivate user
  deactivateUser: async (id: number): Promise<{ detail: string }> => {
    const response = await apiClient.post<{ detail: string }>(
      `${USERS_BASE}${id}/deactivate`,
    );
    return response.data;
  },

  // Update user roles
  updateUserRoles: async (
    id: number,
    data: UpdateUserRolesRequest,
  ): Promise<{ detail: string; user: User }> => {
    const response = await apiClient.put<{ detail: string; user: User }>(
      `${USERS_BASE}${id}/roles`,
      data,
    );
    return response.data;
  },

  // Force password reset
  forcePasswordReset: async (id: number): Promise<{ detail: string }> => {
    const response = await apiClient.post<{ detail: string }>(
      `${USERS_BASE}${id}/force-password-reset`,
    );
    return response.data;
  },

  // Get pending registrations
  getPendingRegistrations: async (
    page: number = 1,
    size: number = 20,
  ): Promise<PendingRegistrationsResponse> => {
    const response = await apiClient.get<PendingRegistrationsResponse>(
      `${USERS_BASE}pending`,
      { params: { page, size } },
    );
    return response.data;
  },

  // Approve registration
  approveRegistration: async (id: number): Promise<{ detail: string }> => {
    const response = await apiClient.post<{ detail: string }>(
      `${USERS_BASE}pending/${id}/approve`,
    );
    return response.data;
  },

  // Reject registration
  rejectRegistration: async (
    id: number,
    reason?: string,
  ): Promise<{ detail: string }> => {
    const response = await apiClient.post<{ detail: string }>(
      `${USERS_BASE}pending/${id}/reject`,
      { reason },
    );
    return response.data;
  },

  // Get user activity logs
  getUserActivityLogs: async (
    userId: number,
    page: number = 1,
    size: number = 50,
  ): Promise<{ logs: UserActivityLog[]; total: number }> => {
    const response = await apiClient.get<{
      logs: UserActivityLog[];
      total: number;
    }>(`${USERS_BASE}${userId}/activity`, {
      params: { page, size },
    });
    return response.data;
  },

  getAuditLogs: async (
    page: number = 1,
    size: number = 50,
  ): Promise<{ logs: AuditLog[]; total: number }> => {
    const response = await apiClient.get<{ logs: AuditLog[]; total: number }>(
      `/api/v1/admin/audit-logs`,
      { params: { page, size } },
    );
    return response.data;
  },

  // Export users to CSV
  exportUsers: async (params?: UserListParams): Promise<Blob> => {
    const response = await apiClient.get(`${USERS_BASE}export`, {
      params,
      responseType: "blob",
    });
    return response.data;
  },
};
