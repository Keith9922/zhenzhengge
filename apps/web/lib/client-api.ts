export function buildWorkspaceProxyUrl(path = "") {
  return `/api/proxy/${path.replace(/^\/+/, "")}`;
}

export async function postProxyJson(path: string, body?: unknown) {
  const response = await fetch(buildWorkspaceProxyUrl(path), {
    method: "POST",
    headers: body === undefined ? undefined : { "content-type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  return response;
}
