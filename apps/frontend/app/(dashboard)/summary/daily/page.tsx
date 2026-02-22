import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";

export default function DailySummaryPage() {
  return (
    <>
      <PageHeader
        title="일간 요약"
        subtitle="완료율, streak, 추세 카드를 위한 구조를 준비하고 API 연동을 대기합니다."
      />
      <section className="card fade-up">
        <h2>Daily KPI</h2>
        <p className="inline" style={{ marginTop: "0.7rem" }}>
          <StatusPill tone="pending" label="요약 API 준비 중" />
          <span className="muted">`GET /summary/daily` 연동 예정</span>
        </p>
      </section>
    </>
  );
}
