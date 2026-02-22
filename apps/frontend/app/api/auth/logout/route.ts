import { type NextRequest, NextResponse } from "next/server";

import { clearAuthStateCookie, clearSessionCookie } from "@/lib/server/auth";

export async function GET(request: NextRequest) {
  const response = NextResponse.redirect(new URL("/", request.url));
  clearSessionCookie(response);
  clearAuthStateCookie(response);
  return response;
}
