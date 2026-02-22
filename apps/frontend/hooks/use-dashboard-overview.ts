"use client";

import { useQuery } from "@tanstack/react-query";

import { getDashboardOverview } from "@/lib/client/dashboard";
import { DEFAULT_POLLING_MS } from "@/lib/client/config";
import { DashboardOverview } from "@/lib/types";

export function useDashboardOverview(initialData?: DashboardOverview) {
  return useQuery({
    queryKey: ["dashboard-overview"],
    queryFn: getDashboardOverview,
    refetchInterval: DEFAULT_POLLING_MS,
    initialData
  });
}
