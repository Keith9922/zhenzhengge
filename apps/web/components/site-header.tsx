import Link from "next/link";
import { LogoMark } from "@/components/logo";

const navItems = [
  { href: "#workflow", label: "功能链路" },
  { href: "#docs", label: "文档入口" },
  { href: "#workspace", label: "工作台" },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/50 bg-white/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
        <Link href="/" className="flex items-center gap-3">
          <LogoMark className="h-11 w-11" />
          <div>
            <p className="text-sm font-semibold text-ink">证证鸽</p>
            <p className="text-xs text-slate-500">侵权取证与处置工作台</p>
          </div>
        </Link>
        <nav className="hidden items-center gap-6 md:flex">
          {navItems.map((item) => (
            <a key={item.href} href={item.href} className="text-sm font-medium text-slate-600 transition hover:text-ink">
              {item.label}
            </a>
          ))}
          <Link
            href="/workspace"
            className="rounded-full bg-ink px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
          >
            进入工作台
          </Link>
        </nav>
      </div>
    </header>
  );
}
