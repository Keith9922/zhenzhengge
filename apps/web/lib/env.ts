export function getRepoUrl() {
  return process.env.NEXT_PUBLIC_REPO_URL || "https://github.com/your-org/zhenzhengge";
}

export function getApiBaseUrl() {
  return process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "";
}

export function getApiAuthToken() {
  return process.env.API_AUTH_TOKEN || process.env.NEXT_PUBLIC_API_AUTH_TOKEN || "";
}

export function getApiV1BaseUrl() {
  const baseUrl = getApiBaseUrl().trim().replace(/\/$/, "");

  if (!baseUrl) {
    return "";
  }

  if (baseUrl.endsWith("/api/v1")) {
    return baseUrl;
  }

  if (baseUrl.endsWith("/api")) {
    return `${baseUrl}/v1`;
  }

  return `${baseUrl}/api/v1`;
}
