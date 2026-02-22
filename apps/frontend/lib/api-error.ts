import { ApiError } from "@/lib/types";

type MaybeApiErrorPayload = {
  error_code?: string;
  message?: string;
  retryable?: boolean;
  request_id?: string;
  detail?: string;
};

export async function toApiError(response: Response): Promise<ApiError> {
  let payload: MaybeApiErrorPayload = {};

  try {
    payload = (await response.json()) as MaybeApiErrorPayload;
  } catch {
    payload = {};
  }

  return {
    code: payload.error_code ?? `http_${response.status}`,
    message:
      payload.message ??
      payload.detail ??
      "요청 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
    retryable: payload.retryable ?? response.status >= 500,
    requestId: payload.request_id,
    status: response.status
  };
}
