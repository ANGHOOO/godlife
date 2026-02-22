import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { requireCurrentSession } from "@/lib/server/auth";

export default async function WeeklySummaryPage() {
  await requireCurrentSession();

  return (
    <>
      <PageHeader
        title="주간 요약"
        subtitle="일자별 완료율과 주간 추세 표현을 위한 레이아웃을 제공합니다."
      />
      <section className="card fade-up">
        <h2>Weekly Trend</h2>
        <p className="inline" style={{ marginTop: "0.7rem" }}>
          <StatusPill tone="pending" label="요약 API 준비 중" />
          <span className="muted">`GET /summary/weekly` 연동 예정</span>
        </p>
      </section>
    </>
  );
}
