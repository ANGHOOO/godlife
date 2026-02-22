import { requestBackendJson } from "@/lib/server/backend";
import { DashboardOverview, HealthResponse } from "@/lib/types";

export async function getDashboardOverviewSnapshot(): Promise<DashboardOverview> {
  const healthPromise = requestBackendJson<HealthResponse>("/healthz");
  const notesPromise = Promise.resolve([
    "현재 백엔드 조회형 API(요약/독서/알림 목록)는 준비 중입니다.",
    "플랜 생성 및 알림 재시도는 현재 연동 가능합니다."
  ]);

  const [healthResult, notes] = await Promise.all([healthPromise, notesPromise]);

  return {
    checkedAt: new Date().toISOString(),
    backendHealthy: healthResult.ok && healthResult.data?.status === "ok",
    capabilities: {
      canGeneratePlan: true,
      canRetryNotification: true,
      hasReadApis: false
    },
    notes
  };
}
