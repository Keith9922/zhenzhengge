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
