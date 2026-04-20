import { getApiAuthToken, getApiV1BaseUrl } from "@/lib/env";

export function buildApiUrl(path: string) {
  const baseUrl = getApiV1BaseUrl();
  if (!baseUrl) {
    return "";
  }

  const normalizedPath = `/${path.replace(/^\/+/, "")}`;
  return `${baseUrl}${normalizedPath}`;
}

export async function fetchJsonOrUndefined<T>(path: string): Promise<T | undefined> {
  const endpoint = buildApiUrl(path);
  if (!endpoint) {
    return undefined;
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2500);

  const token = getApiAuthToken().trim();
  const headers = token ? { Authorization: `Bearer ${token}` } : undefined;

  try {
    const response = await fetch(endpoint, {
      cache: "no-store",
      signal: controller.signal,
      headers,
    });

    if (!response.ok) {
      return undefined;
    }

    return (await response.json()) as T;
  } catch {
    return undefined;
  } finally {
    clearTimeout(timeout);
  }
}

export async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const endpoint = buildApiUrl(path);
  if (!endpoint) {
    throw new Error("当前未配置 API 地址");
  }

  const token = getApiAuthToken().trim();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(endpoint, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `请求失败：${response.status}`);
  }

  return (await response.json()) as T;
}
