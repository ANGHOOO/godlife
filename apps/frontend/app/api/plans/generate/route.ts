import { NextResponse, type NextRequest } from "next/server";

import { requestBackend } from "@/lib/server/backend";
import { getSessionFromRequest } from "@/lib/server/auth";
import { toGeneratePlanBackendPayload } from "@/lib/server/bff-payloads";

type GeneratePlanBody = {
  target_date: string;
  source?: string;
  plan_source?: string;
};

function badRequest(message: string) {
  return NextResponse.json(
    {
      error_code: "validation_error",
      message,
      retryable: false
    },
    { status: 400 }
  );
}

export async function POST(request: NextRequest) {
  let payload: GeneratePlanBody;

  try {
    payload = (await request.json()) as GeneratePlanBody;
  } catch {
    return badRequest("JSON 본문을 확인해주세요.");
  }

  const session = await getSessionFromRequest(request);
  if (!session) {
    return NextResponse.json(
      {
        error_code: "permission_error",
        message: "로그인 상태가 필요합니다.",
        retryable: false
      },
      { status: 401 }
    );
  }

  if (!payload.target_date) {
    return badRequest("`target_date`는 필수입니다.");
  }

  // Start backend request as soon as payload is validated.
  const backendPayload = toGeneratePlanBackendPayload({
    target_date: payload.target_date,
    source: payload.source,
    plan_source: payload.plan_source,
    user_id: session.userId
  });
  const backendPromise = requestBackend("/plans/generate", {
    method: "POST",
    body: JSON.stringify(backendPayload)
  });

  const backendResponse = await backendPromise;

  if (!backendResponse.ok) {
    const detail = await backendResponse.text();

    return NextResponse.json(
      {
        error_code:
          backendResponse.status === 409 ? "conflict" : "dependency_unavailable",
        message: detail || "플랜 생성 요청이 실패했습니다.",
        retryable: backendResponse.status >= 500
      },
      { status: backendResponse.status }
    );
  }

  const responseBody = await backendResponse.json();
  return NextResponse.json(responseBody, { status: 201 });
}
