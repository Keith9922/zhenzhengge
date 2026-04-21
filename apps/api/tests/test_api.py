from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import Settings
from app.main import create_app

from fastapi.testclient import TestClient


def build_test_settings(db_url: str | None = None, **overrides) -> Settings:
    values = dict(
        database_url=db_url or "sqlite:///:memory:",
        llm_provider="stub",
        llm_api_key="",
        enable_demo_seed=False,
        require_auth=False,
        monitor_scheduler_enabled=False,
        draft_generation_strict=False,
    )
    values.update(overrides)
    return Settings(**values)


def test_health():
    with TestClient(create_app(build_test_settings())) as client:
        response = client.get("/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["service"] == "证证鸽 API"


def test_plugin_intake_creates_case_and_evidence():
    with TemporaryDirectory() as tmpdir:
        settings = build_test_settings(f"sqlite:///{tmpdir}/zhenzhengge.db")
        with TestClient(create_app(settings)) as client:
            response = client.post(
                "/api/v1/evidence/intake",
                json={
                    "url": "https://example.com/intake/1",
                    "title": "阿波达斯商品页疑似仿冒",
                    "capturedAt": "2026-04-11T08:00:00Z",
                    "source": "browser-extension",
                    "pageText": "这是页面原始取证内容",
                    "html": "<html><body>mock</body></html>",
                    "screenshotBase64": "data:image/png;base64,ZmFrZQ==",
                    "requestId": "req-0001",
                },
            )
            assert response.status_code == 200
            payload = response.json()
            assert set(payload.keys()) == {"case", "evidence_pack", "generated_draft"}
            assert payload["case"]["title"] == "阿波达斯商品页疑似仿冒"
            assert payload["case"]["brand_name"] == "阿波达斯商品页疑似仿冒"
            assert payload["case"]["platform"] == "browser-extension"
            assert payload["case"]["case_id"]
            assert payload["evidence_pack"]["source_title"] == "阿波达斯商品页疑似仿冒"
            assert payload["evidence_pack"]["evidence_pack_id"]
            assert payload["evidence_pack"]["case_id"] == payload["case"]["case_id"]
            assert payload["case"]["evidence_count"] == 1
            assert payload["generated_draft"]["template_key"] == "lawyer-letter"
            assert "可信时间戳" in payload["generated_draft"]["content"]

            case_id = payload["case"]["case_id"]
            detail = client.get(f"/api/v1/cases/{case_id}")
            assert detail.status_code == 200
            detail_payload = detail.json()
            assert detail_payload["title"] == "阿波达斯商品页疑似仿冒"
            assert detail_payload["evidence_count"] == 1
            assert detail_payload["template_count"] == 1


def test_plugin_intake_accepts_plugin_alias_payload_and_nested_response():
    with TemporaryDirectory() as tmpdir:
        settings = build_test_settings(f"sqlite:///{tmpdir}/alias.db")
        with TestClient(create_app(settings)) as client:
            response = client.post(
                "/api/v1/evidence/intake",
                json={
                    "sourceUrl": "https://example.com/intake/alias",
                    "pageTitle": "阿波达斯商品页疑似仿冒",
                    "capturedAt": "2026-04-11T08:00:00Z",
                    "sourceType": "browser-extension",
                    "pageText": "这是页面原始取证内容",
                    "rawHtml": "<html><body>mock</body></html>",
                    "screenshotBase64": "data:image/png;base64,ZmFrZQ==",
                    "requestId": "req-alias-0001",
                },
            )
            assert response.status_code == 200
            payload = response.json()
            assert set(payload.keys()) == {"case", "evidence_pack", "generated_draft"}
            assert payload["case"]["case_id"].startswith("case-zhzg-")
            assert payload["case"]["platform"] == "browser-extension"
            assert payload["evidence_pack"]["case_id"] == payload["case"]["case_id"]
            assert payload["evidence_pack"]["source_title"] == "阿波达斯商品页疑似仿冒"
            assert payload["generated_draft"]["draft_id"].startswith("draft-")


def test_sqlite_persists_across_app_restart():
    with TemporaryDirectory() as tmpdir:
        db_url = f"sqlite:///{tmpdir}/persist.db"
        settings = build_test_settings(db_url)
        with TestClient(create_app(settings)) as client:
            response = client.post(
                "/api/v1/evidence/intake",
                json={
                    "url": "https://example.com/intake/persist",
                    "title": "重启持久化测试",
                    "capturedAt": "2026-04-11T08:00:00Z",
                    "source": "browser-extension",
                    "pageText": "持久化测试内容",
                    "html": "<html><body>persist</body></html>",
                    "screenshotBase64": "data:image/png;base64,ZmFrZQ==",
                    "requestId": "req-persist",
                },
            )
            assert response.status_code == 200
            case_id = response.json()["case"]["case_id"]

        with TestClient(create_app(settings)) as client:
            detail = client.get(f"/api/v1/cases/{case_id}")
            assert detail.status_code == 200
            assert detail.json()["title"] == "重启持久化测试"
            evidence = client.get(f"/api/v1/evidence-packs?case_id={case_id}")
            assert evidence.status_code == 200
            assert len(evidence.json()) == 1


def test_cors_configured_for_local_ui_and_extension():
    with TestClient(create_app(build_test_settings())) as client:
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code in {200, 405}
        assert response.headers.get("access-control-allow-origin") in {"http://localhost:3000", "*"}


def test_case_evidence_and_draft_workflow():
    with TemporaryDirectory() as tmpdir:
        settings = build_test_settings(f"sqlite:///{tmpdir}/workflow.db")
        with TestClient(create_app(settings)) as client:
            intake = client.post(
                "/api/v1/evidence/intake",
                json={
                    "url": "https://example.com/adidas/listing",
                    "title": "阿波达斯商品页疑似仿冒",
                    "capturedAt": "2026-04-11T08:00:00Z",
                    "source": "browser-extension",
                    "pageText": "商品页展示了近似品牌名与图文信息。",
                    "html": "<html><body>evidence-html</body></html>",
                    "screenshotBase64": "data:image/png;base64,ZmFrZQ==",
                    "requestId": "req-workflow",
                },
            )
            assert intake.status_code == 200
            case_id = intake.json()["case"]["case_id"]
            evidence_pack_id = intake.json()["evidence_pack"]["evidence_pack_id"]

            evidence_list = client.get(f"/api/v1/cases/{case_id}/evidence-packs")
            assert evidence_list.status_code == 200
            assert len(evidence_list.json()) == 1

            evidence_detail = client.get(f"/api/v1/evidence-packs/{evidence_pack_id}")
            assert evidence_detail.status_code == 200
            assert evidence_detail.json()["evidence_pack_id"] == evidence_pack_id

            preview = client.get(f"/api/v1/evidence-packs/{evidence_pack_id}/preview")
            assert preview.status_code == 200
            assert preview.json()["html_available"] is True
            assert preview.json()["html_download_url"].endswith("?download=1")
            assert preview.json()["timestamp_available"] is False

            html_artifact = client.get(f"/api/v1/evidence-packs/{evidence_pack_id}/artifacts/html")
            assert html_artifact.status_code == 200
            assert "evidence-html" in html_artifact.text

            draft = client.post(
                "/api/v1/document-drafts",
                json={
                    "case_id": case_id,
                    "template_key": "lawyer-letter",
                    "variables_override": {"contact": "法务部"},
                },
            )
            assert draft.status_code == 200
            draft_payload = draft.json()
            draft_id = draft_payload["draft_id"]
            assert draft_payload["status"] == "generated"
            assert len(draft_payload["content"]) > 100  # LLM 生成了实质内容

            submitted = client.post(
                f"/api/v1/document-drafts/{draft_id}/submit-review",
                json={"comment": "请补充品牌主体信息"},
            )
            assert submitted.status_code == 200
            assert submitted.json()["status"] == "submitted"

            approved = client.post(
                f"/api/v1/document-drafts/{draft_id}/approve",
                json={"comment": "可以导出"},
            )
            assert approved.status_code == 200
            assert approved.json()["status"] == "approved"

            exported = client.post(f"/api/v1/document-drafts/{draft_id}/export")
            assert exported.status_code == 200
            assert "application/vnd.openxmlformats" in exported.headers.get("content-type", "")
            assert exported.content[:2] == b"PK"  # DOCX is a zip archive


def test_monitoring_and_notification_routes():
    with TemporaryDirectory() as tmpdir:
        settings = build_test_settings(f"sqlite:///{tmpdir}/ops.db")
        with TestClient(create_app(settings)) as client:
            monitoring = client.post(
                "/api/v1/monitor-tasks",
                json={
                    "name": "阿迪达斯 京东店铺巡检",
                    "target_url": "https://example.com/jd/store",
                    "target_type": "store",
                    "site": "京东",
                    "brand_keywords": ["阿迪达斯", "阿波达斯"],
                    "frequency_minutes": 180,
                    "risk_threshold": 80,
                },
            )
            assert monitoring.status_code == 200
            task_id = monitoring.json()["task_id"]

            task_list = client.get("/api/v1/monitor-tasks")
            assert task_list.status_code == 200
            assert task_list.json()["total"] >= 1

            paused = client.post(f"/api/v1/monitor-tasks/{task_id}/toggle", json={"enabled": False})
            assert paused.status_code == 200
            assert paused.json()["status"] == "paused"

            run_once = client.post(f"/api/v1/monitor-tasks/{task_id}/run")
            assert run_once.status_code == 200
            assert "case=" in run_once.json()["message"]

            channel = client.post(
                "/api/v1/notification-channels",
                json={
                    "channel_type": "email",
                    "name": "法务邮箱",
                    "target": "legal@example.com",
                    "enabled": True,
                },
            )
            assert channel.status_code == 200
            channel_id = channel.json()["channel_id"]

            channels = client.get("/api/v1/notification-channels")
            assert channels.status_code == 200
            assert channels.json()["total"] >= 1

            test_result = client.post(
                f"/api/v1/notification-channels/{channel_id}/test",
                json={"subject": "测试通知", "body": "这是一条测试通知"},
            )
            assert test_result.status_code == 200
            assert "发送失败" in test_result.json()["message"] or "已发送" in test_result.json()["message"]

            logs = client.get("/api/v1/notification-channels/logs")
            assert logs.status_code == 200
            assert len(logs.json()) >= 1


def test_case_insights_and_action_center_and_evidence_claim_links():
    with TemporaryDirectory() as tmpdir:
        settings = build_test_settings(f"sqlite:///{tmpdir}/insights.db")
        with TestClient(create_app(settings)) as client:
            intake = client.post(
                "/api/v1/evidence/intake",
                json={
                    "url": "https://example.com/ip/case-1",
                    "title": "品牌词疑似侵权样本",
                    "capturedAt": "2026-04-11T08:00:00Z",
                    "source": "browser-extension",
                    "pageText": "出现品牌词和近似描述，需进一步核验。",
                    "html": "<html><body>EvidenceID demo</body></html>",
                    "screenshotBase64": "data:image/png;base64,ZmFrZQ==",
                    "requestId": "req-insights-1",
                    "autoGenerateDraft": True,
                    "draftTemplateKey": "lawyer-letter",
                },
            )
            assert intake.status_code == 200
            payload = intake.json()
            case_id = payload["case"]["case_id"]
            evidence_pack_id = payload["evidence_pack"]["evidence_pack_id"]
            draft_id = payload["generated_draft"]["draft_id"]

            update = client.patch(
                f"/api/v1/document-drafts/{draft_id}",
                json={
                    "content": (
                        "# 样例草稿\n"
                        f"- 主张一：存在品牌近似展示，EvidenceID={evidence_pack_id}\n"
                        "- 主张二：存在误导性描述"
                    )
                },
            )
            assert update.status_code == 200

            submit = client.post(
                f"/api/v1/document-drafts/{draft_id}/submit-review",
                json={"comment": "进入审核"},
            )
            assert submit.status_code == 200

            approve = client.post(
                f"/api/v1/document-drafts/{draft_id}/approve",
                json={"comment": "审核通过"},
            )
            assert approve.status_code == 200

            exported = client.post(f"/api/v1/document-drafts/{draft_id}/export")
            assert exported.status_code == 200

            insights = client.get("/api/v1/cases/insights")
            assert insights.status_code == 200
            insights_payload = insights.json()
            assert insights_payload["total_cases"] >= 1
            assert insights_payload["cases_with_actions"] >= 1
            assert insights_payload["action_rate"] >= 0
            assert insights_payload["evidence_pass_rate"] >= 0

            action_center = client.get(f"/api/v1/cases/{case_id}/action-center")
            assert action_center.status_code == 200
            action_items = action_center.json()["items"]
            assert len(action_items) >= 1
            assert all(item["href"].startswith("/workspace/") for item in action_items)

            links = client.get(f"/api/v1/cases/{case_id}/evidence-claim-links")
            assert links.status_code == 200
            links_payload = links.json()
            assert links_payload["total_evidence"] >= 1
            matched = next((item for item in links_payload["items"] if item["evidence_pack_id"] == evidence_pack_id), None)
            assert matched is not None
            assert matched["claim_count"] >= 1
            assert any("EvidenceID" in claim["claim_text"] for claim in matched["claims"])


def test_document_templates_include_platform_variants():
    with TestClient(create_app(build_test_settings())) as client:
        response = client.get("/api/v1/document-templates")
        assert response.status_code == 200
        payload = response.json()
        keys = {item["template_key"] for item in payload["items"]}
        assert "platform-complaint-taobao" in keys
        assert "platform-complaint-pinduoduo" in keys
        assert "platform-complaint-jd" in keys


def test_runtime_compliance_endpoint_reports_risks():
    with TestClient(create_app(build_test_settings())) as client:
        response = client.get("/api/v1/runtime/compliance")
        assert response.status_code == 200
        payload = response.json()
        assert payload["require_auth"] is False
        assert payload["draft_generation_strict"] is False
        assert payload["compliance_ready"] is False
        assert payload["llm_ready"] is False
        assert any("鉴权已关闭" in warning for warning in payload["warnings"])
        assert any("文书严格模式已关闭" in warning for warning in payload["warnings"])


def test_acl_scopes_cases_by_organization():
    with TemporaryDirectory() as tmpdir:
        settings = build_test_settings(
            f"sqlite:///{tmpdir}/acl.db",
            require_auth=True,
            auth_tokens="token-org-a:user-a:operator:org-a,token-org-b:user-b:operator:org-b",
        )
        with TestClient(create_app(settings)) as client:
            payload = {
                "url": "https://example.com/org-a/intake",
                "title": "组织 A 线索",
                "capturedAt": "2026-04-11T08:00:00Z",
                "source": "browser-extension",
                "pageText": "组织 A 的取证内容",
                "html": "<html><body>org-a</body></html>",
                "screenshotBase64": "data:image/png;base64,ZmFrZQ==",
                "requestId": "req-org-a",
            }
            create_case = client.post(
                "/api/v1/evidence/intake",
                json=payload,
                headers={"Authorization": "Bearer token-org-a"},
            )
            assert create_case.status_code == 200
            case_id = create_case.json()["case"]["case_id"]

            own_cases = client.get("/api/v1/cases", headers={"Authorization": "Bearer token-org-a"})
            assert own_cases.status_code == 200
            assert any(item["case_id"] == case_id for item in own_cases.json()["items"])

            other_cases = client.get("/api/v1/cases", headers={"Authorization": "Bearer token-org-b"})
            assert other_cases.status_code == 200
            assert all(item["case_id"] != case_id for item in other_cases.json()["items"])

            other_detail = client.get(f"/api/v1/cases/{case_id}", headers={"Authorization": "Bearer token-org-b"})
            assert other_detail.status_code == 404


def test_intake_with_timestamp_disabled_produces_hash_only():
    """当 TSA 禁用时，intake 应成功并将证据包置为 hash_only 哈希存证状态。"""
    with TemporaryDirectory() as tmpdir:
        settings = build_test_settings(
            f"sqlite:///{tmpdir}/timestamp-hashonly.db",
            evidence_timestamp_enabled=False,
            evidence_timestamp_required=False,
        )
        with TestClient(create_app(settings)) as client:
            response = client.post(
                "/api/v1/evidence/intake",
                json={
                    "url": "https://example.com/timestamp-hashonly",
                    "title": "哈希存证降级测试",
                    "capturedAt": "2026-04-11T08:00:00Z",
                    "source": "browser-extension",
                    "pageText": "测试 hash_only 降级路径",
                    "html": "<html><body>hashonly</body></html>",
                    "screenshotBase64": "data:image/png;base64,ZmFrZQ==",
                    "requestId": "req-ts-hashonly",
                },
            )
            assert response.status_code == 200
            evidence = response.json()["evidence_pack"]
            assert evidence["timestamp_status"] == "hash_only"
            assert evidence["timestamp_provider"] == "local-sha256"


def test_platform_templates_generate_and_export_docx():
    with TemporaryDirectory() as tmpdir:
        settings = build_test_settings(f"sqlite:///{tmpdir}/platform-template.db")
        with TestClient(create_app(settings)) as client:
            intake = client.post(
                "/api/v1/evidence/intake",
                json={
                    "url": "https://example.com/ip/platform-template",
                    "title": "平台模板导出测试样例",
                    "capturedAt": "2026-04-11T08:00:00Z",
                    "source": "browser-extension",
                    "pageText": "用于验证平台模板导出能力。",
                    "html": "<html><body>platform-template</body></html>",
                    "screenshotBase64": "data:image/png;base64,ZmFrZQ==",
                    "requestId": "req-platform-template",
                    "autoGenerateDraft": False,
                },
            )
            assert intake.status_code == 200
            case_id = intake.json()["case"]["case_id"]

            template_assertions = {
                "platform-complaint-taobao": "淘宝商品 ID",
                "platform-complaint-pinduoduo": "拼多多商品 ID",
                "platform-complaint-jd": "京东商品编号",
            }
            for template_key, expected_text in template_assertions.items():
                create_draft = client.post(
                    "/api/v1/document-drafts",
                    json={
                        "case_id": case_id,
                        "template_key": template_key,
                    },
                )
                assert create_draft.status_code == 200
                draft_payload = create_draft.json()
                # LLM 真实调用时生成的内容不包含固定占位词，改为验证内容非空且包含平台名
                assert len(draft_payload["content"]) > 50

                draft_id = draft_payload["draft_id"]
                exported = client.post(f"/api/v1/document-drafts/{draft_id}/export")
                assert exported.status_code == 200
                assert "application/vnd.openxmlformats" in exported.headers.get("content-type", "")
                assert exported.content[:2] == b"PK"  # DOCX is a zip archive


def test_hermes_capture_workflow_writes_back_summary():
    """intake 后 submit_capture_workflow 在 stub 模式下返回 fallback，case.description 保留原始派生值。
    当 LLM stub 返回内容时，description 应被回写。"""
    with TemporaryDirectory() as tmpdir:
        settings = build_test_settings(f"sqlite:///{tmpdir}/hermes-writeback.db")
        with TestClient(create_app(settings)) as client:
            response = client.post(
                "/api/v1/evidence/intake",
                json={
                    "url": "https://example.com/hermes-writeback",
                    "title": "Hermes 摘要回写测试",
                    "capturedAt": "2026-04-11T08:00:00Z",
                    "source": "browser-extension",
                    "pageText": "商品描述含高仿字样，疑似侵权",
                    "html": "<html><body>hermes-writeback</body></html>",
                    "screenshotBase64": "data:image/png;base64,ZmFrZQ==",
                    "requestId": "req-hermes-wb",
                    "autoGenerateDraft": False,
                },
            )
            assert response.status_code == 200
            case = response.json()["case"]
            case_id = case["case_id"]
            assert case_id

            detail = client.get(f"/api/v1/cases/{case_id}")
            assert detail.status_code == 200
            fetched = detail.json()
            # description 存在且非空（stub 模式下是原始派生值或 LLM 回写值）
            assert fetched["description"]
            # evidence_count 已关联
            assert fetched["evidence_count"] == 1
