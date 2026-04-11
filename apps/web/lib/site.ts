import { BookOpen, FileText, FolderKanban, ScanSearch, ShieldCheck, Sparkles } from "lucide-react";
import { publicDocEntries } from "@/lib/docs";

export const productHighlights = [
  {
    title: "一键取证",
    description: "在淘宝、拼多多、京东、品牌官网等页面直接捕捉证据，转成标准化案件材料。",
    icon: ScanSearch,
  },
  {
    title: "证据归档",
    description: "把页面截图、文本与关键信息沉淀成可复查、可管理的证据包。",
    icon: ShieldCheck,
  },
  {
    title: "风险研判",
    description: "围绕近似命名、冒用展示和品牌混淆等公开线索提供辅助研判。",
    icon: Sparkles,
  },
  {
    title: "材料辅助",
    description: "围绕常见处置场景整理说明材料和初稿，降低后续沟通与处理成本。",
    icon: FileText,
  },
  {
    title: "案件协同",
    description: "让运营、法务和品牌团队围绕同一条线索查看进展、整理材料和推进动作。",
    icon: FolderKanban,
  },
  {
    title: "产品资料",
    description: "集中了解产品定位、适用场景和能力边界，快速判断是否适合当前业务需求。",
    icon: BookOpen,
  },
];

export const workflowSteps = [
  {
    title: "发现线索",
    detail: "用户在公开网页中发现疑似侵权内容，或对指定目标持续观察后发现新线索。",
  },
  {
    title: "发起取证",
    detail: "围绕当前页面留存截图、页面信息和关键说明，形成可管理的案件入口。",
  },
  {
    title: "证据归档",
    detail: "系统把线索整理为结构化证据包，方便后续查看、比对和推进处理。",
  },
  {
    title: "风险研判",
    detail: "结合近似命名、冒用展示和页面内容，给出辅助判断与处理建议。",
  },
  {
    title: "材料准备",
    detail: "围绕常见处置场景整理说明材料和初稿，帮助团队更快进入下一步动作。",
  },
  {
    title: "人工确认",
    detail: "最终由业务或法务人员确认判断与动作，保证输出稳健、可控。",
  },
];

export const docsIndex = [
  ...publicDocEntries,
];

export const workspaceNav = [
  { href: "/workspace", label: "总览" },
  { href: "/workspace/cases", label: "案件" },
  { href: "/workspace/templates", label: "模板" },
  { href: "/workspace/settings", label: "设置" },
];
