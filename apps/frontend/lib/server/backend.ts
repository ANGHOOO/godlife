import { getBackendBaseUrl } from "@/lib/server/config";

export async function requestBackend(
  path: string,
  init?: RequestInit
): Promise<Response> {
  const baseUrl = getBackendBaseUrl();

  return fetch(`${baseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
}

export async function requestBackendJson<T>(
  path: string,
  init?: RequestInit
): Promise<{ ok: boolean; status: number; data: T | null }> {
  const response = await requestBackend(path, init);

  let data: T | null = null;
  try {
    data = (await response.json()) as T;
  } catch {
    data = null;
  }

  return { ok: response.ok, status: response.status, data };
}
