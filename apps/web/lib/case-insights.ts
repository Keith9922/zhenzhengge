import { fetchJsonOrUndefined } from "@/lib/api";
import { buildApiErrorNote, type DetailFetchResult } from "@/lib/data-source";

export type CaseInsights = {
  totalCases: number;
  casesWithActions: number;
  actionRate: number;
  evidencePassRate: number;
  ttaHours?: number;
  generatedAt: string;
};

type ApiCaseInsights = {
  total_cases?: number;
  cases_with_actions?: number;
  action_rate?: number;
  evidence_pass_rate?: number;
  tta_hours?: number | null;
  generated_at?: string;
};

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

function toStringValue(value: unknown, fallback = "") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function normalize(payload: ApiCaseInsights): CaseInsights {
  const tta = payload.tta_hours;
  return {
    totalCases: toNumberValue(payload.total_cases, 0),
    casesWithActions: toNumberValue(payload.cases_with_actions, 0),
    actionRate: toNumberValue(payload.action_rate, 0),
    evidencePassRate: toNumberValue(payload.evidence_pass_rate, 0),
    ttaHours: typeof tta === "number" && Number.isFinite(tta) ? tta : undefined,
    generatedAt: toStringValue(payload.generated_at, ""),
  };
}

export async function getCaseInsights(): Promise<DetailFetchResult<CaseInsights>> {
  const payload = await fetchJsonOrUndefined<ApiCaseInsights>("/cases/insights");
  if (!payload) {
    return {
      source: "error",
      note: buildApiErrorNote("处置效率看板"),
    };
  }
  return {
    item: normalize(payload),
    source: "api",
  };
}
