import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "证证鸽｜AI 知识产权侵权响应平台",
  description: "面向品牌方与法务团队的 AI 知识产权侵权响应平台，覆盖网页取证、证据沉淀、风险研判与草稿生成。",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
