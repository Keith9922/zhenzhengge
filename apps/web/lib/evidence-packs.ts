import { fetchJsonOrUndefined } from "@/lib/api";
import { buildApiErrorNote, type DetailFetchResult, type ListFetchResult } from "@/lib/data-source";

export type EvidencePackListItem = {
  id: string;
  caseId: string;
  title: string;
  source: string;
  sourceUrl?: string;
  capturedAt: string;
  status: string;
  summary: string;
  artifactPaths: string[];
  snapshotPath?: string;
  htmlPath?: string;
  htmlSnippet?: string;
  screenshotUrl?: string;
  screenshotDownloadUrl?: string;
  htmlDownloadUrl?: string;
  screenshotAvailable?: boolean;
  htmlAvailable?: boolean;
};

type ApiEvidencePack = {
  evidence_pack_id?: string;
  case_id?: string;
  source_title?: string;
  source_url?: string;
  capture_channel?: string;
  created_at?: string;
  status?: string;
  snapshot_path?: string;
  html_path?: string;
  note?: string | null;
};

type ApiEvidencePreviewPayload = {
  item?: ApiEvidencePack;
  screenshot_available?: boolean;
  html_available?: boolean;
  screenshot_url?: string | null;
  screenshot_download_url?: string | null;
  html_download_url?: string | null;
  html_excerpt?: string;
};

const sourceLabelMap: Record<string, string> = {
  "browser-extension": "网页取证",
  "brand-site": "品牌官网",
  taobao: "淘宝",
  tmall: "天猫",
  pinduoduo: "拼多多",
  jd: "京东",
  email: "邮件",
  dingtalk: "钉钉",
  "public-web": "公开网页",
};

function toStringValue(value: unknown, fallback = "") {
  if (typeof value === "string" && value.trim()) {
    return value.trim();
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return String(value);
  }

  return fallback;
}

function toProxyAssetUrl(path: unknown) {
  const raw = toStringValue(path);
  if (!raw) {
    return "";
  }
  if (raw.startsWith("/api/v1/")) {
    return raw.replace("/api/v1/", "/api/proxy/");
  }
  return raw;
}

function toSourceLabel(value: unknown, fallback = "公开网页") {
  const normalized = toStringValue(value).toLowerCase();
  return sourceLabelMap[normalized] || toStringValue(value, fallback);
}

function normalizePack(record: ApiEvidencePack, index = 0): EvidencePackListItem {
  const title = toStringValue(record.source_title, `证据包 ${index + 1}`);
  const artifactPaths = [record.snapshot_path, record.html_path]
    .map((item) => toStringValue(item))
    .filter(Boolean);
  const sourceLabel = toSourceLabel(record.capture_channel, "公开网页");
  const snippetText = toStringValue(record.note, "页面抓取内容已归档。\n可在下方进行预览与下载。");
  const htmlSnippet = [
    `<article class="evidence-card" data-source="${sourceLabel}">`,
    "  <header>",
    `    <h1>${title}</h1>`,
    `    <p>来源：${sourceLabel}</p>`,
    `    <time>${toStringValue(record.created_at, "待补充")}</time>`,
    "  </header>",
    "  <section>",
    `    <p>${snippetText}</p>`,
    "  </section>",
    "</article>",
  ].join("\n");

  return {
    id: toStringValue(record.evidence_pack_id, `evidence-pack-${index + 1}`),
    caseId: toStringValue(record.case_id, "未关联案件"),
    title,
    source: sourceLabel,
    sourceUrl: toStringValue(record.source_url),
    capturedAt: toStringValue(record.created_at, "待补充"),
    status: toStringValue(record.status, "captured"),
    summary: toStringValue(record.note, "已生成基础证据包，可继续补充说明与处置材料。"),
    artifactPaths,
    snapshotPath: toStringValue(record.snapshot_path),
    htmlPath: toStringValue(record.html_path),
    htmlSnippet,
    screenshotAvailable: Boolean(toStringValue(record.snapshot_path)),
    htmlAvailable: Boolean(toStringValue(record.html_path)),
  };
}

export async function getEvidencePacks(): Promise<ListFetchResult<EvidencePackListItem>> {
  const payload = await fetchJsonOrUndefined<ApiEvidencePack[] | { items?: ApiEvidencePack[] }>("/evidence-packs");

  if (!payload) {
    return {
      items: [],
      source: "error",
      note: buildApiErrorNote("证据包列表"),
    };
  }

  const rawItems = Array.isArray(payload) ? payload : payload.items ?? [];

  return {
    items: rawItems.map((item, index) => normalizePack(item, index)),
    source: "api",
  };
}

export async function getEvidencePackById(packId: string): Promise<DetailFetchResult<EvidencePackListItem>> {
  const preview = await fetchJsonOrUndefined<ApiEvidencePreviewPayload>(`/evidence-packs/${encodeURIComponent(packId)}/preview`);

  if (preview?.item) {
    const item = normalizePack(preview.item);
    item.screenshotAvailable = Boolean(preview.screenshot_available);
    item.htmlAvailable = Boolean(preview.html_available);
    item.screenshotUrl = toProxyAssetUrl(preview.screenshot_url);
    item.screenshotDownloadUrl = toProxyAssetUrl(preview.screenshot_download_url);
    item.htmlDownloadUrl = toProxyAssetUrl(preview.html_download_url);
    item.htmlSnippet = toStringValue(preview.html_excerpt, item.htmlSnippet ?? "");
    return { item, source: "api" };
  }

  const payload = await fetchJsonOrUndefined<ApiEvidencePack>(`/evidence-packs/${encodeURIComponent(packId)}`);
  if (!payload) {
    return {
      source: "error",
      note: buildApiErrorNote("证据包详情"),
    };
  }

  return {
    item: normalizePack(payload),
    source: "api",
  };
}
