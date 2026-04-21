import { getApiAuthToken, getApiV1BaseUrl } from "@/lib/env";
import { buildApiErrorNote, type DetailFetchResult, type ListFetchResult } from "@/lib/data-source";

export type CaseStatus = string;

export type CaseSummary = {
  id: string;
  title: string;
  status: CaseStatus;
  summary: string;
  source: string;
  updatedAt: string;
};

export type CaseDetail = CaseSummary & {
  target: string;
  riskScore: number;
  evidenceCount: number;
  evidencePacks: EvidencePackSummary[];
  notes: string[];
  evidenceItems: string[];
  nextActions: string[];
};

export type EvidencePackSummary = {
  id: string;
  title: string;
  source: string;
  capturedAt: string;
  artifactCount: number;
  summary: string;
  items: string[];
};

type ApiCaseRecord = {
  case_id?: string;
  caseId?: string;
  id?: string;
  brand_name?: string;
  brandName?: string;
  suspect_name?: string;
  suspectName?: string;
  platform?: string;
  monitoring_scope?: unknown;
  monitoringScope?: unknown;
  updated_at?: string;
  updatedAt?: string;
  status?: string;
  risk_level?: string | number;
  riskLevel?: string | number;
  risk_score?: string | number;
  riskScore?: string | number;
  title?: string;
  summary?: string;
  description?: string;
  target?: string;
  evidence_count?: string | number;
  evidenceCount?: string | number;
  notes?: string[];
  evidence_items?: string[];
  evidenceItems?: string[];
  next_actions?: string[];
  nextActions?: string[];
  evidence_packs?: unknown;
  evidencePacks?: unknown;
};

type ApiEvidencePackRecord = {
  evidence_pack_id?: string;
  evidencePackId?: string;
  id?: string;
  title?: string;
  name?: string;
  source_title?: string;
  sourceTitle?: string;
  source?: string;
  platform?: string;
  capture_channel?: string;
  captureChannel?: string;
  source_url?: string;
  sourceUrl?: string;
  created_at?: string;
  createdAt?: string;
  captured_at?: string;
  capturedAt?: string;
  updated_at?: string;
  updatedAt?: string;
  note?: string;
  hash_sha256?: string;
  snapshot_path?: string;
  html_path?: string;
  artifact_count?: string | number;
  artifactCount?: string | number;
  summary?: string;
  items?: unknown;
  evidence_items?: unknown;
  evidenceItems?: unknown;
};

type JsonFetchResult =
  | {
      ok: true;
      status: number;
      data: unknown;
    }
  | {
      ok: false;
      status?: number;
      detail: string;
    };

type CaseDetailFetchResult =
  | {
      kind: "ok";
      item: CaseDetail;
    }
  | {
      kind: "missing";
      detail: string;
    }
  | {
      kind: "error";
      detail: string;
    };

const statusLabelMap: Record<string, string> = {
  open: "待处理",
  monitoring: "监测中",
  triaged: "已研判",
  drafting: "材料整理中",
  review: "审核中",
  archived: "已归档",
};

const riskLabelMap: Record<string, string> = {
  high: "高风险",
  medium: "中风险",
  low: "低风险",
};

const platformLabelMap: Record<string, string> = {
  taobao: "淘宝",
  tmall: "天猫",
  pinduoduo: "拼多多",
  jd: "京东",
  "browser-extension": "网页取证",
  "brand-site": "品牌官网",
};

function toStringValue(value: unknown, fallback = "") {
  if (typeof value === "string") {
    return value.trim() || fallback;
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return String(value);
  }

  return fallback;
}

function toNumberValue(value: unknown, fallback = 0) {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string" && value.trim()) {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return fallback;
}

function toStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.map((entry) => toStringValue(entry)).filter(Boolean);
}

function toStatusLabel(value: unknown, fallback = "待处理") {
  const normalized = toStringValue(value).toLowerCase();
  return statusLabelMap[normalized] || toStringValue(value, fallback);
}

function toRiskLabel(value: unknown, fallback = "待评估") {
  const normalized = toStringValue(value).toLowerCase();
  return riskLabelMap[normalized] || toStringValue(value, fallback);
}

function toPlatformLabel(value: unknown, fallback = "公开网页") {
  const normalized = toStringValue(value).toLowerCase();
  return platformLabelMap[normalized] || toStringValue(value, fallback);
}

function buildEvidencePacksEndpoint(caseId: string, variant: "path" | "query" = "path") {
  if (variant === "path") {
    return buildCasesEndpoint(`cases/${encodeURIComponent(caseId)}/evidence-packs`);
  }

  return buildCasesEndpoint(`evidence-packs?case_id=${encodeURIComponent(caseId)}`);
}

function buildCasesEndpoint(path = "cases") {
  const baseUrl = getApiV1BaseUrl();
  if (!baseUrl) {
    return "";
  }

  const normalizedPath = `/${path.replace(/^\/+/, "")}`;
  return `${baseUrl}${normalizedPath}`;
}

