import Link from "next/link";

import { DashboardOverviewPanel } from "@/components/dashboard-overview";
import { PageHeader } from "@/components/page-header";
import { getCurrentSession } from "@/lib/server/auth";
import { getDashboardOverviewSnapshot } from "@/lib/server/dashboard";

export default async function HomePage() {
  const session = await getCurrentSession();

  if (!session) {
    return (
      <section className="card fade-up">
        <h1 className="page-title">GodLife 시작하기</h1>
        <p className="muted" style={{ marginTop: "0.5rem" }}>
          홈 진입 시 카카오톡 로그인으로 사용자 계정을 먼저 연결해주세요.
        </p>
        <Link className="nav-link" href="/api/auth/login" style={{ marginTop: "0.8rem", display: "inline-block", width: "max-content" }}>
          카카오 로그인
        </Link>
        <p className="muted" style={{ marginTop: "0.8rem" }}>
          로그인 후 운동/독서 트래킹 화면으로 이동합니다.
        </p>
      </section>
    );
  }

  const overview = await getDashboardOverviewSnapshot();

  return (
    <>
      <PageHeader
        title="오늘의 운영 보드"
        subtitle="운동·독서 루틴의 현재 상태와 예외 흐름을 한 화면에서 확인합니다."
      />
      <section className="card fade-up" style={{ marginBottom: "0.9rem" }}>
        <p className="muted" style={{ margin: 0 }}>
          로그인 사용자: {session.name || "이름 미정"} ({session.kakaoUserId})
        </p>
        <p className="muted" style={{ margin: "0.42rem 0 0" }}>
          사용자 ID: {session.userId}
        </p>
        <div className="inline" style={{ marginTop: "0.8rem" }}>
          <Link className="nav-link" href="/api/auth/logout">
            로그아웃
          </Link>
        </div>
      </section>
      <DashboardOverviewPanel initialData={overview} />
    </>
  );
}
