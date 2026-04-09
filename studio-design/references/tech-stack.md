# Tech Stack Reference — Astra Studio Frontend

## 技术选型

| 技术 | 用途 | 选型理由 |
|------|------|---------|
| **Next.js App Router** | 路由 + 渲染 | Server Components 减少客户端 bundle，SEO 友好 |
| **TanStack Query** | 服务端状态 | 自动缓存、失效、重试，避免手写 useEffect+fetch |
| **LangGraph SDK** | AI 通信 | 原生支持流式事件，与 DeerFlow 后端配套 |
| **Tailwind CSS 4** | 样式 | 工具类直接写在 JSX，不用切换文件 |
| **shadcn/ui** | 基础组件 | 代码直接进项目（可修改），不依赖黑盒 npm 包 |
| **CodeMirror** | 代码编辑 | 成熟的代码编辑器，支持语法高亮和语言插件 |
| **Radix UI** | 无障碍原语 | shadcn/ui 底层依赖，提供无样式但可访问的组件 |
| **Lucide React** | 图标库 | 与 shadcn/ui 配套，一致的设计语言 |
| **Zustand** | 客户端状态 | 轻量、无 Provider 包裹、TypeScript 友好 |
| **React 19** | UI 框架 | Concurrent features、Server Components 支持 |

## 项目结构约定

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router 页面
│   │   ├── layout.tsx          # Root layout (Server Component)
│   │   ├── workspace/          # 工作区路由组
│   │   │   ├── layout.tsx      # Workspace layout (带 sidebar)
│   │   │   ├── tasks/
│   │   │   │   ├── new/page.tsx
│   │   │   │   └── [id]/page.tsx
│   │   │   ├── projects/page.tsx
│   │   │   └── agents/page.tsx
│   │   └── chat/[id]/page.tsx
│   ├── components/
│   │   ├── ui/                 # shadcn/ui 基础组件 (Button, Input, Card...)
│   │   ├── ai-elements/        # AI 交互组件 (PromptInput, MessageList...)
│   │   ├── workspace/          # 工作区业务组件
│   │   ├── studio/             # Studio shell 组件 (Sidebar, Titlebar)
│   │   └── shared/             # 跨功能共享组件
│   ├── hooks/                  # 自定义 React hooks
│   ├── lib/                    # 工具函数、API client
│   ├── stores/                 # Zustand stores
│   └── types/                  # TypeScript 类型定义
```

## 编码规范

### 组件

```typescript
// 1. 客户端组件标记
"use client";

// 2. 导入顺序：React → Next.js → 第三方 → 内部组件 → 工具/类型
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Task } from "@/types";

// 3. Props 接口定义
interface TaskCardProps {
  task: Task;
  onSelect?: (id: string) => void;
}

// 4. 命名导出（非 default export，page.tsx 除外）
export function TaskCard({ task, onSelect }: TaskCardProps) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      {/* 内容 */}
    </div>
  );
}
```

### 页面组件

```typescript
// page.tsx 使用 default export
"use client";

export default function NewTaskPage() {
  return <div>...</div>;
}
```

### 样式规范

```typescript
// ✅ 使用 Tailwind 工具类
<div className="flex flex-col gap-4 p-6">

// ✅ 使用 cn() 合并条件类名
<button className={cn("px-4 py-2", isActive && "bg-primary text-primary-foreground")}>

// ✅ 使用 CSS 变量 (shadcn 约定)
<div className="bg-background text-foreground border-border">

// ❌ 避免内联样式（除非动态计算值或 Electron 特殊属性）
// ❌ 避免 CSS Modules
// ❌ 避免 styled-components
```

### 数据获取

```typescript
// ✅ TanStack Query 用于服务端数据
const { data, isLoading } = useQuery({
  queryKey: ["tasks", projectId],
  queryFn: () => fetchTasks(projectId),
});

// ✅ Zustand 用于客户端 UI 状态
const { sidebarOpen, toggleSidebar } = useSidebarStore();

// ❌ 避免 useEffect + fetch 模式
// ❌ 避免 prop drilling 超过 2 层
```

### AI 交互

```typescript
// LangGraph SDK 用于 AI 通信
import { Client } from "@langchain/langgraph-sdk";

const client = new Client({ apiUrl: "http://localhost:2024" });

// 流式响应处理
const stream = client.runs.stream(threadId, assistantId, {
  input: { messages: [...] },
  streamMode: "events",
});

for await (const event of stream) {
  // 处理流式事件
}
```

## shadcn/ui 组件清单

已安装的常用组件（`@/components/ui/` 目录下）：

| 组件 | 文件 | 用途 |
|------|------|------|
| `Button` | button.tsx | 按钮（variants: default, outline, ghost, destructive） |
| `Input` | input.tsx | 文本输入 |
| `Textarea` | textarea.tsx | 多行文本 |
| `Card` | card.tsx | 卡片容器 |
| `Dialog` | dialog.tsx | 模态对话框 |
| `DropdownMenu` | dropdown-menu.tsx | 下拉菜单 |
| `Sidebar` | sidebar.tsx | 侧边栏（SidebarProvider, Sidebar, SidebarContent...） |
| `Tooltip` | tooltip.tsx | 提示气泡 |
| `Tabs` | tabs.tsx | 标签页切换 |
| `Badge` | badge.tsx | 标签/徽章 |
| `Separator` | separator.tsx | 分隔线 |
| `ScrollArea` | scroll-area.tsx | 可滚动区域 |
| `Avatar` | avatar.tsx | 头像 |
| `Skeleton` | skeleton.tsx | 加载占位 |

## Electron Desktop 模式

当运行在 Electron 中时：
- `window.astra?.isElectron` 为 `true`
- 通过 `window.astra.ipc` 访问 IPC 方法
- Titlebar 区域需要 `WebkitAppRegion: "drag"` 支持窗口拖拽
- macOS 交通灯按钮占据左上角约 76px 宽度

## 设计 Token 映射

| Tailwind CSS 变量 | 用途 | 暗色主题值 |
|-------------------|------|-----------|
| `--background` | 页面背景 | `#09090B` |
| `--foreground` | 主文本 | `#FAFAFA` |
| `--card` | 卡片背景 | `#111113` |
| `--muted` | 低调背景 | `#1A1A1F` |
| `--muted-foreground` | 次要文本 | `#A1A1AA` |
| `--primary` | 主色调 | `#3B82F6` |
| `--border` | 边框 | `#27272A` |
| `--input` | 输入框背景 | `#1C1C22` |
| `--destructive` | 危险色 | `#EF4444` |
| `--sidebar-background` | 侧边栏背景 | `#0C0C0E` |
