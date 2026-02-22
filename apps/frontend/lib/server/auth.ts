import { cookies } from "next/headers";
import type { NextRequest, NextResponse } from "next/server";
import { redirect } from "next/navigation";

export type UserSession = {
  userId: string;
  kakaoUserId: string;
  name: string;
};

export const SESSION_COOKIE_NAME = "godlife_session";
export const AUTH_STATE_COOKIE_NAME = "godlife_auth_state";

export function buildCookieOptions() {
  return {
    path: "/",
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production"
  };
}

function isString(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}

export function encodeSession(session: UserSession): string {
  return encodeURIComponent(
    JSON.stringify({
      userId: session.userId,
      kakaoUserId: session.kakaoUserId,
      name: session.name
    })
  );
}

function parseSessionValue(raw: string | null): UserSession | null {
  if (!raw) {
    return null;
  }

  let payload: Record<string, unknown>;
  try {
    payload = JSON.parse(decodeURIComponent(raw)) as Record<string, unknown>;
  } catch {
    return null;
  }

  if (
    !isString(payload.userId) ||
    !isString(payload.kakaoUserId) ||
    typeof payload.name !== "string"
  ) {
    return null;
  }

  return {
    userId: payload.userId,
    kakaoUserId: payload.kakaoUserId,
    name: payload.name
  };
}

export async function getSessionFromRequest(
  request: NextRequest
): Promise<UserSession | null> {
  return parseSessionValue(request.cookies.get(SESSION_COOKIE_NAME)?.value ?? null);
}

export async function getCurrentSession(): Promise<UserSession | null> {
  const cookieStore = await cookies();
  return parseSessionValue(cookieStore.get(SESSION_COOKIE_NAME)?.value ?? null);
}

export async function requireCurrentSession(): Promise<UserSession> {
  const session = await getCurrentSession();
  if (session === null) {
    redirect("/");
  }

  return session;
}

export function setSessionCookie(
  response: NextResponse,
  session: UserSession
): void {
  response.cookies.set({
    name: SESSION_COOKIE_NAME,
    value: encodeSession(session),
    ...buildCookieOptions()
  });
}

export function clearSessionCookie(response: NextResponse): void {
  response.cookies.delete({
    name: SESSION_COOKIE_NAME,
    ...buildCookieOptions()
  });
}

export function setAuthStateCookie(
  response: NextResponse,
  state: string
): void {
  response.cookies.set({
    name: AUTH_STATE_COOKIE_NAME,
    value: state,
    ...buildCookieOptions(),
    maxAge: 300
  });
}

export function clearAuthStateCookie(response: NextResponse): void {
  response.cookies.delete({
    name: AUTH_STATE_COOKIE_NAME,
    ...buildCookieOptions()
  });
}

export function getAuthStateCookieValue(request: NextRequest): string | null {
  return request.cookies.get(AUTH_STATE_COOKIE_NAME)?.value ?? null;
}

function isLoopbackHostname(hostname: string): boolean {
  return (
    hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1"
  );
}

function safeParseUrl(value: string): URL | null {
  try {
    return new URL(value);
  } catch {
    return null;
  }
}

function logRedirectPolicyMismatch(message: string, details: Record<string, string>) {
  if (process.env.NODE_ENV === "production") {
    return;
  }
  console.debug(message, details);
}

export function getKakaoClientId(): string | null {
  return process.env.KAKAO_CLIENT_ID ?? null;
}

export function getKakaoClientSecret(): string | null {
  return process.env.KAKAO_CLIENT_SECRET ?? null;
}

export function getKakaoRedirectUri(request: NextRequest): string {
  const requestRedirectUri = `${request.nextUrl.origin}/api/auth/callback`;
  const configuredRedirectUri = process.env.KAKAO_REDIRECT_URI;
  const requestHost = request.nextUrl.hostname;

  if (!configuredRedirectUri) {
    return requestRedirectUri;
  }

  const configuredRedirect = safeParseUrl(configuredRedirectUri);
  if (configuredRedirect === null) {
    logRedirectPolicyMismatch("카카오 리다이렉트 URI 형식이 유효하지 않습니다.", {
      configuredRedirectUri,
      requestRedirectUri
    });
    return requestRedirectUri;
  }

  const configuredHost = configuredRedirect.hostname;

  if (
    isLoopbackHostname(configuredHost) &&
    isLoopbackHostname(requestHost)
  ) {
    if (configuredRedirectUri !== requestRedirectUri) {
      logRedirectPolicyMismatch(
        "루프백 호스트 간 mismatch를 감지하여 요청 기준 URI를 사용합니다.",
        {
          configuredRedirectUri,
          requestRedirectUri
        }
      );
    }
    return requestRedirectUri;
  }

  return configuredRedirect.toString();
}