function extractCaseList(payload: unknown): ApiCaseRecord[] {
  const candidates =
    Array.isArray(payload)
      ? payload
      : typeof payload === "object" && payload !== null
        ? [
            (payload as { items?: unknown }).items,
            (payload as { data?: unknown }).data,
            (payload as { cases?: unknown }).cases,
          ].find(Array.isArray)
        : undefined;

  return Array.isArray(candidates) ? (candidates as ApiCaseRecord[]) : [];
}

function extractEvidencePackList(payload: unknown): EvidencePackSummary[] {
  const candidates =
    Array.isArray(payload)
      ? payload
      : typeof payload === "object" && payload !== null
        ? [
            (payload as { items?: unknown }).items,
            (payload as { data?: unknown }).data,
            (payload as { evidence_packs?: unknown }).evidence_packs,
            (payload as { evidencePacks?: unknown }).evidencePacks,
          ].find(Array.isArray)
        : undefined;

  if (!Array.isArray(candidates)) {
    return [];
  }

  return candidates
    .map((item, index) => normalizeApiEvidencePack(item as ApiEvidencePackRecord, index))
    .filter(Boolean);
}

function extractCaseDetail(payload: unknown): CaseDetail | undefined {
  if (!payload || typeof payload !== "object") {
    return undefined;
  }

  const direct = payload as ApiCaseRecord & {
    item?: unknown;
    data?: unknown;
    case?: unknown;
  };
  const candidates = [direct, direct.item, direct.data, direct.case].filter(Boolean);

  for (const candidate of candidates) {
    const record = candidate as ApiCaseRecord;
    if (record && typeof record === "object") {
      const id = record.case_id || record.caseId || record.id;
      if (!id) {
        continue;
      }

      return normalizeApiCaseDetail(record, String(id));
    }
  }

  return undefined;
}

function normalizeApiEvidencePack(record: ApiEvidencePackRecord, index = 0): EvidencePackSummary {
  const source = toPlatformLabel(
    record.capture_channel || record.captureChannel || record.source || record.platform,
    "未知来源",
  );
  const items = toStringArray(record.items || record.evidence_items || record.evidenceItems);
  const title = toStringValue(record.title || record.name || record.source_title || record.sourceTitle, `${source}证据包`);
  const capturedAt = toStringValue(
    record.created_at ||
      record.createdAt ||
      record.captured_at ||
      record.capturedAt ||
      record.updated_at ||
      record.updatedAt,
    "待补充",
  );
  const summary = toStringValue(
    record.summary,
    `${source} · ${toNumberValue(record.artifact_count ?? record.artifactCount, items.length || index + 1) || items.length || index + 1} 个材料`,
  );
  const finalItems =
    items.length
      ? items
      : [
          toStringValue(record.source_title || record.sourceTitle, "页面标题"),
          source,
          "页面截图",
          "抓取时间",
        ];
  const artifactCount = toNumberValue(record.artifact_count ?? record.artifactCount, finalItems.length);

  return {
    id: toStringValue(record.evidence_pack_id || record.evidencePackId || record.id, `evidence-pack-${index + 1}`),
    title,
    source,
    capturedAt,
    artifactCount: artifactCount || finalItems.length || 0,
    summary,
    items: finalItems,
  };
}

function normalizeApiCaseSummary(record: ApiCaseRecord, fallbackId = ""): CaseSummary {
  const id = toStringValue(record.case_id || record.caseId || record.id, fallbackId);
  const platform = toPlatformLabel(record.platform, "公开网页");
  const updatedAt = toStringValue(record.updated_at || record.updatedAt, "待更新");
  const rawStatus = toStatusLabel(record.status, "待处理");
  const riskLevel = toRiskLabel(record.risk_level ?? record.riskLevel ?? record.risk_score ?? record.riskScore, "待评估");
  const title = toStringValue(record.title, record.brand_name || record.brandName || `${platform}案件`);
  const summary = toStringValue(
    record.description || record.summary,
    `来源：${platform} · 风险等级：${riskLevel} · 当前进展：${rawStatus}`,
  );

  return {
    id,
    title,
    status: rawStatus,
    summary,
    source: platform,
    updatedAt,
  };
}

function normalizeApiCaseDetail(record: ApiCaseRecord, fallbackId = ""): CaseDetail {
  const summary = normalizeApiCaseSummary(record, fallbackId);
  const riskLevel = toRiskLabel(record.risk_level ?? record.riskLevel ?? record.risk_score ?? record.riskScore, "待评估");
  const riskScore = toNumberValue(record.risk_score ?? record.riskScore ?? record.risk_level ?? record.riskLevel, 0);
  const notes =
    Array.isArray(record.notes) && record.notes.length
      ? record.notes
      : [
          `平台：${summary.source}`,
          `风险等级：${riskLevel}`,
          "建议结合现有证据和业务判断继续推进。",
        ];
  const evidenceItems =
    Array.isArray(record.evidence_items) && record.evidence_items.length
      ? record.evidence_items
      : Array.isArray(record.evidenceItems) && record.evidenceItems.length
        ? record.evidenceItems
        : ["URL", "页面标题", "截图", "文本", "抓取时间"];
  const nextActions =
    Array.isArray(record.next_actions) && record.next_actions.length
      ? record.next_actions
      : Array.isArray(record.nextActions) && record.nextActions.length
        ? record.nextActions
        : ["整理案件材料", "补充证据", "人工确认"];

  return {
    ...summary,
    target: toStringValue(
      record.suspect_name ||
        record.suspectName ||
        record.brand_name ||
        record.brandName ||
        record.target ||
        summary.source,
      summary.source,
    ),
    riskScore,
    evidenceCount: toNumberValue(record.evidence_count ?? record.evidenceCount, 0),
    evidencePacks: [],
    notes,
    evidenceItems,
    nextActions,
  };
}

