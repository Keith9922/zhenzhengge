import { fetchJsonOrUndefined } from "@/lib/api";
import { buildApiErrorNote, type ListFetchResult } from "@/lib/data-source";

export type NotificationChannelItem = {
  id: string;
  name: string;
  typeLabel: string;
  target: string;
  enabled: boolean;
  updatedAt: string;
};

export type NotificationLogItem = {
  id: string;
  channelId: string;
  eventType: string;
  subject: string;
  status: string;
  detail: string;
  createdAt: string;
};

type ApiNotificationChannel = {
  channel_id?: string;
  channel_type?: string;
  name?: string;
  target?: string;
  enabled?: boolean;
  updated_at?: string;
};

type ApiNotificationList = {
  total?: number;
  items?: ApiNotificationChannel[];
};

type ApiNotificationLog = {
  log_id?: string;
  channel_id?: string;
  event_type?: string;
  subject?: string;
  status?: string;
  detail?: string;
  created_at?: string;
};

function toStringValue(value: unknown, fallback = "") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function toTypeLabel(value: unknown) {
  const normalized = toStringValue(value).toLowerCase();
  if (normalized === "dingtalk") {
    return "即时提醒";
  }
  if (normalized === "email") {
    return "邮件提醒";
  }
  return "接收方式";
}

function normalizeChannel(record: ApiNotificationChannel, index = 0): NotificationChannelItem {
  return {
    id: toStringValue(record.channel_id, `channel-${index + 1}`),
    name: toStringValue(record.name, `接收方式 ${index + 1}`),
    typeLabel: toTypeLabel(record.channel_type),
    target: toStringValue(record.target, "待补充"),
    enabled: Boolean(record.enabled),
    updatedAt: toStringValue(record.updated_at, "待更新"),
  };
}

function normalizeLog(record: ApiNotificationLog, index = 0): NotificationLogItem {
  return {
    id: toStringValue(record.log_id, `log-${index + 1}`),
    channelId: toStringValue(record.channel_id, "unknown"),
    eventType: toStringValue(record.event_type, "unknown"),
    subject: toStringValue(record.subject, "未命名通知"),
    status: toStringValue(record.status, "unknown"),
    detail: toStringValue(record.detail, "无详情"),
    createdAt: toStringValue(record.created_at, "待更新"),
  };
}

export async function getNotificationChannels(): Promise<ListFetchResult<NotificationChannelItem>> {
  const payload = await fetchJsonOrUndefined<ApiNotificationList>("/notification-channels");
  const items = payload?.items;

  if (!items) {
    return {
      items: [],
      source: "error",
      note: buildApiErrorNote("接收方式"),
    };
  }

  return {
    items: items.map((item, index) => normalizeChannel(item, index)),
    source: "api",
  };
}

export async function getNotificationLogs(limit = 20): Promise<ListFetchResult<NotificationLogItem>> {
  const items = await fetchJsonOrUndefined<ApiNotificationLog[]>(`/notification-channels/logs?limit=${limit}`);

  if (!items) {
    return {
      items: [],
      source: "error",
      note: buildApiErrorNote("通知日志"),
    };
  }

  return {
    items: items.map((item, index) => normalizeLog(item, index)),
    source: "api",
  };
}
