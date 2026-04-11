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
