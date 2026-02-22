import { NextResponse } from "next/server";

import { requestBackend } from "@/lib/server/backend";
import { toWebhookBackendPayload } from "@/lib/server/bff-payloads";

type WebhookRouteProps = {
  params: Promise<{ provider: string }>;
};

export async function POST(request: Request, { params }: WebhookRouteProps) {
  const { provider } = await params;

  let body: unknown = {};
  try {
    body = await request.json();
  } catch {
    body = {};
  }

  const forwardedPayload = toWebhookBackendPayload(provider, body);
  const backendResponse = await requestBackend(`/webhooks/${provider}`, {
    method: "POST",
    body: JSON.stringify(forwardedPayload)
  });

  let payload: unknown = { result: "accepted" };
  try {
    payload = await backendResponse.json();
  } catch {
    payload = { result: backendResponse.ok ? "accepted" : "failed" };
  }

  return NextResponse.json(payload, { status: backendResponse.status });
}
