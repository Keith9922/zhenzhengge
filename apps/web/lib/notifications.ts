import { fetchJsonOrUndefined } from "@/lib/api";
import { buildDemoDataNote, type ListFetchResult } from "@/lib/data-source";

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

const mockChannels: NotificationChannelItem[] = [
  {
    id: "channel-0001",
    name: "默认接收方式",
    typeLabel: "邮件提醒",
    target: "legal@example.com",
    enabled: true,
    updatedAt: "2026-04-11T08:00:00+00:00",
  },
];

const mockLogs: NotificationLogItem[] = [
  {
    id: "log-0001",
    channelId: "channel-0001",
    eventType: "manual_test",
    subject: "证证鸽测试提醒",
    status: "dry-run",
    detail: "演示环境使用模拟日志。",
    createdAt: "2026-04-12T00:00:00+00:00",
  },
];

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

  if (!items?.length) {
    return { items: mockChannels, source: "mock", note: buildDemoDataNote("接收方式") };
  }

  return {
    items: items.map((item, index) => normalizeChannel(item, index)),
    source: "api",
  };
}

export async function getNotificationLogs(limit = 20): Promise<ListFetchResult<NotificationLogItem>> {
  const items = await fetchJsonOrUndefined<ApiNotificationLog[]>(`/notification-channels/logs?limit=${limit}`);

  if (!items?.length) {
    return { items: mockLogs, source: "mock", note: buildDemoDataNote("通知日志") };
  }

  return {
    items: items.map((item, index) => normalizeLog(item, index)),
    source: "api",
  };
}
