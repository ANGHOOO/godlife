import { PageHeader } from "@/components/page-header";
import { getBackendBaseUrl } from "@/lib/server/config";

export default function SettingsPage() {
  const backendBaseUrl = getBackendBaseUrl();
  const userId =
    process.env.NEXT_PUBLIC_DEFAULT_USER_ID ??
    "00000000-0000-0000-0000-000000000001";

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
        <p className="muted" style={{ marginTop: "0.4rem" }}>
          NEXT_PUBLIC_DEFAULT_USER_ID: {userId}
        </p>
      </section>
    </>
  );
}
