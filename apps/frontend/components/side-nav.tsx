import Link from "next/link";

const links: Array<{ href: string; label: string }> = [
  { href: "/", label: "오늘 요약" },
  { href: "/plans/new", label: "운동 계획 생성" },
  { href: "/reading", label: "독서 현황" },
  { href: "/summary/daily", label: "일간 요약" },
  { href: "/summary/weekly", label: "주간 요약" },
  { href: "/ops/notifications", label: "알림 재시도" },
  { href: "/settings", label: "설정" }
];

export function SideNav() {
  return (
    <aside className="side-nav">
      <h1 className="nav-title">GodLife<br />Control</h1>
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
