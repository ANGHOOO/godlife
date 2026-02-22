import { SideNav } from "@/components/side-nav";
import type { ReactNode } from "react";
import { getCurrentSession } from "@/lib/server/auth";

export default async function DashboardLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  const session = await getCurrentSession();

  return (
    <div className="app-shell">
      {session ? <SideNav session={session} /> : null}
      <main className="main">{children}</main>
    </div>
  );
}
