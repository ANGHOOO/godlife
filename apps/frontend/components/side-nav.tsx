import Link from "next/link";
import type { UserSession } from "@/lib/server/auth";

const links: Array<{ href: string; label: string }> = [
  { href: "/", label: "오늘 요약" },
  { href: "/plans/new", label: "운동 계획 생성" },
  { href: "/reading", label: "독서 현황" },
  { href: "/summary/daily", label: "일간 요약" },
  { href: "/summary/weekly", label: "주간 요약" },
  { href: "/ops/notifications", label: "알림 재시도" },
  { href: "/settings", label: "설정" }
];

interface SideNavProps {
  session?: UserSession | null;
}

export function SideNav({ session }: SideNavProps) {
  return (
    <aside className="side-nav">
      <h1 className="nav-title">GodLife<br />Control</h1>
      {session ? (
        <section className="account-card">
          <p className="account-label">로그인 계정</p>
          <p className="account-name">{session.name || "이름 미정"}</p>
          <p className="account-meta">카카오 UID: {session.kakaoUserId}</p>
          <div className="inline" style={{ marginTop: "0.7rem" }}>
            <Link className="nav-link" href="/api/auth/logout">
              로그아웃
            </Link>
          </div>
        </section>
      ) : null}
      <nav aria-label="주요 메뉴">
        {links.map((link) => (
          <Link key={link.href} className="nav-link" href={link.href}>
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
