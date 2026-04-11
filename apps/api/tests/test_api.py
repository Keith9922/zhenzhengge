from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
    with TestClient(create_app()) as client:
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
