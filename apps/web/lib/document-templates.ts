import { fetchJsonOrUndefined } from "@/lib/api";
import { buildApiErrorNote, type ListFetchResult } from "@/lib/data-source";

export type DocumentTemplateItem = {
  templateKey: string;
  name: string;
  category: string;
  description: string;
  targetUse: string;
  outputFormats: string[];
  isActive: boolean;
};

type ApiDocumentTemplateItem = {
  template_key?: string;
  name?: string;
  category?: string;
  description?: string;
  target_use?: string;
  output_formats?: string[];
  is_active?: boolean;
};

type ApiDocumentTemplateList = {
  total?: number;
  items?: ApiDocumentTemplateItem[];
};

function toStringValue(value: unknown, fallback = "") {
  if (typeof value === "string" && value.trim()) {
    return value.trim();
  }

  return fallback;
}

function toStringArray(value: unknown) {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.map((item) => toStringValue(item)).filter(Boolean);
}

function normalizeTemplate(item: ApiDocumentTemplateItem, index = 0): DocumentTemplateItem {
  return {
    templateKey: toStringValue(item.template_key, `template-${index + 1}`),
    name: toStringValue(item.name, `文书模板 ${index + 1}`),
    category: toStringValue(item.category, "通用"),
    description: toStringValue(item.description, "暂无模板说明。"),
    targetUse: toStringValue(item.target_use, "用于文书草稿生成与复核。"),
    outputFormats: toStringArray(item.output_formats),
    isActive: item.is_active !== false,
  };
}

export async function getDocumentTemplates(): Promise<ListFetchResult<DocumentTemplateItem>> {
  const payload = await fetchJsonOrUndefined<ApiDocumentTemplateList>("/document-templates");

  if (!payload?.items) {
    return {
      items: [],
      source: "error",
      note: buildApiErrorNote("文书模板"),
    };
  }

  return {
    items: payload.items.map((item, index) => normalizeTemplate(item, index)),
    source: "api",
  };
}
