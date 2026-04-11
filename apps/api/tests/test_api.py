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
                "title": "阿波达斯商品页疑似仿冒",
                "brand_name": "阿迪达斯",
                "suspect_name": "阿波达斯",
                "platform": "淘宝",
                "source_url": "https://example.com/intake/1",
                "source_title": "阿波达斯商品页",
                "description": "插件 intake 自动建案测试",
                "note": "manual smoke",
                "monitoring_scope": ["taobao.com"],
                "tags": ["商标近似"],
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["case"]["title"] == "阿波达斯商品页疑似仿冒"
        assert payload["case"]["brand_name"] == "阿迪达斯"
        assert payload["evidence_pack"]["source_title"] == "阿波达斯商品页"
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
