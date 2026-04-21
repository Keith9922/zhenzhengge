import { fetchJsonOrUndefined, buildApiUrl } from "@/lib/api";
import { getApiAuthToken } from "@/lib/env";
import { buildApiErrorNote, type ListFetchResult } from "@/lib/data-source";

export type BrandProfile = {
  profile_id: string;
  organization_id: string;
  brand_name: string;
  trademark_classes: string[];
  trademark_numbers: string[];
  confusable_terms: string[];
  protection_keywords: string[];
  created_at: string;
  updated_at: string;
};

export type BrandProfileCreatePayload = {
  brand_name: string;
  trademark_classes: string[];
  trademark_numbers: string[];
  confusable_terms: string[];
  protection_keywords: string[];
};

type ApiBrandProfileList = {
  total?: number;
  items?: BrandProfile[];
};

export async function fetchBrandProfiles(): Promise<ListFetchResult<BrandProfile>> {
  const data = await fetchJsonOrUndefined<ApiBrandProfileList>("brand-profiles");
  if (!data) {
    return { items: [], source: "error", note: buildApiErrorNote("brand-profiles") };
  }
  return { items: data.items ?? [], source: "api", total: data.total };
}

async function mutateProxyJson(path: string, method: string, body?: unknown): Promise<Response> {
  const url = buildApiUrl(path);
  const token = getApiAuthToken().trim();
  return fetch(url, {
    method,
    headers: {
      "content-type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

export async function createBrandProfile(payload: BrandProfileCreatePayload): Promise<BrandProfile | null> {
  const res = await mutateProxyJson("brand-profiles", "POST", payload);
  if (!res.ok) return null;
  return res.json();
}

export async function updateBrandProfile(
  profileId: string,
  payload: Partial<BrandProfileCreatePayload>
): Promise<BrandProfile | null> {
  const res = await mutateProxyJson(`brand-profiles/${profileId}`, "PUT", payload);
  if (!res.ok) return null;
  return res.json();
}

export async function deleteBrandProfile(profileId: string): Promise<boolean> {
  const res = await mutateProxyJson(`brand-profiles/${profileId}`, "DELETE");
  return res.ok;
}

export async function suggestConfusable(profileId: string): Promise<string[]> {
  const res = await mutateProxyJson(`brand-profiles/${profileId}/suggest-confusable`, "POST");
  if (!res.ok) return [];
  const data = await res.json();
  return data.suggestions ?? [];
}
