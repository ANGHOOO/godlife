import { describe, expect, it } from "vitest";

import {
  toGeneratePlanBackendPayload,
  toWebhookBackendPayload
} from "./bff-payloads";

describe("toGeneratePlanBackendPayload", () => {
  it("plan_source와 source를 모두 전달하면 둘 다 유지한다", () => {
    const payload = toGeneratePlanBackendPayload({
      user_id: "user-1",
      target_date: "2026-02-22",
      plan_source: "llm",
      source: "rule"
    });

    expect(payload.plan_source).toBe("llm");
    expect(payload.source).toBe("rule");
  });

  it("source 계열 입력이 없으면 rule 기본값을 설정한다", () => {
    const payload = toGeneratePlanBackendPayload({
      user_id: "user-1",
      target_date: "2026-02-22"
    });

    expect(payload.source).toBe("rule");
  });
});

describe("toWebhookBackendPayload", () => {
  it("객체 payload에 provider를 주입한다", () => {
    const payload = toWebhookBackendPayload("kakao", {
      event_type: "message",
      user_id: "u-1"
    });

    expect(payload.provider).toBe("kakao");
    expect(payload.event_type).toBe("message");
  });

  it("기존 provider 값이 있더라도 경로 provider로 덮어쓴다", () => {
    const payload = toWebhookBackendPayload("kakao", {
      provider: "other",
      event_type: "message"
    });

    expect(payload.provider).toBe("kakao");
  });

  it("객체가 아닌 payload는 raw_payload로 감싼다", () => {
    const payload = toWebhookBackendPayload("kakao", "raw");

    expect(payload.provider).toBe("kakao");
    expect(payload.raw_payload).toBe("raw");
  });
});
