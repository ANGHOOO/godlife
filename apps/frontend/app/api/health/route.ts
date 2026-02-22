import { NextResponse } from "next/server";

import { requestBackendJson } from "@/lib/server/backend";
import { HealthResponse } from "@/lib/types";

export async function GET() {
  const healthResult = await requestBackendJson<HealthResponse>("/healthz");

  if (!healthResult.ok || healthResult.data === null) {
    return NextResponse.json(
      {
        error_code: "dependency_unavailable",
        message: "백엔드 healthcheck 호출에 실패했습니다.",
        retryable: true
      },
      { status: 502 }
    );
  }

  return NextResponse.json(healthResult.data);
}
