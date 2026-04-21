import { fetchJsonOrUndefined } from "@/lib/api";
import { buildApiErrorNote, type DetailFetchResult } from "@/lib/data-source";

export type CaseActionItem = {
  actionId: string;
  title: string;
  description: string;
  priority: string;
  ctaLabel: string;
  href: string;
};

export type CaseActionCenter = {
  caseId: string;
  generatedAt: string;
  items: CaseActionItem[];
};

export type EvidenceClaimReference = {
  draftId: string;
  draftTitle: string;
  lineNo: number;
  claimText: string;
};

export type CaseEvidenceClaimLinkItem = {
  evidencePackId: string;
  sourceTitle: string;
  claimCount: number;
  claims: EvidenceClaimReference[];
};

export type CaseEvidenceClaimLinks = {
  caseId: string;
  generatedAt: string;
  totalEvidence: number;
  totalClaims: number;
  items: CaseEvidenceClaimLinkItem[];
};

type ApiCaseActionItem = {
  action_id?: string;
  title?: string;
  description?: string;
  priority?: string;
  cta_label?: string;
  href?: string;
};

type ApiCaseActionCenter = {
  case_id?: string;
  generated_at?: string;
  items?: ApiCaseActionItem[];
};

type ApiEvidenceClaimReference = {
  draft_id?: string;
  draft_title?: string;
  line_no?: number;
  claim_text?: string;
};

type ApiCaseEvidenceClaimLinkItem = {
  evidence_pack_id?: string;
  source_title?: string;
  claim_count?: number;
  claims?: ApiEvidenceClaimReference[];
};

type ApiCaseEvidenceClaimLinks = {
  case_id?: string;
  generated_at?: string;
  total_evidence?: number;
  total_claims?: number;
  items?: ApiCaseEvidenceClaimLinkItem[];
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

function normalizeActionCenter(payload: ApiCaseActionCenter): CaseActionCenter {
  const items = (payload.items || []).map((item, index) => ({
    actionId: toStringValue(item.action_id, `action-${index + 1}`),
    title: toStringValue(item.title, "待处理动作"),
    description: toStringValue(item.description, "请继续补充案件处理动作。"),
    priority: toStringValue(item.priority, "medium"),
    ctaLabel: toStringValue(item.cta_label, "去处理"),
    href: toStringValue(item.href, "/workspace/cases"),
  }));
  return {
    caseId: toStringValue(payload.case_id),
    generatedAt: toStringValue(payload.generated_at),
    items,
  };
}

function normalizeEvidenceClaimLinks(payload: ApiCaseEvidenceClaimLinks): CaseEvidenceClaimLinks {
  return {
    caseId: toStringValue(payload.case_id),
    generatedAt: toStringValue(payload.generated_at),
    totalEvidence: toNumberValue(payload.total_evidence, 0),
    totalClaims: toNumberValue(payload.total_claims, 0),
    items: (payload.items || []).map((item, index) => ({
      evidencePackId: toStringValue(item.evidence_pack_id, `ep-${index + 1}`),
      sourceTitle: toStringValue(item.source_title, "未命名证据"),
      claimCount: toNumberValue(item.claim_count, 0),
      claims: (item.claims || []).map((claim) => ({
        draftId: toStringValue(claim.draft_id),
        draftTitle: toStringValue(claim.draft_title, "未命名草稿"),
        lineNo: toNumberValue(claim.line_no, 0),
        claimText: toStringValue(claim.claim_text),
      })),
    })),
  };
}

export async function getCaseActionCenter(caseId: string): Promise<DetailFetchResult<CaseActionCenter>> {
  const payload = await fetchJsonOrUndefined<ApiCaseActionCenter>(`/cases/${encodeURIComponent(caseId)}/action-center`);
  if (!payload) {
    return {
      source: "error",
      note: buildApiErrorNote("案件动作中心"),
    };
  }
  return {
    item: normalizeActionCenter(payload),
    source: "api",
  };
}

export async function getCaseEvidenceClaimLinks(caseId: string): Promise<DetailFetchResult<CaseEvidenceClaimLinks>> {
  const payload = await fetchJsonOrUndefined<ApiCaseEvidenceClaimLinks>(
    `/cases/${encodeURIComponent(caseId)}/evidence-claim-links`,
  );
  if (!payload) {
    return {
      source: "error",
      note: buildApiErrorNote("证据主张关联"),
    };
  }
  return {
    item: normalizeEvidenceClaimLinks(payload),
    source: "api",
  };
}
