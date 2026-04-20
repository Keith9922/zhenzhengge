# 证证鸽浏览器插件

基于 Plasmo 的浏览器插件，用于证证鸽的前台一键取证入口。

## 功能

- 当前页面一键取证
- 采集 URL、标题、时间戳、页面正文、HTML 与整页/可视区截图
- 直接提交到后端 intake，自动创建案件与证据包
- 支持返回文书草稿编号并跳转工作台草稿详情

## 本地开发

```bash
pnpm install
pnpm dev
```

## 打包

```bash
pnpm build
pnpm pack
```

## 环境变量

复制 `.env.example` 为 `.env`，配置：

```bash
PLASMO_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
PLASMO_PUBLIC_WEB_BASE_URL=http://127.0.0.1:3006
PLASMO_PUBLIC_API_TOKEN=dev-operator-token
PLASMO_PUBLIC_ALLOW_SIMULATED_SUBMISSION=false
```

如果不配置 API 地址，且允许模拟提交，插件会退回到本地模拟提交模式。正式联调时建议显式关闭模拟提交，并配置 API Token。

## 默认提交接口

优先对接：

```bash
/api/v1/evidence/intake
```

请求体会优先包含：

- `requestId`
- `source`
- `url`
- `title`
- `capturedAt`
- `pageText`
- `html`
- `screenshotBase64`
- `captureWarnings`

## 提交结果

如果后端返回 `case.case_id`、`evidence_pack.evidence_pack_id` 和 `generated_draft.draft_id`，插件会直接展示它们。
如果配置了 `PLASMO_PUBLIC_WEB_BASE_URL`，会优先显示“打开草稿详情”按钮，跳转到：

```bash
/workspace/drafts/{draftId}
```
