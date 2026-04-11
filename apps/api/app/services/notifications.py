from dataclasses import dataclass


@dataclass(slots=True)
class NotificationResult:
    channel: str
    status: str
    detail: str


class NotificationAdapter:
    def __init__(self) -> None:
        self._status = "stub"

    def health(self) -> dict[str, str]:
        return {
            "name": "notification_adapter",
            "status": self._status,
            "description": "钉钉 / 邮件通知预留位",
        }

    def send_dingtalk(self, subject: str, body: str) -> NotificationResult:
        return NotificationResult(
            channel="dingtalk",
            status="queued",
            detail=f"已排队发送钉钉通知：{subject}",
        )

    def send_email(self, subject: str, body: str) -> NotificationResult:
        return NotificationResult(
            channel="email",
            status="queued",
            detail=f"已排队发送邮件通知：{subject}",
        )

