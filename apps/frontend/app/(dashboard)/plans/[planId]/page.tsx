import Link from "next/link";

import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";

type PlanDetailPageProps = {
  params: Promise<{ planId: string }>;
};

export default async function PlanDetailPage({ params }: PlanDetailPageProps) {
  const { planId } = await params;

  return (
    <>
      <PageHeader
        title="운동 계획 상세"
        subtitle="현재 백엔드 조회 API 확장 전 단계이므로 생성 결과 기반 메타 정보만 노출합니다."
      />
      <section className="card fade-up">
        <h2>Plan ID</h2>
        <p style={{ marginTop: "0.55rem" }}>{planId}</p>
        <p className="inline" style={{ marginTop: "0.8rem" }}>
          <StatusPill tone="pending" label="세트 상세 API 준비 중" />
          <span className="muted">향후 `/plans/{'{plan_id}'}` 조회 API 연동 예정</span>
        </p>
        <div style={{ marginTop: "0.9rem" }}>
          <Link className="nav-link" href="/plans/new">
            새 계획 만들기
          </Link>
        </div>
      </section>
    </>
  );
}
