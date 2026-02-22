export type ApiError = {
  code: string;
  message: string;
  retryable: boolean;
  status: number;
  requestId?: string;
};

export type HealthResponse = {
  status: string;
};

export type DashboardOverview = {
  checkedAt: string;
  backendHealthy: boolean;
  capabilities: {
    canGeneratePlan: boolean;
    canRetryNotification: boolean;
    hasReadApis: boolean;
  };
  notes: string[];
};

export type PlanGenerateInput = {
  userId: string;
  targetDate: string;
  source: "rule" | "llm";
};

export type PlanGenerateResult = {
  id: string;
  user_id: string;
  target_date: string;
  source: string;
  status: string;
};

export type NotificationRetryInput = {
  notificationId: string;
};

export type NotificationRetryResult = {
  id: string;
  state: string;
};
