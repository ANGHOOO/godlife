import { NextResponse } from "next/server";

import { getDashboardOverviewSnapshot } from "@/lib/server/dashboard";

export async function GET() {
  const overview = await getDashboardOverviewSnapshot();
  return NextResponse.json(overview);
}
