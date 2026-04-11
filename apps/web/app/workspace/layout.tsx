import type { ReactNode } from "react";
import { WorkspaceShell } from "@/components/workspace-shell";

export default function WorkspaceLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <WorkspaceShell
      title="工作台总览"
      description="围绕案件、证据包、模板和审核流进行操作，先把取证与处置闭环跑通。"
    >
      {children}
    </WorkspaceShell>
  );
}
