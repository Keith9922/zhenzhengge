# 证证鸽浏览器插件

基于 Plasmo 的浏览器插件，用于证证鸽的前台一键取证入口。

## 功能

- 当前页面一键取证
- 采集 URL、标题、时间戳、页面正文和可视区截图
- 模拟提交到后端
- 预留后续截图、DOM 抽取、证据上传能力

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
PLASMO_PUBLIC_ALLOW_SIMULATED_SUBMISSION=false
```

如果不配置 API 地址，且允许模拟提交，插件会退回到本地模拟提交模式。正式联调时建议显式关闭模拟提交。

## 默认提交接口

优先对接：

```bash
/api/v1/evidence/intake
```

请求体会优先包含：

- `requestId`
- `sourceType`
- `sourceUrl`
- `pageTitle`
- `capturedAt`
- `notes`
- `pageText`
- `rawHtml`
- `screenshotBase64`
- `imageUrls`
- `captureWarnings`

## 提交结果

如果后端返回 `case.case_id` 和 `evidence_pack.evidence_pack_id`，插件会直接展示它们。
如果配置了 `PLASMO_PUBLIC_WEB_BASE_URL`，还会显示“打开案件详情”按钮，跳转到：

```bash
/workspace/cases/{caseId}
```
