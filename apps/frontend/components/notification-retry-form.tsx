"use client";

import { FormEvent, useState } from "react";

import { useRetryNotification } from "@/hooks/use-retry-notification";
import { ApiError } from "@/lib/types";

import { StatusPill } from "./status-pill";

export function NotificationRetryForm() {
  const [notificationId, setNotificationId] = useState("");
  const mutation = useRetryNotification();

  const apiError = mutation.error as ApiError | null;

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await mutation.mutateAsync({ notificationId });
  }

  return (
    <section className="card fade-up">
      <h2>알림 재시도</h2>
      <p className="muted" style={{ marginTop: "0.5rem" }}>
        수동 보정 플로우 전 단계로 재시도 상태를 확인할 수 있습니다.
      </p>

      <form className="form" style={{ marginTop: "0.9rem" }} onSubmit={(event) => void onSubmit(event)}>
        <label>
          Notification ID
          <input
            required
            value={notificationId}
            onChange={(event) => setNotificationId(event.target.value)}
            placeholder="UUID"
          />
        </label>
        <button disabled={mutation.isPending || !notificationId} type="submit">
          {mutation.isPending ? "재시도 요청 중..." : "재시도 요청"}
        </button>
      </form>

      {apiError ? (
        <div className="banner" style={{ marginTop: "0.9rem" }}>
          <strong>요청 실패 ({apiError.status})</strong>
          <p style={{ marginTop: "0.45rem" }}>{apiError.message}</p>
          {apiError.status === 404 ? (
            <p style={{ marginTop: "0.45rem" }}>알림 ID를 다시 확인해주세요.</p>
          ) : null}
        </div>
      ) : null}

      {mutation.data ? (
        <div className="result-block" style={{ marginTop: "0.9rem" }}>
          <div className="inline">
            <StatusPill tone="ok" label="재시도 처리" />
            <span className="muted">notification_id: {mutation.data.id}</span>
          </div>
          <p className="muted" style={{ marginTop: "0.45rem" }}>
            현재 상태: {mutation.data.state}
          </p>
        </div>
      ) : null}
    </section>
  );
}
