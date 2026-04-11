import { getApiV1BaseUrl } from "@/lib/env";

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

const mockCases: CaseDetail[] = [
  {
    id: "case-adidas-aaodasis",
    title: "阿波达斯商品页",
    status: "高风险",
    summary: "近似命名、品牌视觉混淆，已完成基础取证。",
    source: "淘宝商品页",
    updatedAt: "2026-04-11 10:18",
    target: "阿迪达斯",
    riskScore: 92,
    evidenceCount: 8,
    evidencePacks: [
      {
        id: "pack-adidas-001",
        title: "商品页抓取包",
        source: "淘宝商品页",
        capturedAt: "2026-04-11 10:12",
        artifactCount: 4,
        summary: "保存了页面截图、标题、URL 和抓取日志。",
        items: ["URL", "页面标题", "全页截图", "抓取时间"],
      },
      {
        id: "pack-adidas-002",
        title: "图片比对包",
        source: "图片资源",
        capturedAt: "2026-04-11 10:18",
        artifactCount: 4,
        summary: "保存了图片哈希、对比结果和固证日志。",
        items: ["图片哈希", "对比结果", "HTML", "操作日志"],
      },
    ],
    notes: [
      "商品标题与目标品牌高度近似。",
      "页面视觉元素存在品牌混淆风险。",
      "已生成证据包，等待法务复核。",
    ],
    evidenceItems: ["URL", "页面标题", "全页截图", "HTML", "抓取时间", "哈希值", "图片链接", "操作日志"],
    nextActions: ["生成律师函初稿", "整理案件说明", "导出证据目录"],
  },
  {
    id: "case-brand-homepage-copy",
    title: "品牌官网疑似仿冒页",
    status: "待复核",
    summary: "页面出现新内容，等待进一步固证与人工审核。",
    source: "品牌官网",
    updatedAt: "2026-04-11 09:42",
    target: "官方品牌站",
    riskScore: 78,
    evidenceCount: 5,
    evidencePacks: [
      {
        id: "pack-homepage-001",
        title: "首页巡检包",
        source: "品牌官网",
        capturedAt: "2026-04-11 09:42",
        artifactCount: 3,
        summary: "保留了页面快照、DOM 变化和时间戳。",
        items: ["URL", "页面截图", "抓取时间"],
      },
    ],
    notes: ["页面近期更新过内容。", "需要补充更多历史快照。", "建议先完成人工复核。"],
    evidenceItems: ["URL", "页面标题", "全页截图", "页面文本", "抓取时间"],
    nextActions: ["继续巡检", "补抓历史页面", "发起复核"],
  },
  {
    id: "case-jd-mixed-content",
    title: "京东店铺图文混用页",
    status: "处理中",
    summary: "已生成证据包，待推送给负责人。",
    source: "京东店铺",
    updatedAt: "2026-04-10 20:05",
    target: "品牌授权页面",
    riskScore: 67,
    evidenceCount: 6,
    evidencePacks: [
      {
        id: "pack-jd-001",
        title: "图文混用抓取包",
        source: "京东店铺",
        capturedAt: "2026-04-10 20:05",
        artifactCount: 3,
        summary: "包含页面截图、文本提取和图片哈希。",
        items: ["截图", "文本", "图片哈希"],
      },
      {
        id: "pack-jd-002",
        title: "进展整理包",
        source: "案件记录",
        capturedAt: "2026-04-10 20:12",
        artifactCount: 3,
        summary: "包含当前处理状态、补充说明和后续动作。",
        items: ["处理状态", "补充说明", "后续动作"],
      },
    ],
    notes: ["图文混用，需拆分识别文字与图片。", "风险中等偏高。", "后续可进入投诉材料准备阶段。"],
    evidenceItems: ["URL", "页面标题", "截图", "文本", "图片哈希", "抓取时间"],
    nextActions: ["整理案件说明", "生成平台投诉函", "等待审核确认"],
  },
];

function normalize(value: string) {
  return value.trim().toLowerCase();
}

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

function extractCaseList(payload: unknown): CaseSummary[] {
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

  return Array.isArray(candidates) ? (candidates as CaseSummary[]) : [];
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
          `建议结合现有证据和业务判断继续推进。`,
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

export async function getCases() {
  const endpoint = buildCasesEndpoint();
  if (!endpoint) {
    return { items: mockCases, source: "mock" as const };
  }

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2500);
    const response = await fetch(endpoint, {
      cache: "no-store",
      signal: controller.signal,
    }).finally(() => clearTimeout(timeout));

    if (!response.ok) {
      return { items: mockCases, source: "mock" as const };
    }

    const payload: unknown = await response.json();
    const items = extractCaseList(payload).map((item, index) => {
      const record = item as ApiCaseRecord;
      return normalizeApiCaseSummary(record, record.case_id || record.caseId || record.id || `api-case-${index + 1}`);
    });

    if (!items.length) {
      return { items: mockCases, source: "mock" as const };
    }

    return { items, source: "api" as const };
  } catch {
    return { items: mockCases, source: "mock" as const };
  }
}

async function fetchJson(endpoint: string) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2500);
  try {
    const response = await fetch(endpoint, {
      cache: "no-store",
      signal: controller.signal,
    });

    if (!response.ok) {
      return undefined;
    }

    return await response.json();
  } catch {
    return undefined;
  } finally {
    clearTimeout(timeout);
  }
}

async function fetchApiCaseDetail(caseId: string) {
  const detailEndpoint = buildCasesEndpoint(`cases/${encodeURIComponent(caseId)}`);
  if (!detailEndpoint) {
    return undefined;
  }

  const payload = await fetchJson(detailEndpoint);
  const detail = extractCaseDetail(payload);
  if (!detail) {
    return undefined;
  }

  const evidencePackEndpoints = [
    buildEvidencePacksEndpoint(caseId, "path"),
    buildEvidencePacksEndpoint(caseId, "query"),
  ].filter(Boolean);

  let evidencePacks: EvidencePackSummary[] = [];
  for (const endpoint of evidencePackEndpoints) {
    const packPayload = await fetchJson(endpoint);
    evidencePacks = extractEvidencePackList(packPayload);
    if (evidencePacks.length) {
      break;
    }
  }

  const payloadRecord = payload as ApiCaseRecord;
  const inlinePacks = extractEvidencePackList(
    (payloadRecord.evidence_packs as unknown) || (payloadRecord.evidencePacks as unknown),
  );

  return mergeCaseDetailWithEvidencePacks(detail, evidencePacks.length ? evidencePacks : inlinePacks);
}

export async function getCaseById(caseId: string) {
  const apiDetail = await fetchApiCaseDetail(caseId);
  if (apiDetail) {
    return apiDetail;
  }

  const endpoint = buildCasesEndpoint(`cases/${encodeURIComponent(caseId)}`);
  if (endpoint) {
    try {
      const payload = await fetchJson(endpoint);
      const item = extractCaseDetail(payload);
      if (item) {
        return item;
      }
    } catch {
      // fall back to mock
    }
  }

  return mockCases.find((item) => normalize(item.id) === normalize(caseId) || normalize(item.title) === normalize(caseId));
}

export const mockCaseSummaries: CaseSummary[] = mockCases.map((item) => ({
  id: item.id,
  title: item.title,
  status: item.status,
  summary: item.summary,
  source: item.source,
  updatedAt: item.updatedAt,
}));
