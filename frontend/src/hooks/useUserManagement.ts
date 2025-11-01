import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  usersApi,
  UserListParams,
  CreateUserRequest,
  UpdateUserRequest,
} from "@/lib/api/usersApi";
import { toast } from "sonner";

// Query keys
export const userKeys = {
  all: ["users"] as const,
  lists: () => [...userKeys.all, "list"] as const,
  list: (params?: UserListParams) => [...userKeys.lists(), params] as const,
  details: () => [...userKeys.all, "detail"] as const,
  detail: (id: number) => [...userKeys.details(), id] as const,
  recent: (days: number) => [...userKeys.all, "recent", days] as const,
  pending: () => [...userKeys.all, "pending"] as const,
  activity: (userId: number) => [...userKeys.all, "activity", userId] as const,
  audit: () => [...userKeys.all, "audit"] as const,
};

// Get users list
export const useUsers = (params?: UserListParams) => {
  return useQuery({
    queryKey: userKeys.list(params),
    queryFn: () => usersApi.getUsers(params),
    staleTime: 30000, // 30 seconds
  });
};

// Get recent users
export const useRecentUsers = (days: number) => {
  const date = new Date();
  date.setDate(date.getDate() - days);
  const created_after = date.toISOString().split("T")[0];

  return useQuery({
    queryKey: userKeys.recent(days),
    queryFn: () => usersApi.getUsers({ created_after }),
  });
};

// Get single user
export const useUser = (id: number) => {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => usersApi.getUserById(id),
    enabled: !!id,
  });
};

// Create user mutation
export const useCreateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateUserRequest) => usersApi.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};

// Update user mutation
export const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateUserRequest }) =>
      usersApi.updateUser(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: userKeys.detail(variables.id),
      });
    },
  });
};

// Delete user mutation
export const useDeleteUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => usersApi.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};

// Get pending registrations
export const usePendingRegistrations = (
  page: number = 1,
  limit: number = 20,
) => {
  return useQuery({
    queryKey: [...userKeys.pending(), page, limit],
    queryFn: () => usersApi.getPendingRegistrations(page, limit),
    staleTime: 30000,
  });
};

// Get user activity logs
export const useUserActivity = (
  userId: number,
  page: number = 1,
  limit: number = 50,
) => {
  return useQuery({
    queryKey: [...userKeys.activity(userId), page, limit],
    queryFn: () => usersApi.getUserActivityLogs(userId, page, limit),
    enabled: !!userId,
  });
};

// Get audit logs
export const useAuditLogs = (page: number = 1, limit: number = 50) => {
  return useQuery({
    queryKey: [...userKeys.audit(), page, limit],
    queryFn: () => usersApi.getAuditLogs(page, limit),
    staleTime: 30000,
  });
};

// Activate user mutation
export const useActivateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => usersApi.activateUser(id),
    onSuccess: (_, userId) => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      queryClient.invalidateQueries({ queryKey: userKeys.detail(userId) });
    },
  });
};

// Deactivate user mutation
export const useDeactivateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => usersApi.deactivateUser(id),
    onSuccess: (_, userId) => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      queryClient.invalidateQueries({ queryKey: userKeys.detail(userId) });
    },
  });
};

// Update user roles mutation
export const useUpdateUserRoles = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, role_ids }: { id: number; role_ids: number[] }) =>
      usersApi.updateUserRoles(id, { role_ids }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: userKeys.detail(variables.id),
      });
    },
  });
};

// Force password reset mutation
export const useForcePasswordReset = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => usersApi.forcePasswordReset(id),
    onSuccess: (_, userId) => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      queryClient.invalidateQueries({ queryKey: userKeys.detail(userId) });
    },
  });
};

// Approve registration mutation
export const useApproveRegistration = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => usersApi.approveRegistration(id),
    onSuccess: (data) => {
      toast.success(data.detail);
      queryClient.invalidateQueries({ queryKey: userKeys.pending() });
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};

// Reject registration mutation
export const useRejectRegistration = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, reason }: { id: number; reason?: string }) =>
      usersApi.rejectRegistration(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.pending() });
    },
  });
};

// Export users mutation
export const useExportUsers = () => {
  return useMutation({
    mutationFn: (params?: UserListParams) => usersApi.exportUsers(params),
    onSuccess: (blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `users-export-${new Date().toISOString().split("T")[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    },
  });
};
