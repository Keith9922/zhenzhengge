import type { ReactNode } from "react";
import Link from "next/link";
import { workspaceNav } from "@/lib/site";

export function WorkspaceShell({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
      <div className="border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
          <div>
            <p className="text-sm font-semibold text-brand-700">证证鸽工作台</p>
            <p className="text-xs text-slate-500">案件、证据包、模板与审核流</p>
          </div>
          <Link href="/" className="text-sm font-medium text-slate-600 hover:text-ink">
            返回主站
          </Link>
        </div>
      </div>
      <div className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-[220px_minmax(0,1fr)] lg:px-8">
        <aside className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-4 rounded-2xl bg-brand-50 px-4 py-3">
            <p className="text-sm font-semibold text-ink">{title}</p>
            <p className="mt-1 text-xs leading-5 text-slate-600">{description}</p>
          </div>
          <nav className="space-y-1">
            {workspaceNav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="block rounded-2xl px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-100 hover:text-ink"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </aside>
        <main className="space-y-6">{children}</main>
      </div>
    </div>
  );
}
