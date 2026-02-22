import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { requireCurrentSession } from "@/lib/server/auth";

export default async function ReadingPage() {
  await requireCurrentSession();

  return (
    <>
      <PageHeader
        title="독서 현황"
        subtitle="기록/보완 알림 조회 API 연동 전, 화면 구조와 상태 가이드를 먼저 제공합니다."
      />
      <section className="card fade-up">
        <h2>독서 데이터</h2>
        <p className="inline" style={{ marginTop: "0.7rem" }}>
          <StatusPill tone="pending" label="API 준비 중" />
          <span className="muted">`GET /reading/logs` 및 `GET /reading/plans/{'{plan_id}'}` 대기</span>
        </p>
        <p className="muted" style={{ marginTop: "0.8rem" }}>
          빈 상태에서는 &quot;바로 기록 시작&quot; 버튼을 제공하도록 정책을 유지합니다.
        </p>
      </section>
    </>
  );
}
