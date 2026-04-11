import { fetchJsonOrUndefined } from "@/lib/api";

export type EvidencePackListItem = {
  id: string;
  caseId: string;
  title: string;
  source: string;
  capturedAt: string;
  status: string;
  summary: string;
  artifactPaths: string[];
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

const mockEvidencePacks: EvidencePackListItem[] = [
  {
    id: "pack-adidas-001",
    caseId: "case-adidas-aaodasis",
    title: "阿波达斯商品页抓取包",
    source: "公开网页",
    capturedAt: "2026-04-11 10:12",
    status: "已归档",
    summary: "包含页面标题、来源地址、截图路径和页面源文件路径。",
    artifactPaths: ["snapshot.png", "page.html"],
  },
];

function toStringValue(value: unknown, fallback = "") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function normalizePack(record: ApiEvidencePack, index = 0): EvidencePackListItem {
  const title = toStringValue(record.source_title, `证据包 ${index + 1}`);
  const artifactPaths = [record.snapshot_path, record.html_path]
    .map((item) => toStringValue(item))
    .filter(Boolean);

  return {
    id: toStringValue(record.evidence_pack_id, `evidence-pack-${index + 1}`),
    caseId: toStringValue(record.case_id, "未关联案件"),
    title,
    source: toStringValue(record.source_url, "公开网页"),
    capturedAt: toStringValue(record.created_at, "待补充"),
    status: toStringValue(record.status, "captured"),
    summary: toStringValue(record.note, "已生成基础证据包，可继续补充说明与处置材料。"),
    artifactPaths,
  };
}

export async function getEvidencePacks() {
  const payload = await fetchJsonOrUndefined<ApiEvidencePack[] | { items?: ApiEvidencePack[] }>("/evidence-packs");
  const rawItems = Array.isArray(payload) ? payload : payload?.items;
  if (!rawItems?.length) {
    return { items: mockEvidencePacks, source: "mock" as const };
  }

  return {
    items: rawItems.map((item, index) => normalizePack(item, index)),
    source: "api" as const,
  };
}

export async function getEvidencePackById(packId: string) {
  const payload = await fetchJsonOrUndefined<ApiEvidencePack>(`/evidence-packs/${encodeURIComponent(packId)}`);
  if (!payload) {
    return mockEvidencePacks.find((item) => item.id === packId);
  }

  return normalizePack(payload);
}
