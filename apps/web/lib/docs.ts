import { getRepoUrl } from "@/lib/env";

export type DocSlug = "prd" | "tech-selection" | "project-package";

export type DocEntry = {
  slug: DocSlug;
  title: string;
  summary: string;
  href: string;
  sourcePath: string;
  bullets: string[];
};

export const docEntries: DocEntry[] = [
  {
    slug: "prd",
    title: "PRD",
    summary: "产品边界、目标角色、核心链路与成功标准。",
    href: "/docs/prd",
    sourcePath: "docs/zhenzhengge-prd.md",
    bullets: [
      "初版优先聚焦国内公开网页场景。",
      "重心放在取证固证，文书是后续连带能力。",
      "输出统一使用“疑似侵权”“建议人工复核”等表述。",
    ],
  },
  {
    slug: "tech-selection",
    title: "技术选型表",
    summary: "Plasmo、Next.js、FastAPI、Hermes 和通知方案的正式选型。",
    href: "/docs/tech-selection",
    sourcePath: "docs/zhenzhengge-tech-selection.md",
    bullets: [
      "前端以 Next.js + Tailwind 为主站与工作台骨架。",
      "Hermes 作为后端编排中枢，不暴露为开放聊天机器人。",
      "P0 优先接入 Plasmo、Playwright、RapidFuzz、docxtpl 和通知适配层。",
    ],
  },
  {
    slug: "project-package",
    title: "项目资料包",
    summary: "品牌、流程、模块命名与展示口径的统一入口。",
    href: "/docs/project-package",
    sourcePath: "docs/zhenzhengge-project-package.md",
    bullets: [
      "品牌名采用“证证鸽”。",
      "主链路为主动取证 + 自动监测 + 文书辅助。",
      "Landing Page 作为主站入口和资料入口。",
    ],
  },
];

export function getDocBySlug(slug: DocSlug) {
  return docEntries.find((doc) => doc.slug === slug);
}

export function getDocSourceUrl(sourcePath: string) {
  return `${getRepoUrl()}/blob/main/${sourcePath}`;
}
