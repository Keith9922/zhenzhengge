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
                "title": "阿波达斯商品页疑似仿冒",
                "brand_name": "阿迪达斯",
                "suspect_name": "阿波达斯",
                "platform": "淘宝",
                "source_url": "https://example.com/intake/1",
                "source_title": "阿波达斯商品页",
                "description": "smoke test",
                "note": "smoke",
                "monitoring_scope": ["taobao.com"],
                "tags": ["商标近似"],
            },
        )
        assert intake.status_code == 200, intake.text
        payload = intake.json()
        case_id = payload["case"]["case_id"]
        assert payload["case"]["evidence_count"] == 1
        assert payload["evidence_pack"]["case_id"] == case_id

        detail = client.get(f"/api/v1/cases/{case_id}")
        assert detail.status_code == 200, detail.text
        assert detail.json()["title"] == "阿波达斯商品页疑似仿冒"

        templates = client.get("/api/v1/document-templates")
        assert templates.status_code == 200, templates.text
        assert templates.json()["total"] >= 1

        runtime = client.get("/api/v1/runtime/modules")
        assert runtime.status_code == 200, runtime.text
        assert any(item["name"] == "hermes_orchestrator" for item in runtime.json())

    print("smoke test passed")


if __name__ == "__main__":
    main()
