import { getApiV1BaseUrl } from "@/lib/env";

export type CaseStatus = "高风险" | "待复核" | "处理中" | "已完成";

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
  notes: string[];
  evidenceItems: string[];
  nextActions: string[];
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
    notes: [
      "商品标题与目标品牌高度近似。",
      "页面视觉元素存在品牌混淆风险。",
      "已生成证据包，等待法务复核。",
    ],
    evidenceItems: ["URL", "页面标题", "全页截图", "HTML", "抓取时间", "哈希值", "图片链接", "操作日志"],
    nextActions: ["生成律师函初稿", "推送钉钉通知", "导出证据目录"],
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
    notes: ["图文混用，需拆分识别文字与图片。", "风险中等偏高。", "后续可进入投诉材料阶段。"],
    evidenceItems: ["URL", "页面标题", "截图", "文本", "图片哈希", "抓取时间"],
    nextActions: ["发送邮箱通知", "生成平台投诉函", "等待审核"],
  },
];

function normalize(value: string) {
  return value.trim().toLowerCase();
}

function buildCasesEndpoint(path = "") {
  const baseUrl = getApiV1BaseUrl();
  if (!baseUrl) {
    return "";
  }

  const normalizedPath = path ? `/${path.replace(/^\/+/, "")}` : "";
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

function extractCaseDetail(payload: unknown): CaseDetail | undefined {
  if (!payload || typeof payload !== "object") {
    return undefined;
  }

  const direct = payload as CaseDetail & { item?: unknown; data?: unknown; case?: unknown };
  const candidates = [direct, direct.item, direct.data, direct.case].filter(Boolean);

  for (const candidate of candidates) {
    if (candidate && typeof candidate === "object" && "id" in candidate && "title" in candidate) {
      return candidate as CaseDetail;
    }
  }

  return undefined;
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
    const items = extractCaseList(payload);

    if (!items.length) {
      return { items: mockCases, source: "mock" as const };
    }

    return { items, source: "api" as const };
  } catch {
    return { items: mockCases, source: "mock" as const };
  }
}

export async function getCaseById(caseId: string) {
  const endpoint = buildCasesEndpoint(encodeURIComponent(caseId));
  if (endpoint) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 2500);
      const response = await fetch(endpoint, {
        cache: "no-store",
        signal: controller.signal,
      }).finally(() => clearTimeout(timeout));

      if (response.ok) {
        const payload = await response.json();
        const item = extractCaseDetail(payload);
        if (item) {
          return item;
        }
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
