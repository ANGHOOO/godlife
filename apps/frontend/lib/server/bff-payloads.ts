type GeneratePlanBody = {
  target_date: string;
  source?: string;
  plan_source?: string;
  user_id: string;
};

type WebhookBody = Record<string, unknown>;

function isPlainObject(value: unknown): value is WebhookBody {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function toGeneratePlanBackendPayload(payload: GeneratePlanBody): GeneratePlanBody {
  const backendPayload: GeneratePlanBody = {
    user_id: payload.user_id,
    target_date: payload.target_date
  };

  if (payload.plan_source !== undefined) {
    backendPayload.plan_source = payload.plan_source;
  }
  if (payload.source !== undefined) {
    backendPayload.source = payload.source;
  }
  if (backendPayload.plan_source === undefined && backendPayload.source === undefined) {
    backendPayload.source = "rule";
  }

  return backendPayload;
}

export function toWebhookBackendPayload(
  provider: string,
  payload: unknown
): Record<string, unknown> {
  if (isPlainObject(payload)) {
    const rawPayload = isPlainObject(payload.raw_payload)
      ? payload.raw_payload
      : payload;

    return {
      ...payload,
      provider,
      raw_payload: rawPayload
    };
  }

  return {
    provider,
    raw_payload: {
      value: payload ?? null
    }
  };
}
