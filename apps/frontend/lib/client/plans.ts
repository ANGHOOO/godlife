import { fetchJson } from "@/lib/client/http";
import { PlanGenerateInput, PlanGenerateResult } from "@/lib/types";

export function generatePlan(input: PlanGenerateInput): Promise<PlanGenerateResult> {
  return fetchJson<PlanGenerateResult>("/api/plans/generate", {
    method: "POST",
    body: JSON.stringify({
      user_id: input.userId,
      target_date: input.targetDate,
      source: input.source
    })
  });
}
