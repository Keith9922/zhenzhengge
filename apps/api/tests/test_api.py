from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import Settings
from app.main import create_app

from fastapi.testclient import TestClient


def test_health():
    with TestClient(create_app()) as client:
        response = client.get("/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["service"] == "证证鸽 API"


def test_plugin_intake_creates_case_and_evidence():
    with TemporaryDirectory() as tmpdir:
        settings = Settings(database_url=f"sqlite:///{tmpdir}/zhenzhengge.db")
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
            assert payload["case"]["title"] == "阿波达斯商品页疑似仿冒"
            assert payload["case"]["brand_name"] == "阿波达斯商品页疑似仿冒"
            assert payload["case"]["platform"] == "browser-extension"
            assert payload["evidence_pack"]["source_title"] == "阿波达斯商品页疑似仿冒"
            assert payload["case"]["evidence_count"] == 1

            case_id = payload["case"]["case_id"]
            detail = client.get(f"/api/v1/cases/{case_id}")
            assert detail.status_code == 200
            detail_payload = detail.json()
            assert detail_payload["title"] == "阿波达斯商品页疑似仿冒"
            assert detail_payload["evidence_count"] == 1


def test_sqlite_persists_across_app_restart():
    with TemporaryDirectory() as tmpdir:
        db_url = f"sqlite:///{tmpdir}/persist.db"
        settings = Settings(database_url=db_url)
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
    with TestClient(create_app()) as client:
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
        settings = Settings(database_url=f"sqlite:///{tmpdir}/workflow.db")
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
            assert "法务审核前预览" in draft_payload["content"]

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
            assert exported.json()["item"]["status"] == "exported"
            assert exported.json()["file_path"].endswith(f"{draft_id}.md")
            export_file = Path(tmpdir) / exported.json()["file_path"]
            assert export_file.exists()


def test_monitoring_and_notification_routes():
    with TemporaryDirectory() as tmpdir:
        settings = Settings(database_url=f"sqlite:///{tmpdir}/ops.db")
        with TestClient(create_app(settings)) as client:
            monitoring = client.post(
                "/api/v1/monitor-tasks",
                json={
                    "name": "京东店铺巡检",
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
            assert "已执行" in run_once.json()["message"]

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
            assert "未实际发送" in test_result.json()["message"] or "已发送" in test_result.json()["message"]
