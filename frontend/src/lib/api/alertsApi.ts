import { apiClient } from "./apiClient";

export interface Alert {
  id: number;
  title: string;
  severity: "critical" | "high" | "medium" | "low";
  category: string;
  src_ip: string;
  dst_ip: string;
  dst_port: number;
  flow_timestamp: string;
  status: "active" | "investigating" | "resolved" | "acknowledged";
  description: string | null;
  model_output: {
    timestamp: string;
    src_ip: string;
    dst_ip: string;
    binary: {
      label: string;
      confidence: number;
      is_malicious: boolean;
    };
    multiclass: {
      label: string;
      confidence: number;
      probabilities: Record<string, number>;
    };
    anomaly: {
      is_anomaly: boolean;
      anomaly_score: number;
      threshold: number;
    };
    threat_level: string;
    id: null;
  };
  assigned_to_id: number | null;
  assigned_user: {
    id: number;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    department: string;
    job_title: string;
  } | null;
  created_at: string;
  updated_at: string;
}

export interface AlertListParams {
  start_date?: string;
  end_date?: string;
  severity?: "critical" | "high" | "medium" | "low";
  status?: "active" | "investigating" | "resolved" | "acknowledged";
  page?: number;
  size?: number;
}

export interface AlertListResponse {
  items: Alert[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface AssignAlertRequest {
  user_id: number;
}

export interface ResolveAlertRequest {
  notes: string;
}

export interface AlertsSummaryResponse {
  total_alerts: number;
  by_severity: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  by_status: {
    active: number;
    investigating: number;
    resolved: number;
    acknowledged: number;
  };
  // by_category: e.g., [{"category": "Bruteforce", "count": 10}]
  by_category: Array<{
    category: string;
    count: number;
  }>;
  // time_series: For a "alerts over time" chart
  time_series: Array<{
    timestamp: string;
    count: number;
  }>;
}

const ALERTS_BASE = "/api/v1/nids/alerts";

export const alertsApi = {
  // Get all alerts with filters and pagination
  getAlerts: async (params?: AlertListParams): Promise<AlertListResponse> => {
    const response = await apiClient.get<AlertListResponse>(ALERTS_BASE, {
      params,
    });
    return response.data;
  },

  // Get single alert by ID
  getAlertById: async (id: number): Promise<Alert> => {
    const response = await apiClient.get<Alert>(`${ALERTS_BASE}/${id}`);
    return response.data;
  },

  // Delete alert
  deleteAlert: async (id: number): Promise<void> => {
    await apiClient.delete(`${ALERTS_BASE}/${id}`);
  },

  // Assign alert to user
  assignAlert: async (id: number, data: AssignAlertRequest): Promise<Alert> => {
    const response = await apiClient.patch<Alert>(
      `${ALERTS_BASE}/${id}/assign`,
      data,
    );
    return response.data;
  },

  // Acknowledge alert
  acknowledgeAlert: async (id: number): Promise<Alert> => {
    const response = await apiClient.patch<Alert>(
      `${ALERTS_BASE}/${id}/acknowledge`,
    );
    return response.data;
  },

  // Resolve alert
  resolveAlert: async (
    id: number,
    data: ResolveAlertRequest,
  ): Promise<Alert> => {
    const response = await apiClient.patch<Alert>(
      `${ALERTS_BASE}/${id}/resolve`,
      data,
    );
    return response.data;
  },

  // Alerts summary
  getAlertsSummary: async (): Promise<AlertsSummaryResponse> => {
    const response = await apiClient.get<AlertsSummaryResponse>(
      `${ALERTS_BASE}/summary`,
    );
    return response.data;
  },
};
