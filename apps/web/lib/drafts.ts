import { fetchJsonOrUndefined } from "@/lib/api";

export type DraftItem = {
  id: string;
  caseId: string;
  title: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  templateKey: string;
  content: string;
  reviewComment?: string;
  exportPath?: string;
};

type ApiDraft = {
  draft_id?: string;
  case_id?: string;
  title?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
  template_key?: string;
  content?: string;
  review_comment?: string | null;
  export_path?: string | null;
};

type ApiDraftListPayload = {
  total?: number;
  items?: ApiDraft[];
};

const mockDrafts: DraftItem[] = [
  {
    id: "draft-0001",
    caseId: "case-zhzg-0001",
    title: "阿迪达斯变体商品页疑似仿冒 - 律师函初稿",
    status: "generated",
    createdAt: "2026-04-11T08:00:00+00:00",
    updatedAt: "2026-04-11T08:00:00+00:00",
    templateKey: "lawyer-letter",
    content: "## 律师函初稿\n\n现就相关页面中的疑似侵权展示提出说明与整改要求。",
  },
];

function toStringValue(value: unknown, fallback = "") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function normalizeDraft(record: ApiDraft, index = 0): DraftItem {
  return {
    id: toStringValue(record.draft_id, `draft-${index + 1}`),
    caseId: toStringValue(record.case_id, "未关联案件"),
    title: toStringValue(record.title, `文书草稿 ${index + 1}`),
    status: toStringValue(record.status, "generated"),
    createdAt: toStringValue(record.created_at, "待补充"),
    updatedAt: toStringValue(record.updated_at, "待补充"),
    templateKey: toStringValue(record.template_key, "lawyer-letter"),
    content: toStringValue(record.content, "暂无草稿内容。"),
    reviewComment: toStringValue(record.review_comment),
    exportPath: toStringValue(record.export_path),
  };
}

export async function getDrafts(caseId?: string) {
  const query = caseId ? `?case_id=${encodeURIComponent(caseId)}` : "";
  const payload = await fetchJsonOrUndefined<ApiDraftListPayload>(`/document-drafts${query}`);
  const items = payload?.items;

  if (!items?.length) {
    const fallback = caseId ? mockDrafts.filter((item) => item.caseId === caseId) : mockDrafts;
    return { items: fallback, source: "mock" as const };
  }

  return {
    items: items.map((item, index) => normalizeDraft(item, index)),
    source: "api" as const,
  };
}

export async function getDraftById(draftId: string) {
  const payload = await fetchJsonOrUndefined<ApiDraft>(`/document-drafts/${encodeURIComponent(draftId)}`);
  if (!payload) {
    return mockDrafts.find((item) => item.id === draftId);
  }

  return normalizeDraft(payload);
}
