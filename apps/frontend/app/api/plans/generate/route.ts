import { NextResponse } from "next/server";

import { requestBackend } from "@/lib/server/backend";
import { toGeneratePlanBackendPayload } from "@/lib/server/bff-payloads";

type GeneratePlanBody = {
  user_id: string;
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

export async function POST(request: Request) {
  let payload: GeneratePlanBody;

  try {
    payload = (await request.json()) as GeneratePlanBody;
  } catch {
    return badRequest("JSON 본문을 확인해주세요.");
  }

  if (!payload.user_id || !payload.target_date) {
    return badRequest("`user_id`와 `target_date`는 필수입니다.");
  }

  // Start backend request as soon as payload is validated.
  const backendPayload = toGeneratePlanBackendPayload(payload);
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
