import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  rolesApi,
  RoleListParams,
  UpdateRoleRequest,
} from "@/lib/api/rolesApi";

// Query keys for roles
export const roleKeys = {
  all: ["roles"] as const,
  lists: () => [...roleKeys.all, "list"] as const,
  list: (params?: RoleListParams) => [...roleKeys.lists(), params] as const,
  details: () => [...roleKeys.all, "detail"] as const,
  detail: (id: number) => [...roleKeys.details(), id] as const,
};

// Get roles list
export const useRoles = (params?: RoleListParams) => {
  return useQuery({
    queryKey: roleKeys.list(params),
    queryFn: () => rolesApi.getRoles(params),
    staleTime: 30000, // 30 seconds
  });
};

// Get single role
export const useRole = (id: number) => {
  return useQuery({
    queryKey: roleKeys.detail(id),
    queryFn: () => rolesApi.getRoleById(id),
    enabled: !!id,
  });
};

// Update role mutation
export const useUpdateRole = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateRoleRequest }) =>
      rolesApi.updateRole(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: roleKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: roleKeys.detail(variables.id),
      });
    },
  });
};

// Delete role mutation
export const useDeleteRole = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => rolesApi.deleteRole(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: roleKeys.lists() });
    },
  });
};
