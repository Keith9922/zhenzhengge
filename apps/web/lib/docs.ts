import { getRepoUrl } from "@/lib/env";

export type DocSlug = "prd" | "tech-selection" | "project-package";

export type PublicDocEntry = {
  slug: DocSlug;
  title: string;
  summary: string;
  href: string;
  bullets: string[];
};

export type InternalDocEntry = {
  slug: DocSlug;
  title: string;
  summary: string;
  href: string;
  sourcePath: string;
  bullets: string[];
};

export const publicDocEntries: PublicDocEntry[] = [
  {
    slug: "prd",
    title: "产品概览",
    summary: "快速了解证证鸽解决什么问题、适合谁用，以及当前版本聚焦的核心价值。",
    href: "/docs/prd",
    bullets: [
      "聚焦公开网页场景下的侵权线索发现、取证与材料整理。",
      "适合品牌方、法务团队、电商运营与知识产权管理人员使用。",
      "强调先留证、再研判、再进入后续处置动作。",
    ],
  },
  {
    slug: "tech-selection",
    title: "适用场景",
    summary: "明确当前版本最适合处理的页面类型、线索类型与典型使用方式。",
    href: "/docs/tech-selection",
    bullets: [
      "优先面向淘宝、拼多多、京东和品牌官网等公开网页场景。",
      "重点处理商标冒用、近似命名、图文混用和仿冒展示等问题。",
      "既支持主动取证，也支持对指定目标进行持续巡检。",
    ],
  },
  {
    slug: "project-package",
    title: "能力边界",
    summary: "说明系统当前能帮助用户完成什么，以及哪些动作仍需人工确认。",
    href: "/docs/project-package",
    bullets: [
      "系统输出的是疑似侵权线索、风险提示和材料初稿，不替代最终法律认定。",
      "当前版本重心是取证固证、风险研判和材料辅助，不直接自动执行正式投诉或起诉。",
      "所有处置动作都建议结合人工审核与业务判断推进。",
    ],
  },
];

export const internalDocEntries: InternalDocEntry[] = [
  {
    slug: "prd",
    title: "PRD",
    summary: "产品边界、目标角色、核心链路与成功标准。",
    href: "/internal/docs/prd",
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
    href: "/internal/docs/tech-selection",
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
    href: "/internal/docs/project-package",
    sourcePath: "docs/zhenzhengge-project-package.md",
    bullets: [
      "品牌名采用“证证鸽”。",
      "主链路为主动取证 + 自动监测 + 文书辅助。",
      "Landing Page 作为主站入口和资料入口。",
    ],
  },
];

export function getPublicDocBySlug(slug: DocSlug) {
  return publicDocEntries.find((doc) => doc.slug === slug);
}

export function getInternalDocBySlug(slug: DocSlug) {
  return internalDocEntries.find((doc) => doc.slug === slug);
}

export function getDocSourceUrl(sourcePath: string) {
  return `${getRepoUrl()}/blob/main/${sourcePath}`;
}
