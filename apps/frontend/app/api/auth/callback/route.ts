import { type NextRequest, NextResponse } from "next/server";

import { requestBackend } from "@/lib/server/backend";
import {
  clearAuthStateCookie,
  getKakaoRedirectUri,
  getKakaoClientId,
  getKakaoClientSecret,
  getAuthStateCookieValue,
  setSessionCookie
} from "@/lib/server/auth";

const KAKAO_TOKEN_ENDPOINT = "https://kauth.kakao.com/oauth/token";
const KAKAO_ME_ENDPOINT = "https://kapi.kakao.com/v2/user/me";

type KakaoTokenPayload = {
  access_token?: string;
  error?: string;
  error_description?: string;
};

type KakaoUserPayload = {
  id?: number | string | null;
  properties?: {
    nickname?: string;
  };
  kakao_account?: {
    profile?: {
      nickname?: string;
    };
  };
};

type ResolveUserResponse = {
  user_id: string;
  kakao_user_id: string;
  name: string;
};

function oauthBadRequest(message: string, status = 400) {
  return NextResponse.json({ error: message }, { status });
}

async function requestKakaoToken(
  request: NextRequest
): Promise<KakaoTokenPayload> {
  const clientId = getKakaoClientId();
  const redirectUri = getKakaoRedirectUri(request);

  const code = request.nextUrl.searchParams.get("code");
  if (!code) {
    throw new Error("인증 코드가 없습니다.");
  }

  if (!clientId) {
    throw new Error("KAKAO_CLIENT_ID가 설정되어 있지 않습니다.");
  }

  const tokenPayload = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: clientId,
    redirect_uri: redirectUri,
    code
  });

  const clientSecret = getKakaoClientSecret();
  if (clientSecret) {
    tokenPayload.set("client_secret", clientSecret);
  }

  const tokenResponse = await fetch(KAKAO_TOKEN_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    },
    body: tokenPayload.toString()
  });

  const tokenPayloadResult = (await tokenResponse.json()) as KakaoTokenPayload;

  if (!tokenResponse.ok || !tokenPayloadResult.access_token) {
    throw new Error(
      tokenPayloadResult.error_description ||
        tokenPayloadResult.error ||
        `카카오 토큰 교환 실패 (${tokenResponse.status})`
    );
  }

  return tokenPayloadResult;
}

async function requestKakaoUser(accessToken: string): Promise<KakaoUserPayload> {
  const userResponse = await fetch(KAKAO_ME_ENDPOINT, {
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });

  if (!userResponse.ok) {
    throw new Error(`카카오 사용자 조회 실패 (${userResponse.status})`);
  }

  const userPayload = (await userResponse.json()) as KakaoUserPayload;
  return userPayload;
}

function resolveKakaoName(payload: KakaoUserPayload): string | null {
  if (payload.properties?.nickname) {
    return payload.properties.nickname;
  }

  if (payload.kakao_account?.profile?.nickname) {
    return payload.kakao_account.profile.nickname;
  }

  return null;
}

function logStateValidationFailure(
  request: NextRequest,
  state: string | null,
  savedState: string | null
) {
  if (process.env.NODE_ENV === "production") {
    return;
  }

  console.warn("카카오 state 검증 실패", {
    requestHost: request.nextUrl.hostname,
    requestHostWithPort: request.nextUrl.host,
    receivedState: state,
    savedState,
    redirectUri: getKakaoRedirectUri(request)
  });
}

export async function GET(request: NextRequest) {
  if (request.nextUrl.searchParams.get("error")) {
    const error = request.nextUrl.searchParams.get("error") ?? "oauth_error";
    const detail = request.nextUrl.searchParams.get("error_description");
    return oauthBadRequest(`${error}: ${detail ?? "인증이 중단되었습니다."}`);
  }

  const state = request.nextUrl.searchParams.get("state");
  const savedState = getAuthStateCookieValue(request);

  if (!state || !savedState || state !== savedState) {
    logStateValidationFailure(request, state, savedState);
    return oauthBadRequest("state 검증에 실패했습니다.", 400);
  }

  let token: KakaoTokenPayload;
  try {
    token = await requestKakaoToken(request);
  } catch (error) {
    return oauthBadRequest(
      error instanceof Error ? error.message : "토큰 교환에 실패했습니다."
    );
  }

  if (!token.access_token) {
    return oauthBadRequest("액세스 토큰을 발급받지 못했습니다.");
  }

  let kakaoProfile: KakaoUserPayload;
  try {
    kakaoProfile = await requestKakaoUser(token.access_token);
  } catch (error) {
    return oauthBadRequest(
      error instanceof Error ? error.message : "카카오 사용자 조회에 실패했습니다."
    );
  }
  const kakaoUserId = kakaoProfile.id
    ? String(kakaoProfile.id)
    : "";

  if (!kakaoUserId) {
    return oauthBadRequest("카카오 사용자 정보를 파싱하지 못했습니다.");
  }

  const resolved = await requestBackend("/auth/resolve", {
    method: "POST",
    body: JSON.stringify({
      kakao_user_id: kakaoUserId,
      name: resolveKakaoName(kakaoProfile)
    })
  });

  if (!resolved.ok) {
    const text = await resolved.text();
    return oauthBadRequest(
      text || "사용자 식별자 매핑에 실패했습니다.",
      resolved.status
    );
  }

  const resolvedBody = (await resolved.json()) as ResolveUserResponse;

  const response = NextResponse.redirect(new URL("/", request.url));
  clearAuthStateCookie(response);
  setSessionCookie(response, {
    userId: resolvedBody.user_id,
    kakaoUserId: resolvedBody.kakao_user_id,
    name: resolvedBody.name
  });

  return response;
}
