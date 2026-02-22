import { describe, expect, it } from "vitest";

import { toApiError } from "./api-error";

describe("toApiError", () => {
  it("payload의 message와 error_code를 매핑한다", async () => {
    const response = new Response(
      JSON.stringify({
        error_code: "conflict",
        message: "이미 존재합니다.",
        retryable: false,
        request_id: "req-1"
      }),
      { status: 409 }
    );

    const error = await toApiError(response);

    expect(error.code).toBe("conflict");
    expect(error.message).toBe("이미 존재합니다.");
    expect(error.retryable).toBe(false);
    expect(error.status).toBe(409);
    expect(error.requestId).toBe("req-1");
  });

  it("본문이 없을 때 기본 메시지를 사용한다", async () => {
    const response = new Response("", { status: 503 });

    const error = await toApiError(response);

    expect(error.code).toBe("http_503");
    expect(error.retryable).toBe(true);
    expect(error.message.length).toBeGreaterThan(0);
  });
});
