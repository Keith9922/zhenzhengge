# 证证鸽接口清单

> 版本：`v0.1`  
> 目标：定义第一阶段前后端联调所需的核心 API，后续实现以此为基线迭代。

## 1. 设计原则

1. 所有接口统一经由业务后端暴露，不直接让前端调用 Hermes。
2. 所有写操作都要求带用户上下文，并受角色权限控制。
3. 所有“生成文书”“触发工作流”类动作都返回任务状态或结果引用，而不是直接暴露底层执行细节。

## 2. 基础接口

### `GET /health`

用途：健康检查

返回示例：

```json
{
  "status": "ok",
  "service": "zhenzhengge-api"
}
```

### `GET /meta/app`

用途：前端获取站点基础信息

返回字段：

- `name`
- `version`
- `env`
- `docsUrl`
- `repoUrl`

## 3. 认证与用户

### `POST /auth/login`

用途：登录

### `GET /auth/me`

用途：获取当前用户与角色信息

返回字段：

- `id`
- `name`
- `email`
- `roles`
- `organizationId`

## 4. 案件与证据

### `GET /cases`

用途：案件列表

查询参数：

- `status`
- `riskLevel`
- `site`
- `keyword`
- `page`
- `pageSize`

### `POST /cases`

用途：手动创建案件

请求字段：

- `title`
- `brandAssetId`
- `sourceType`
- `sourceUrl`
- `notes`

### `GET /cases/{caseId}`

用途：案件详情

### `POST /cases/{caseId}/analyze`

用途：触发风险分析

### `GET /cases/{caseId}/evidence-packs`

用途：查看案件下证据包列表

### `POST /evidence-packs`

用途：创建证据包

请求字段：

- `sourceUrl`
- `pageTitle`
- `capturedAt`
- `notes`
- `rawHtml`
- `textContent`
- `imageUrls`

### `GET /evidence-packs/{evidencePackId}`

用途：证据包详情

## 5. 插件取证接口

### `POST /capture/submit`

用途：插件提交当前页面取证请求

请求字段：

- `url`
- `title`
- `capturedAt`
- `notes`
- `pageText`
- `html`
- `screenshotBase64`

返回字段：

- `caseId`
- `evidencePackId`
- `status`

## 6. 模板与文书

### `GET /templates`

用途：获取模板列表

查询参数：

- `type`
- `enabled`

### `GET /templates/{templateId}`

用途：查看模板详情

### `POST /drafts/generate`

用途：生成文书初稿

请求字段：

- `caseId`
- `templateId`
- `variablesOverride`

返回字段：

- `draftId`
- `status`
- `downloadUrl`

### `GET /drafts/{draftId}`

用途：获取文书草稿详情

### `POST /drafts/{draftId}/submit-review`

用途：提交审核

### `POST /drafts/{draftId}/export`

用途：导出文书正式版本

## 7. 审核接口

### `GET /reviews`

用途：审核任务列表

### `POST /reviews/{reviewId}/approve`

用途：通过审核

### `POST /reviews/{reviewId}/reject`

用途：驳回审核

请求字段：

- `comment`

## 8. 监控任务

### `GET /monitor-tasks`

用途：任务列表

### `POST /monitor-tasks`

用途：创建监控任务

请求字段：

- `targetType`
- `targetUrl`
- `brandKeywords`
- `site`
- `frequency`
- `riskThreshold`

### `POST /monitor-tasks/{taskId}/toggle`

用途：启停监控任务

### `GET /monitor-tasks/{taskId}`

用途：查看任务详情

## 9. 通知配置

### `GET /notification-channels`

用途：获取通知渠道配置

### `POST /notification-channels/dingtalk`

用途：保存钉钉通知配置

### `POST /notification-channels/email`

用途：保存邮箱通知配置

### `POST /notification-channels/test`

用途：测试通知

## 10. Agent 工作流接口

### `POST /workflows/capture`

用途：触发主动取证工作流

### `POST /workflows/monitor`

用途：触发自动监测工作流

### `POST /workflows/generate-draft`

用途：触发文书生成工作流

### `GET /workflows/{workflowId}`

用途：查询工作流状态

## 11. 联调优先级

第一阶段最先打通的接口：

1. `GET /health`
2. `POST /capture/submit`
3. `GET /cases`
4. `GET /cases/{caseId}`
5. `GET /evidence-packs/{evidencePackId}`
6. `GET /templates`
7. `POST /drafts/generate`
8. `POST /notification-channels/test`

## 12. 后续约束

- 接口字段命名以英文为主，前端展示文案中文化
- 所有附件类返回建议走 `fileUrl` 或 `downloadUrl`
- 后续如果接入异步任务系统，生成类接口应优先返回任务 ID
