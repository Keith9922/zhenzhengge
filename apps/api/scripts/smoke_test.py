__test__ = False

from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def main() -> None:
    with TemporaryDirectory() as tmpdir:
        settings = Settings(
            database_url=f"sqlite:///{tmpdir}/smoke.db",
            llm_provider="stub",
            llm_api_key="",
            enable_demo_seed=False,
            require_auth=False,
            monitor_scheduler_enabled=False,
            draft_generation_strict=False,
        )
        with TestClient(create_app(settings)) as client:
            health = client.get("/health")
            assert health.status_code == 200, health.text
            assert health.json()["status"] == "ok"

            intake = client.post(
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
            assert intake.status_code == 200, intake.text
            payload = intake.json()
            case_id = payload["case"]["case_id"]
            assert payload["case"]["evidence_count"] == 1
            assert payload["evidence_pack"]["case_id"] == case_id
            assert payload["case"]["brand_name"] == "阿波达斯商品页疑似仿冒"
            assert payload["case"]["platform"] == "browser-extension"
            intake_draft_id = payload["generated_draft"]["draft_id"]

            detail = client.get(f"/api/v1/cases/{case_id}")
            assert detail.status_code == 200, detail.text
            assert detail.json()["title"] == "阿波达斯商品页疑似仿冒"

            case_packs = client.get(f"/api/v1/cases/{case_id}/evidence-packs")
            assert case_packs.status_code == 200, case_packs.text
            assert len(case_packs.json()) == 1
            evidence_pack_id = case_packs.json()[0]["evidence_pack_id"]

            preview = client.get(f"/api/v1/evidence-packs/{evidence_pack_id}/preview")
            assert preview.status_code == 200, preview.text
            assert preview.json()["html_available"] is True

            templates = client.get("/api/v1/document-templates")
            assert templates.status_code == 200, templates.text
            assert templates.json()["total"] >= 1

            draft = client.post(
                "/api/v1/document-drafts",
                json={
                    "case_id": case_id,
                    "template_key": "lawyer-letter",
                    "variables_override": {"contact": "法务部"},
                },
            )
            assert draft.status_code == 200, draft.text
            draft_id = draft.json()["draft_id"]

            exported = client.post(f"/api/v1/document-drafts/{draft_id}/export")
            assert exported.status_code == 200, exported.text
            assert exported.json()["file_path"].endswith(f"{draft_id}.docx")

            update = client.patch(
                f"/api/v1/document-drafts/{intake_draft_id}",
                json={
                    "content": (
                        "# 自动化核验草稿\n"
                        f"- 主张：页面存在品牌近似展示，EvidenceID={evidence_pack_id}\n"
                        "- 处理建议：先人工复核后再发起动作。"
                    )
                },
            )
            assert update.status_code == 200, update.text

            insights = client.get("/api/v1/cases/insights")
            assert insights.status_code == 200, insights.text
            assert insights.json()["total_cases"] >= 1

            action_center = client.get(f"/api/v1/cases/{case_id}/action-center")
            assert action_center.status_code == 200, action_center.text
            assert len(action_center.json()["items"]) >= 1

            claim_links = client.get(f"/api/v1/cases/{case_id}/evidence-claim-links")
            assert claim_links.status_code == 200, claim_links.text
            assert claim_links.json()["total_evidence"] >= 1
            assert claim_links.json()["total_claims"] >= 1

            runtime_compliance = client.get("/api/v1/runtime/compliance")
            assert runtime_compliance.status_code == 200, runtime_compliance.text
            assert "compliance_ready" in runtime_compliance.json()

            monitor = client.post(
                "/api/v1/monitor-tasks",
                json={
                    "name": "证证鸽 品牌官网巡检",
                    "target_url": "https://example.com/brand",
                    "target_type": "page",
                    "site": "品牌官网",
                    "brand_keywords": ["证证鸽"],
                    "frequency_minutes": 120,
                    "risk_threshold": 75,
                },
            )
            assert monitor.status_code == 200, monitor.text
            monitor_id = monitor.json()["task_id"]

            monitor_run = client.post(f"/api/v1/monitor-tasks/{monitor_id}/run")
            assert monitor_run.status_code == 200, monitor_run.text

            channel = client.post(
                "/api/v1/notification-channels",
                json={
                    "channel_type": "email",
                    "name": "法务接收",
                    "target": "legal@example.com",
                    "enabled": True,
                },
            )
            assert channel.status_code == 200, channel.text
            channel_id = channel.json()["channel_id"]

            channel_test = client.post(
                f"/api/v1/notification-channels/{channel_id}/test",
                json={"subject": "测试通知", "body": "这是一条测试通知"},
            )
            assert channel_test.status_code == 200, channel_test.text

            logs = client.get("/api/v1/notification-channels/logs")
            assert logs.status_code == 200, logs.text
            assert len(logs.json()) >= 1

            runtime = client.get("/api/v1/runtime/modules")
            assert runtime.status_code == 200, runtime.text
            assert any(item["name"] == "hermes_orchestrator" for item in runtime.json())

    print("smoke test passed")


if __name__ == "__main__":
    main()
