import { NextResponse, type NextRequest } from "next/server";
import { getApiAuthToken, getApiBaseUrl } from "@/lib/env";

function buildUpstreamUrl(pathSegments: string[], search: string) {
  const baseUrl = getApiBaseUrl().trim().replace(/\/$/, "");
  if (!baseUrl) {
    return "";
  }

  const upstreamPath = `/${pathSegments.map((segment) => segment.replace(/^\/+|\/+$/g, "")).filter(Boolean).join("/")}`;
  const normalizedBase = baseUrl.endsWith("/api/v1")
    ? baseUrl
    : baseUrl.endsWith("/api")
      ? `${baseUrl}/v1`
      : `${baseUrl}/api/v1`;

  return `${normalizedBase}${upstreamPath}${search}`;
}

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const upstreamUrl = buildUpstreamUrl(path, request.nextUrl.search);

  if (!upstreamUrl) {
    return NextResponse.json({ detail: "上游服务未配置" }, { status: 503 });
  }

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("content-length");
  const token = getApiAuthToken().trim();
  if (token && !headers.get("authorization")) {
    headers.set("authorization", `Bearer ${token}`);
  }

  const hasBody = !["GET", "HEAD"].includes(request.method);
  const body = hasBody ? await request.arrayBuffer() : undefined;

  const response = await fetch(upstreamUrl, {
    method: request.method,
    headers,
    body,
    redirect: "manual",
  });

  const responseHeaders = new Headers(response.headers);
  responseHeaders.delete("content-encoding");
  responseHeaders.delete("transfer-encoding");

  return new NextResponse(response.body, {
    status: response.status,
    headers: responseHeaders,
  });
}

export async function GET(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return proxy(request, context);
}

export async function POST(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return proxy(request, context);
}

export async function PATCH(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return proxy(request, context);
}
