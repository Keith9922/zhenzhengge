import { BookOpen, Bot, FileText, ScanSearch, ShieldCheck, Sparkles } from "lucide-react";
import { docEntries } from "@/lib/docs";
import { getRepoUrl } from "@/lib/env";

export const productHighlights = [
  {
    title: "一键取证",
    description: "在淘宝、拼多多、京东、品牌官网等页面直接捕捉证据，转成标准化案件材料。",
    icon: ScanSearch,
  },
  {
    title: "自动固证",
    description: "服务端补抓页面、截图、HTML、时间戳与哈希，沉淀为可追踪的证据包。",
    icon: ShieldCheck,
  },
  {
    title: "风险分析",
    description: "对商标、图样和命名做近似预筛，输出高风险线索与建议动作。",
    icon: Sparkles,
  },
  {
    title: "文书辅助",
    description: "基于案件事实和模板生成初稿，进入法务审核流程后再导出正式版本。",
    icon: FileText,
  },
  {
    title: "消息推送",
    description: "通过钉钉或邮箱把案件摘要、证据链接和下一步动作推送给负责人。",
    icon: Bot,
  },
  {
    title: "文档入口",
    description: "集中查阅 PRD、技术选型、开源清单和项目资料包，作为开发对齐基线。",
    icon: BookOpen,
  },
];

export const workflowSteps = [
  {
    title: "发现线索",
    detail: "用户在浏览器中发现疑似侵权页面，或者由后台巡检发现更新。",
  },
  {
    title: "一键取证",
    detail: "插件采集 URL、标题、截图和备注，服务端补抓完整页面材料。",
  },
  {
    title: "分析评分",
    detail: "系统输出相似度、风险等级、命中原因和建议动作。",
  },
  {
    title: "推送通知",
    detail: "钉钉或邮箱立即收到案件摘要与证据包入口。",
  },
  {
    title: "生成初稿",
    detail: "选择模板后一键生成律师函、投诉函或举报材料初稿。",
  },
  {
    title: "人工审核",
    detail: "法务审核后再导出正式材料，保留版本和审计日志。",
  },
];

export const docsIndex = [
  ...docEntries,
];

export { getRepoUrl };

export const workspaceNav = [
  { href: "/workspace", label: "总览" },
  { href: "/workspace/cases", label: "案件" },
  { href: "/workspace/templates", label: "模板" },
  { href: "/workspace/settings", label: "设置" },
];
