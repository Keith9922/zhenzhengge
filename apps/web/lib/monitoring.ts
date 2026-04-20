import { fetchJsonOrUndefined } from "@/lib/api";
import { buildApiErrorNote, type DetailFetchResult, type ListFetchResult } from "@/lib/data-source";

export type MonitorTaskItem = {
  id: string;
  name: string;
  targetUrl: string;
  site: string;
  frequencyMinutes: number;
  riskThreshold: number;
  status: string;
  lastRunAt?: string;
};

type ApiMonitorTask = {
  task_id?: string;
  name?: string;
  target_url?: string;
  site?: string;
  frequency_minutes?: number;
  risk_threshold?: number;
  status?: string;
  last_run_at?: string | null;
};

type ApiMonitorTaskList = {
  total?: number;
  items?: ApiMonitorTask[];
};

function toStringValue(value: unknown, fallback = "") {
  if (typeof value === "string" && value.trim()) {
    return value.trim();
  }

  return fallback;
}

function toNumberValue(value: unknown, fallback = 0) {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function normalizeTask(record: ApiMonitorTask, index = 0): MonitorTaskItem {
  return {
    id: toStringValue(record.task_id, `monitor-${index + 1}`),
    name: toStringValue(record.name, `监控任务 ${index + 1}`),
    targetUrl: toStringValue(record.target_url, "https://example.com"),
    site: toStringValue(record.site, "公开网页"),
    frequencyMinutes: toNumberValue(record.frequency_minutes, 60),
    riskThreshold: toNumberValue(record.risk_threshold, 70),
    status: toStringValue(record.status, "active"),
    lastRunAt: toStringValue(record.last_run_at),
  };
}

export async function getMonitorTasks(): Promise<ListFetchResult<MonitorTaskItem>> {
  const payload = await fetchJsonOrUndefined<ApiMonitorTaskList>("/monitor-tasks");
  const items = payload?.items;

  if (!items) {
    return {
      items: [],
      source: "error",
      note: buildApiErrorNote("监控任务"),
    };
  }

  return {
    items: items.map((item, index) => normalizeTask(item, index)),
    source: "api",
  };
}

export async function getMonitorTask(taskId: string): Promise<DetailFetchResult<MonitorTaskItem>> {
  const payload = await fetchJsonOrUndefined<ApiMonitorTask>(`/monitor-tasks/${encodeURIComponent(taskId)}`);

  if (!payload) {
    return {
      source: "error",
      note: buildApiErrorNote("监控任务详情"),
    };
  }

  return {
    item: normalizeTask(payload),
    source: "api",
  };
}
