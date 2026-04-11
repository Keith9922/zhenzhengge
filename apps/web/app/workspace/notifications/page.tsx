import { DataSourceBanner } from "@/components/data-source-banner";
import { NotificationConsole } from "@/components/workspace/notification-console";
import { getNotificationChannels } from "@/lib/notifications";

export const dynamic = "force-dynamic";

export default async function NotificationsPage() {
  const { items, source, note } = await getNotificationChannels();

  return (
    <section className="space-y-6">
      <DataSourceBanner source={source} label="接收方式" note={note} />
      <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-brand-700">接收方式</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink">提醒接收设置</h1>
        <p className="mt-4 text-sm leading-7 text-slate-600">
          在这里管理线索更新、材料处理和任务执行时的默认接收入口，并支持发送测试消息确认可用性。
        </p>
      </div>
      <NotificationConsole items={items} />
    </section>
  );
}
