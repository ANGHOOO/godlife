"use client";

import { FormEvent, useState } from "react";

import { useGeneratePlan } from "@/hooks/use-generate-plan";
import { ApiError } from "@/lib/types";

import { StatusPill } from "./status-pill";

type Source = "rule" | "llm";

export function PlanGenerateForm() {
  const today = new Date().toISOString().slice(0, 10);
  const [targetDate, setTargetDate] = useState(today);
  const [source, setSource] = useState<Source>("rule");
  const mutation = useGeneratePlan();

  const apiError = mutation.error as ApiError | null;

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await mutation.mutateAsync({
      targetDate,
      source
    });
  }

  return (
    <section className="card fade-up">
      <h2>운동 계획 생성</h2>
      <p className="muted" style={{ marginTop: "0.5rem" }}>
        현재 사용자 기준으로 target date 당 ACTIVE 플랜은 1개만 허용됩니다.
      </p>
      <form className="form" style={{ marginTop: "0.9rem" }} onSubmit={(event) => void onSubmit(event)}>
        <label>
          사용자
          <input value="로그인 사용자 기준" readOnly />
        </label>
        <label>
          목표 날짜
          <input
            required
            type="date"
            value={targetDate}
            onChange={(event) => setTargetDate(event.target.value)}
          />
        </label>
        <label>
          생성 소스
          <select
            value={source}
            onChange={(event) => setSource(event.target.value as Source)}
          >
            <option value="rule">rule</option>
            <option value="llm">llm</option>
          </select>
        </label>

        <button disabled={mutation.isPending} type="submit">
          {mutation.isPending ? "생성 중..." : "플랜 생성"}
        </button>
      </form>

      {apiError ? (
        <div className="banner" style={{ marginTop: "0.9rem" }}>
          <strong>요청 실패 ({apiError.status})</strong>
          <p style={{ marginTop: "0.45rem" }}>{apiError.message}</p>
          {apiError.status === 409 ? (
            <p style={{ marginTop: "0.45rem" }}>
              이미 ACTIVE 플랜이 존재합니다. 날짜를 변경하거나 기존 계획을 확인하세요.
            </p>
          ) : null}
        </div>
      ) : null}

      {mutation.data ? (
        <div className="result-block" style={{ marginTop: "0.9rem" }}>
          <div className="inline">
            <StatusPill tone="ok" label="생성 완료" />
            <span className="muted">plan_id: {mutation.data.id}</span>
          </div>
          <p className="muted" style={{ marginTop: "0.45rem" }}>
            source: {mutation.data.source} / status: {mutation.data.status}
          </p>
        </div>
      ) : null}
    </section>
  );
}
