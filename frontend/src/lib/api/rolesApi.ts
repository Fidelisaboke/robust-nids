import { Permission } from "@/types/auth";
import { apiClient } from "./apiClient";

export interface Role {
  id: number;
  name: string;
  description: string | null;
  permissions: Permission[];
}

export interface RoleListParams {
  page?: number;
  size?: number;
  search?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export interface RoleListResponse {
  items: Role[];
  page: number;
  pages: number;
  size: number;
  total: number;
}

export interface CreateRoleRequest {
  name: string;
  description?: string;
  permissions?: string[];
}

export interface UpdateRoleRequest {
  name?: string;
  description?: string;
  permissions?: string[];
}

const ROLES_BASE = "/api/v1/roles/";

export const rolesApi = {
  // Get all roles with filters and pagination
  getRoles: async (params?: RoleListParams): Promise<RoleListResponse> => {
    const response = await apiClient.get<RoleListResponse>(ROLES_BASE, {
      params,
    });
    return response.data;
  },

  // Get single role by ID
  getRoleById: async (id: number): Promise<Role> => {
    const response = await apiClient.get<Role>(`${ROLES_BASE}${id}`);
    return response.data;
  },

  // Create a new role
  createRole: async (data: CreateRoleRequest): Promise<Role> => {
    const response = await apiClient.post<Role>(ROLES_BASE, data);
    return response.data;
  },

  // Update role details
  updateRole: async (id: number, data: UpdateRoleRequest): Promise<Role> => {
    const response = await apiClient.put<Role>(`${ROLES_BASE}${id}`, data);
    return response.data;
  },

  // Delete role
  deleteRole: async (id: number): Promise<{ detail: string }> => {
    const response = await apiClient.delete<{ detail: string }>(
      `${ROLES_BASE}${id}`,
    );
    return response.data;
  },
};