function mergeCaseDetailWithEvidencePacks(
  detail: CaseDetail,
  evidencePacks: EvidencePackSummary[],
): CaseDetail {
  const mergedPacks = evidencePacks.length ? evidencePacks : detail.evidencePacks;
  const flattenedItems = mergedPacks.length
    ? mergedPacks.flatMap((pack) => pack.items).filter(Boolean)
    : detail.evidenceItems;
  const evidenceCount = mergedPacks.reduce((count, pack) => count + pack.artifactCount, 0) || detail.evidenceCount;

  return {
    ...detail,
    evidencePacks: mergedPacks,
    evidenceCount,
    evidenceItems: flattenedItems.length ? Array.from(new Set(flattenedItems)) : detail.evidenceItems,
  };
}

async function fetchJson(endpoint: string): Promise<JsonFetchResult> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 3000);
  const token = getApiAuthToken().trim();
  const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
  try {
    const response = await fetch(endpoint, {
      cache: "no-store",
      signal: controller.signal,
      headers,
    });

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        detail: `HTTP ${response.status}`,
      };
    }

    const data = (await response.json()) as unknown;
    return {
      ok: true,
      status: response.status,
      data,
    };
  } catch (error) {
    const detail = error instanceof Error ? error.message : "网络请求失败";
    return {
      ok: false,
      detail,
    };
  } finally {
    clearTimeout(timeout);
  }
}

async function fetchApiCaseDetail(caseId: string): Promise<CaseDetailFetchResult> {
  const detailEndpoint = buildCasesEndpoint(`cases/${encodeURIComponent(caseId)}`);
  if (!detailEndpoint) {
    return {
      kind: "error",
      detail: "未配置 API 地址",
    };
  }

  const detailResponse = await fetchJson(detailEndpoint);
  if (!detailResponse.ok) {
    return {
      kind: "error",
      detail: detailResponse.detail,
    };
  }

  const detail = extractCaseDetail(detailResponse.data);
  if (!detail) {
    return {
      kind: "missing",
      detail: "未找到对应案件",
    };
  }

  const evidencePackEndpoints = [
    buildEvidencePacksEndpoint(caseId, "path"),
    buildEvidencePacksEndpoint(caseId, "query"),
  ].filter(Boolean);

  let evidencePacks: EvidencePackSummary[] = [];
  for (const endpoint of evidencePackEndpoints) {
    const packResponse = await fetchJson(endpoint);
    if (!packResponse.ok) {
      continue;
    }

    evidencePacks = extractEvidencePackList(packResponse.data);
    if (evidencePacks.length) {
      break;
    }
  }

  const payloadRecord = detailResponse.data as ApiCaseRecord;
  const inlinePacks = extractEvidencePackList(
    (payloadRecord.evidence_packs as unknown) || (payloadRecord.evidencePacks as unknown),
  );

  return {
    kind: "ok",
    item: mergeCaseDetailWithEvidencePacks(detail, evidencePacks.length ? evidencePacks : inlinePacks),
  };
}

export async function getCases(): Promise<ListFetchResult<CaseSummary>> {
  const endpoint = buildCasesEndpoint();
  if (!endpoint) {
    return {
      items: [],
      source: "error",
      note: buildApiErrorNote("案件列表", "未配置 API 地址"),
    };
  }

  const result = await fetchJson(endpoint);
  if (!result.ok) {
    return {
      items: [],
      source: "error",
      note: buildApiErrorNote("案件列表", result.detail),
    };
  }

  const records = extractCaseList(result.data);
  if (!records.length) {
    return {
      items: [],
      source: "api",
    };
  }

  return {
    items: records.map((record, index) =>
      normalizeApiCaseSummary(record, record.case_id || record.caseId || record.id || `api-case-${index + 1}`),
    ),
    source: "api",
  };
}

export async function getCaseById(caseId: string): Promise<DetailFetchResult<CaseDetail>> {
  const detailResult = await fetchApiCaseDetail(caseId);
  if (detailResult.kind === "ok") {
    return {
      item: detailResult.item,
      source: "api",
    };
  }

  if (detailResult.kind === "missing") {
    return {
      source: "error",
      note: buildApiErrorNote("案件详情", detailResult.detail),
    };
  }

  return {
    source: "error",
    note: buildApiErrorNote("案件详情", detailResult.detail),
  };
}
