"use client";

import { useDashboardOverview } from "@/hooks/use-dashboard-overview";
import { DashboardOverview } from "@/lib/types";

import { StatusPill } from "./status-pill";

export function DashboardOverviewPanel({
  initialData
}: {
  initialData: DashboardOverview;
}) {
  const { data, isError, refetch, isFetching } = useDashboardOverview(initialData);
  const resolvedData = data ?? initialData;

  const tone = resolvedData.backendHealthy ? "ok" : "fail";

  return (
    <div className="grid">
      <section className="card fade-up">
        <h2>백엔드 상태</h2>
        <p className="inline" style={{ marginTop: "0.7rem" }}>
          <StatusPill
            tone={tone}
            label={resolvedData.backendHealthy ? "정상 연결" : "연결 불안정"}
          />
          <span className="muted">
            마지막 확인: {new Date(resolvedData.checkedAt).toLocaleString()}
          </span>
        </p>
        <p className="muted" style={{ marginTop: "0.8rem" }}>
          기본 폴링은 15초이며, 주요 액션 이후 즉시 동기화됩니다.
        </p>
      </section>

      <section className="card fade-up" style={{ animationDelay: "70ms" }}>
        <h2>현재 기능 범위</h2>
        <p className="inline" style={{ marginTop: "0.7rem" }}>
          <StatusPill tone="ok" label="플랜 생성" />
          <StatusPill tone="ok" label="알림 재시도" />
          <StatusPill
            tone={resolvedData.capabilities.hasReadApis ? "ok" : "pending"}
            label={
              resolvedData.capabilities.hasReadApis
                ? "조회 API 사용 가능"
                : "조회 API 준비 중"
            }
          />
        </p>
      </section>

      <section className="card fade-up" style={{ animationDelay: "140ms" }}>
        <h3>운영 메모</h3>
        <ul>
          {resolvedData.notes.map((note) => (
            <li key={note} className="muted" style={{ marginTop: "0.42rem" }}>
              {note}
            </li>
          ))}
        </ul>
      </section>

      <section className="card fade-up" style={{ animationDelay: "210ms" }}>
        <h3>예외 대응</h3>
        <p className="muted" style={{ marginTop: "0.7rem" }}>
          {isError
            ? "상태 조회에 실패했습니다. 수동 재시도를 진행해주세요."
            : "Webhook 지연/중복 응답은 중립 메시지로 안내합니다."}
        </p>
        <div className="inline" style={{ marginTop: "0.8rem" }}>
          <button className="secondary" type="button" onClick={() => void refetch()}>
            상태 다시 확인
          </button>
          {isFetching ? <StatusPill tone="pending" label="동기화 중" /> : null}
        </div>
      </section>
    </div>
  );
}
