import { AlertTriangle, WifiOff } from "lucide-react";
import { buildApiErrorNote, type DataSourceState } from "@/lib/data-source";

type DataSourceBannerProps = {
  source: DataSourceState;
  label: string;
  note?: string;
};

export function DataSourceBanner({ source, label, note }: DataSourceBannerProps) {
  if (source !== "error") {
    return null;
  }

  const tone = "border-rose-200 bg-rose-50 text-rose-900";
  const message = note || buildApiErrorNote(label);
  const badge = "接口异常";

  return (
    <div className={`rounded-[1.75rem] border px-5 py-4 shadow-sm ${tone}`}>
      <div className="flex flex-wrap items-start gap-3">
        <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-2xl bg-white/80">
          <WifiOff className="h-4 w-4" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-sm font-semibold">{label}</p>
            <span className="rounded-full bg-white/80 px-2.5 py-1 text-[11px] font-medium tracking-[0.2em]">{badge}</span>
          </div>
          <p className="mt-1 text-sm leading-6">{message}</p>
        </div>
        <AlertTriangle className="mt-1 h-4 w-4 shrink-0" />
      </div>
    </div>
  );
}
