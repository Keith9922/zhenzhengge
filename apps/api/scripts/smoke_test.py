__test__ = False

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.main import create_app


def main() -> None:
    with TestClient(create_app()) as client:
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

        detail = client.get(f"/api/v1/cases/{case_id}")
        assert detail.status_code == 200, detail.text
        assert detail.json()["title"] == "阿波达斯商品页疑似仿冒"

        case_packs = client.get(f"/api/v1/cases/{case_id}/evidence-packs")
        assert case_packs.status_code == 200, case_packs.text
        assert len(case_packs.json()) == 1

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
        assert exported.json()["file_path"].endswith(f"{draft_id}.md")

        monitor = client.post(
            "/api/v1/monitor-tasks",
            json={
                "name": "品牌官网巡检",
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

        runtime = client.get("/api/v1/runtime/modules")
        assert runtime.status_code == 200, runtime.text
        assert any(item["name"] == "hermes_orchestrator" for item in runtime.json())

    print("smoke test passed")


if __name__ == "__main__":
    main()
