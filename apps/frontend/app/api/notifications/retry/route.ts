import { NextResponse } from "next/server";

import { requestBackend } from "@/lib/server/backend";

type RetryNotificationBody = {
  notification_id: string;
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
  let payload: RetryNotificationBody;

  try {
    payload = (await request.json()) as RetryNotificationBody;
  } catch {
    return badRequest("JSON 본문을 확인해주세요.");
  }

  if (!payload.notification_id) {
    return badRequest("`notification_id`는 필수입니다.");
  }

  const backendResponse = await requestBackend("/notifications/retry", {
    method: "POST",
    body: JSON.stringify({ notification_id: payload.notification_id })
  });

  if (!backendResponse.ok) {
    const detail = await backendResponse.text();

    return NextResponse.json(
      {
        error_code:
          backendResponse.status === 404 ? "not_found" : "dependency_unavailable",
        message: detail || "알림 재시도 요청이 실패했습니다.",
        retryable: backendResponse.status >= 500
      },
      { status: backendResponse.status }
    );
  }

  const responseBody = await backendResponse.json();
  return NextResponse.json(responseBody);
}
