import { fetchJsonOrUndefined } from "@/lib/api";
import { buildApiErrorNote, type ListFetchResult } from "@/lib/data-source";

export type RuntimeModuleItem = {
  name: string;
  status: string;
  description: string;
};

type ApiRuntimeModuleItem = {
  name?: string;
  status?: string;
  description?: string | null;
};

function toStringValue(value: unknown, fallback = "") {
  if (typeof value === "string" && value.trim()) {
    return value.trim();
  }

  return fallback;
}

function normalizeRuntimeModule(item: ApiRuntimeModuleItem, index = 0): RuntimeModuleItem {
  return {
    name: toStringValue(item.name, `module-${index + 1}`),
    status: toStringValue(item.status, "unknown"),
    description: toStringValue(item.description, "暂无说明"),
  };
}

export async function getRuntimeModules(): Promise<ListFetchResult<RuntimeModuleItem>> {
  const payload = await fetchJsonOrUndefined<ApiRuntimeModuleItem[]>("/runtime/modules");

  if (!payload) {
    return {
      items: [],
      source: "error",
      note: buildApiErrorNote("运行时模块状态"),
    };
  }

  return {
    items: payload.map((item, index) => normalizeRuntimeModule(item, index)),
    source: "api",
  };
}
