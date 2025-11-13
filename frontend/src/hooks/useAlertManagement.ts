import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  alertsApi,
  AlertListParams,
  AssignAlertRequest,
  ResolveAlertRequest,
} from "@/lib/api/alertsApi";

// Query keys for alerts
export const alertKeys = {
  all: ["alerts"] as const,
  lists: () => [...alertKeys.all, "list"] as const,
  list: (params?: AlertListParams) => [...alertKeys.lists(), params] as const,
  details: () => [...alertKeys.all, "detail"] as const,
  detail: (id: number) => [...alertKeys.details(), id] as const,
};

// Get alerts list with filters and pagination
export const useAlerts = (params?: AlertListParams) => {
  return useQuery({
    queryKey: alertKeys.list(params),
    queryFn: () => alertsApi.getAlerts(params),
    staleTime: 30000, // 30 seconds
    refetchInterval: 30000, // Auto-refetch every 30 seconds
  });
};

// Get single alert by ID
export const useAlert = (id: number) => {
  return useQuery({
    queryKey: alertKeys.detail(id),
    queryFn: () => alertsApi.getAlertById(id),
    enabled: !!id,
    staleTime: 30000,
  });
};

// Delete alert mutation
export const useDeleteAlert = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => alertsApi.deleteAlert(id),
    onSuccess: () => {
      // Invalidate all alert lists to refresh the data
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
    },
  });
};

// Assign alert to user mutation
export const useAssignAlert = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: AssignAlertRequest }) =>
      alertsApi.assignAlert(id, data),
    onSuccess: (_, variables) => {
      // Invalidate both the list and the specific alert detail
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: alertKeys.detail(variables.id),
      });
    },
  });
};

// Acknowledge alert mutation
export const useAcknowledgeAlert = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => alertsApi.acknowledgeAlert(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({ queryKey: alertKeys.detail(id) });
    },
  });
};

// Resolve alert mutation
export const useResolveAlert = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ResolveAlertRequest }) =>
      alertsApi.resolveAlert(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: alertKeys.detail(variables.id),
      });
    },
  });
};
