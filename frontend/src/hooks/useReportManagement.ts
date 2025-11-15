import { User } from "@/types/auth";
import { apiClient } from "@/lib/api/apiClient";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { normalizeError } from "@/lib/api/apiClient";
import { ReportStatus } from "@/types/enums";

export interface Report {
  id: number;
  title: string;
  status: ReportStatus;
  parameters: {
    title: string;
    start_date: string;
    end_date: string;
    severity?: string;
    status?: string;
    search?: string;
  };
  file_path: string | null;
  owner: User;
  created_at: string;
  updated_at: string;
}

export interface PaginatedReports {
  items: Report[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ReportCreateRequest {
  title: string;
  start_date: string;
  end_date: string;
  severity?: string;
  status?: string;
  search?: string;
}

export interface ReportListParams {
  page?: number;
  size?: number;
  search?: string;
  status?: string;
  sort_by?: string;
  sort_direction?: string;
}

const API_BASE = "/api/v1/reports";

/**
 * Fetches a paginated list of reports.
 * Polls every 5 seconds to check for new/updated reports.
 */
export const useReports = (params: ReportListParams) => {
  const {
    page = 1,
    size = 10,
    search,
    status,
    sort_by = "created_at",
    sort_direction = "desc",
  } = params;

  return useQuery<PaginatedReports, Error>({
    // queryKey must include all filters to ensure uniqueness
    queryKey: ["reports", page, size, search, status, sort_by, sort_direction],
    queryFn: async () => {
      // Build query string from params
      const queryParams = new URLSearchParams({
        page: page.toString(),
        size: size.toString(),
        sort_by: sort_by,
        sort_direction: sort_direction,
      });
      if (search) queryParams.append("search", search);
      if (status) queryParams.append("status", status);

      const response = await apiClient.get<PaginatedReports>(
        `${API_BASE}/?${queryParams.toString()}`,
      );
      return response.data;
    },
    // Poll to check for 'READY' status on pending reports
    refetchInterval: 5000,
  });
};

/**
 * Mutation hook to create a new report generation job.
 */
export const useCreateReport = () => {
  const queryClient = useQueryClient();
  return useMutation<Report, Error, ReportCreateRequest>({
    mutationFn: async (reportData) => {
      const response = await apiClient.post<Report>(`${API_BASE}/`, reportData);
      return response.data;
    },
    onSuccess: () => {
      toast.success("Report generation started!");
      // Invalidate the reports query to show the new 'PENDING' report
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
    onError: (error) => {
      toast.error("Failed to start report", {
        description: normalizeError(error).message,
      });
    },
  });
};

/**
 * Function to trigger a report download.
 */
export const downloadReport = async (reportId: number, reportTitle: string) => {
  try {
    const response = await apiClient.get(`${API_BASE}/${reportId}/download`, {
      responseType: "blob", // Important: Tell axios to expect a file
    });

    // Create a URL for the blob and trigger download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;

    // Use the title from the report for a clean filename
    const filename = `${reportTitle.replace(/ /g, "_")}.csv`;
    link.setAttribute("download", filename);

    document.body.appendChild(link);
    link.click();

    // Clean up
    link.parentNode?.removeChild(link);
    window.URL.revokeObjectURL(url);

    toast.success("Report download started.");
  } catch (error) {
    toast.error("Download failed", {
      description: normalizeError(error).message,
    });
  }
};

/**
 * Function to delete a report.
 */
export const useDeleteReport = () => {
  const queryClient = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: async (reportId) => {
      await apiClient.delete(`${API_BASE}/${reportId}`);
    },
    onSuccess: () => {
      toast.success("Report deleted successfully.");
      // Invalidate the reports query to reflect deletion
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
    onError: (error) => {
      toast.error("Failed to delete report", {
        description: normalizeError(error).message,
      });
    },
  });
};
