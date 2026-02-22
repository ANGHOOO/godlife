"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { generatePlan } from "@/lib/client/plans";
import { PlanGenerateInput } from "@/lib/types";

export function useGeneratePlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: PlanGenerateInput) => generatePlan(input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["dashboard-overview"] });
    }
  });
}
