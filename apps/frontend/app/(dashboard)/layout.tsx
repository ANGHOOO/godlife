import { SideNav } from "@/components/side-nav";
import type { ReactNode } from "react";

export default function DashboardLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <div className="app-shell">
      <SideNav />
      <main className="main">{children}</main>
    </div>
  );
}
