import { PageHeader } from "@/components/page-header";
import { getBackendBaseUrl } from "@/lib/server/config";
import { requireCurrentSession } from "@/lib/server/auth";

export default async function SettingsPage() {
  const session = await requireCurrentSession();
  const backendBaseUrl = getBackendBaseUrl();

  return (
    <>
      <PageHeader
        title="설정"
        subtitle="단일 사용자 MVP 운영을 위한 기본 환경값을 확인합니다."
      />
      <section className="card fade-up">
        <h2>환경값</h2>
        <p className="muted" style={{ marginTop: "0.6rem" }}>
          BACKEND_BASE_URL: {backendBaseUrl}
        </p>
        <div className="muted" style={{ marginTop: "0.4rem" }}>
          세션 사용자: {session ? session.userId : "-"}
        </div>
        <div className="muted" style={{ marginTop: "0.4rem" }}>
          카카오 사용자: {session ? session.kakaoUserId : "-"}
        </div>
        <div className="muted" style={{ marginTop: "0.4rem" }}>
          표시 이름: {session ? session.name : "-"}
        </div>
      </section>
    </>
  );
}
