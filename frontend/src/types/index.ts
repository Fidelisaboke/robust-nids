export enum UserRole {
  ADMIN = "Administrator",
  ANALYST = "Security Analyst",
  OPERATOR = "Operator",
  VIEWER = "Viewer",
}

export enum UserStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TOTPVerifyRequest {
  code: string;
  sessionToken: string;
}

// Alert Types
export interface Alert {
  id: number;
  type: AlertType;
  severity: AlertSeverity;
  source: string;
  destination: string;
  protocol: string;
  timestamp: string;
  description: string;
  status: AlertStatus;
  affectedSystems: number;
  metadata?: Record<string, never>;
}

export enum AlertType {
  DDOS = "DDoS Attack",
  PORT_SCAN = "Port Scan",
  BRUTE_FORCE = "Brute Force",
  SQL_INJECTION = "SQL Injection",
  MALWARE = "Malware Detected",
  PHISHING = "Phishing Attempt",
  RANSOMWARE = "Ransomware",
  DATA_EXFILTRATION = "Data Exfiltration",
  UNAUTHORIZED_ACCESS = "Unauthorized Access",
}

export enum AlertSeverity {
  CRITICAL = "critical",
  HIGH = "high",
  MEDIUM = "medium",
  LOW = "low",
  INFO = "info",
}

export enum AlertStatus {
  ACTIVE = "active",
  INVESTIGATING = "investigating",
  BLOCKED = "blocked",
  RESOLVED = "resolved",
  FALSE_POSITIVE = "false_positive",
}

// Metric Types
export interface NetworkMetric {
  id: number;
  timestamp: string;
  totalTraffic: number;
  inboundTraffic: number;
  outboundTraffic: number;
  activeConnections: number;
  blockedRequests: number;
  throughput: number;
}

export interface SystemMetric {
  id: number;
  timestamp: string;
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  modelAccuracy: number;
  detectionRate: number;
  falsePositiveRate: number;
}

export interface ThreatMetric {
  type: string;
  count: number;
  trend: "up" | "down" | "stable";
  percentage: number;
}

// Report Types
export interface Report {
  id: number;
  title: string;
  type: ReportType;
  status: ReportStatus;
  createdBy: string;
  createdAt: string;
  period: string;
  format: ReportFormat;
  fileSize?: number;
  downloadUrl?: string;
}

export enum ReportType {
  DAILY = "daily",
  WEEKLY = "weekly",
  MONTHLY = "monthly",
  CUSTOM = "custom",
  INCIDENT = "incident",
  COMPLIANCE = "compliance",
}

export enum ReportStatus {
  GENERATING = "generating",
  READY = "ready",
  FAILED = "failed",
}

export enum ReportFormat {
  PDF = "pdf",
  CSV = "csv",
  JSON = "json",
  HTML = "html",
}

// Network Types
export interface NetworkNode {
  id: string;
  label: string;
  type: "device" | "server" | "router" | "firewall" | "endpoint";
  ip: string;
  status: "online" | "offline" | "warning";
  threats: number;
}

export interface NetworkConnection {
  source: string;
  target: string;
  traffic: number;
  protocol: string;
  status: "normal" | "suspicious" | "blocked";
}

// Audit Log Types
export interface AuditLog {
  id: number;
  timestamp: string;
  userId: number;
  userName: string;
  action: AuditAction;
  resource: string;
  details: string;
  ipAddress: string;
  userAgent: string;
}

export enum AuditAction {
  LOGIN = "login",
  LOGOUT = "logout",
  CREATE = "create",
  UPDATE = "update",
  DELETE = "delete",
  VIEW = "view",
  EXPORT = "export",
  CONFIG_CHANGE = "config_change",
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: ApiError[];
}

export interface ApiError {
  field?: string;
  message: string;
  code?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Filter Types
export interface AlertFilters {
  severity?: AlertSeverity[];
  status?: AlertStatus[];
  type?: AlertType[];
  dateFrom?: string;
  dateTo?: string;
  searchTerm?: string;
}

export interface UserFilters {
  role?: UserRole[];
  status?: UserStatus[];
  mfaEnabled?: boolean;
  searchTerm?: string;
}

// Form Types
export interface CreateUserForm {
  name: string;
  email: string;
  role: UserRole;
  sendInvite: boolean;
  requireMFA: boolean;
}

export interface UpdatePasswordForm {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface NotificationSettings {
  criticalAlerts: boolean;
  highPriorityAlerts: boolean;
  systemUpdates: boolean;
  weeklyReports: boolean;
  userActivity: boolean;
}
