export function getRepoUrl() {
  return process.env.NEXT_PUBLIC_REPO_URL || "https://github.com/your-org/zhenzhengge";
}

export function getApiBaseUrl() {
  return process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "";
}
