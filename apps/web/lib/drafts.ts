import { fetchJsonOrUndefined } from "@/lib/api";
import { buildApiErrorNote, type DetailFetchResult, type ListFetchResult } from "@/lib/data-source";

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

function toStringValue(value: unknown, fallback = "") {
  if (typeof value === "string" && value.trim()) {
    return value.trim();
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return String(value);
  }

  return fallback;
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

export async function getDrafts(caseId?: string): Promise<ListFetchResult<DraftItem>> {
  const query = caseId ? `?case_id=${encodeURIComponent(caseId)}` : "";
  const payload = await fetchJsonOrUndefined<ApiDraftListPayload>(`/document-drafts${query}`);

  if (!payload) {
    return {
      items: [],
      source: "error",
      note: buildApiErrorNote("草稿列表"),
    };
  }

  const items = payload.items ?? [];

  return {
    items: items.map((item, index) => normalizeDraft(item, index)),
    source: "api",
  };
}

export async function getDraftById(draftId: string): Promise<DetailFetchResult<DraftItem>> {
  const payload = await fetchJsonOrUndefined<ApiDraft>(`/document-drafts/${encodeURIComponent(draftId)}`);

  if (!payload) {
    return {
      source: "error",
      note: buildApiErrorNote("草稿详情"),
    };
  }

  return {
    item: normalizeDraft(payload),
    source: "api",
  };
}
