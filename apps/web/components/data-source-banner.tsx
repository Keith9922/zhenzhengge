import { AlertTriangle, DatabaseZap, WifiOff } from "lucide-react";
import { buildDemoDataNote, type DataSourceState } from "@/lib/data-source";

type DataSourceBannerProps = {
  source: DataSourceState;
  label: string;
  note?: string;
};

export function DataSourceBanner({ source, label, note }: DataSourceBannerProps) {
  if (source === "api") {
    return null;
  }

  const tone =
    source === "error"
      ? "border-rose-200 bg-rose-50 text-rose-900"
      : "border-amber-200 bg-amber-50 text-amber-900";
  const icon = source === "error" ? WifiOff : DatabaseZap;
  const Icon = icon;
  const message = note || buildDemoDataNote(label);
  const badge = `source=${source}`;

  return (
    <div className={`rounded-[1.75rem] border px-5 py-4 shadow-sm ${tone}`}>
      <div className="flex flex-wrap items-start gap-3">
        <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-2xl bg-white/80">
          <Icon className="h-4 w-4" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-sm font-semibold">{label}</p>
            <span className="rounded-full bg-white/80 px-2.5 py-1 text-[11px] font-medium uppercase tracking-[0.2em]">{badge}</span>
          </div>
          <p className="mt-1 text-sm leading-6">{message}</p>
        </div>
        {source === "error" ? <AlertTriangle className="mt-1 h-4 w-4 shrink-0" /> : null}
      </div>
    </div>
  );
}
