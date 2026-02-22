import { fetchJson } from "@/lib/client/http";
import { DashboardOverview } from "@/lib/types";

export function getDashboardOverview(): Promise<DashboardOverview> {
  return fetchJson<DashboardOverview>("/api/dashboard/overview");
}
