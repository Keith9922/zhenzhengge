import { fetchJsonOrUndefined } from "@/lib/api";
import { buildApiErrorNote, type ListFetchResult } from "@/lib/data-source";

export type RuntimeModuleItem = {
  name: string;
  status: string;
  description: string;
};

export type RuntimeCompliance = {
  requireAuth: boolean;
  demoSeedEnabled: boolean;
  draftGenerationStrict: boolean;
  captureAllowHttpFallback: boolean;
  harnessAgentEnabled: boolean;
  evidenceTimestampEnabled: boolean;
  evidenceTimestampRequired: boolean;
  evidenceTimestampReady: boolean;
  extensionTokenConfigured: boolean;
  llmProvider: string;
  llmReady: boolean;
  complianceReady: boolean;
  warnings: string[];
};

type ApiRuntimeModuleItem = {
  name?: string;
  status?: string;
  description?: string | null;
};

type ApiRuntimeCompliance = {
  require_auth?: boolean;
  demo_seed_enabled?: boolean;
  draft_generation_strict?: boolean;
  capture_allow_http_fallback?: boolean;
  harness_agent_enabled?: boolean;
  evidence_timestamp_enabled?: boolean;
  evidence_timestamp_required?: boolean;
  evidence_timestamp_ready?: boolean;
  extension_token_configured?: boolean;
  llm_provider?: string;
  llm_ready?: boolean;
  compliance_ready?: boolean;
  warnings?: unknown;
};

function toStringValue(value: unknown, fallback = "") {
  if (typeof value === "string" && value.trim()) {
    return value.trim();
  }

  return fallback;
}

function toBooleanValue(value: unknown, fallback = false) {
  if (typeof value === "boolean") {
    return value;
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

function toStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((item) => toStringValue(item))
    .filter(Boolean);
}

function normalizeRuntimeCompliance(payload: ApiRuntimeCompliance): RuntimeCompliance {
  return {
    requireAuth: toBooleanValue(payload.require_auth),
    demoSeedEnabled: toBooleanValue(payload.demo_seed_enabled),
    draftGenerationStrict: toBooleanValue(payload.draft_generation_strict),
    captureAllowHttpFallback: toBooleanValue(payload.capture_allow_http_fallback),
    harnessAgentEnabled: toBooleanValue(payload.harness_agent_enabled),
    evidenceTimestampEnabled: toBooleanValue(payload.evidence_timestamp_enabled),
    evidenceTimestampRequired: toBooleanValue(payload.evidence_timestamp_required),
    evidenceTimestampReady: toBooleanValue(payload.evidence_timestamp_ready),
    extensionTokenConfigured: toBooleanValue(payload.extension_token_configured),
    llmProvider: toStringValue(payload.llm_provider, "unknown"),
    llmReady: toBooleanValue(payload.llm_ready),
    complianceReady: toBooleanValue(payload.compliance_ready),
    warnings: toStringArray(payload.warnings),
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

export async function getRuntimeCompliance(): Promise<
  { item: RuntimeCompliance; source: "api"; note?: undefined } | { item: null; source: "error"; note: string }
> {
  const payload = await fetchJsonOrUndefined<ApiRuntimeCompliance>("/runtime/compliance");
  if (!payload) {
    return {
      item: null,
      source: "error",
      note: buildApiErrorNote("合规状态"),
    };
  }

  return {
    item: normalizeRuntimeCompliance(payload),
    source: "api",
  };
}
