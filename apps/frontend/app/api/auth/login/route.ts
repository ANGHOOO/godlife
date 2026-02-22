import { type NextRequest, NextResponse } from "next/server";

import {
  clearAuthStateCookie,
  getKakaoClientId,
  getKakaoRedirectUri,
  setAuthStateCookie
} from "@/lib/server/auth";
import { randomUUID } from "node:crypto";

const KAKAO_AUTH_ENDPOINT = "https://kauth.kakao.com/oauth/authorize";

function badConfigResponse(message: string) {
  return NextResponse.json({ error: message }, { status: 500 });
}

export async function GET(request: NextRequest) {
  const clientId = getKakaoClientId();
  if (clientId === null) {
    return badConfigResponse("KAKAO_CLIENT_ID 환경변수가 설정되지 않았습니다.");
  }

  const state = randomUUID();
  const kakaoRedirectUrl = getKakaoRedirectUri(request);
  const authorizeUrl = new URL(KAKAO_AUTH_ENDPOINT);
  authorizeUrl.searchParams.set("response_type", "code");
  authorizeUrl.searchParams.set("client_id", clientId);
  authorizeUrl.searchParams.set("redirect_uri", kakaoRedirectUrl);
  authorizeUrl.searchParams.set("state", state);

  const response = NextResponse.redirect(authorizeUrl);
  clearAuthStateCookie(response);
  setAuthStateCookie(response, state);

  return response;
}
