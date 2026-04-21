import base64
import hashlib
import hmac
import time
from email.message import EmailMessage
import smtplib
import urllib.parse

import httpx

from app.core.config import Settings
from app.core.storage import SQLiteStorage
from app.schemas.notification_channels import (
    NotificationChannelCreateRequest,
    NotificationChannelRecord,
)


class NotificationAdapter:
    def __init__(self, storage: SQLiteStorage, settings: Settings) -> None:
        self.storage = storage
        self.settings = settings

    def health(self) -> dict[str, str]:
        email_ready = bool(self.settings.smtp_host and self.settings.smtp_from_email)
        return {
            "name": "notification_adapter",
            "status": "ready" if email_ready else "degraded",
            "description": "通知渠道已接入；未配置 SMTP 时邮件发送会失败并记录日志。",
        }

    def list_channels(self, *, organization_id: str | None = None) -> list[NotificationChannelRecord]:
        return self.storage.list_notification_channels(organization_id=organization_id)

    def create_channel(
        self,
        payload: NotificationChannelCreateRequest,
        *,
        organization_id: str,
        owner_user_id: str,
    ) -> NotificationChannelRecord:
        return self.storage.create_notification_channel(
            payload,
            organization_id=organization_id,
            owner_user_id=owner_user_id,
        )

    def get_channel(self, channel_id: str, *, organization_id: str | None = None) -> NotificationChannelRecord | None:
        return self.storage.get_notification_channel(channel_id, organization_id=organization_id)

    def list_logs(self, *, organization_id: str | None = None, limit: int = 50) -> list[dict[str, str | None]]:
        rows = self.storage.list_notification_logs(organization_id=organization_id, limit=limit)
        return [
            {
                "log_id": row["log_id"],
                "channel_id": row["channel_id"],
                "task_id": row["task_id"],
                "case_id": row["case_id"],
                "event_type": row["event_type"],
                "subject": row["subject"],
                "status": row["status"],
                "detail": row["detail"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def send_dingtalk(self, target: str, subject: str, body: str) -> dict[str, str]:
        if not target.startswith("http"):
            return {"channel": "dingtalk", "status": "failed", "detail": f"未配置有效 webhook：{subject}"}

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": subject,
                "text": f"### {subject}\n\n{body}",
            },
        }
        url = self._with_dingtalk_signature(target)
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        return {"channel": "dingtalk", "status": "sent", "detail": f"已发送钉钉通知：{subject}"}

    def send_email(self, target: str, subject: str, body: str) -> dict[str, str]:
        if not (self.settings.smtp_host and self.settings.smtp_from_email):
            return {"channel": "email", "status": "failed", "detail": f"SMTP 未配置，发送失败：{subject}"}

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.settings.smtp_from_email
        message["To"] = target
        message.set_content(body)

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=10) as client:
            if self.settings.smtp_use_tls:
                client.starttls()
            if self.settings.smtp_username:
                client.login(self.settings.smtp_username, self.settings.smtp_password)
            client.send_message(message)
        return {"channel": "email", "status": "sent", "detail": f"已发送邮件通知：{subject}"}

    def test_channel(
        self,
        channel_id: str,
        *,
        organization_id: str,
        subject: str,
        body: str,
    ) -> dict[str, str]:
        channel = self.get_channel(channel_id, organization_id=organization_id)
        if channel is None:
            raise ValueError("通知渠道不存在")
        if not channel.enabled:
            result = {"channel": channel.channel_type.value, "status": "disabled", "detail": "通知渠道已停用"}
        elif channel.channel_type.value == "dingtalk":
            result = self.send_dingtalk(channel.target, subject, body)
        else:
            result = self.send_email(channel.target, subject, body)
        self.storage.create_notification_log(
            channel_id=channel.channel_id,
            event_type="manual_test",
            subject=subject,
            body=body,
            status=result["status"],
            detail=result["detail"],
            organization_id=organization_id,
        )
        return result

    def notify_enabled_channels(
        self,
        *,
        event_type: str,
        subject: str,
        body: str,
        organization_id: str,
        task_id: str | None = None,
        case_id: str | None = None,
    ) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        for channel in self.list_channels(organization_id=organization_id):
            if not channel.enabled:
                continue
            if channel.channel_type.value == "dingtalk":
                result = self.send_dingtalk(channel.target, subject, body)
            else:
                result = self.send_email(channel.target, subject, body)
            self.storage.create_notification_log(
                channel_id=channel.channel_id,
                task_id=task_id,
                case_id=case_id,
                event_type=event_type,
                subject=subject,
                body=body,
                status=result["status"],
                detail=result["detail"],
                organization_id=organization_id,
            )
            results.append(
                {
                    "channel_id": channel.channel_id,
                    "channel_type": channel.channel_type.value,
                    "status": result["status"],
                    "detail": result["detail"],
                }
            )
        return results

    def _with_dingtalk_signature(self, url: str) -> str:
        if "secret=" not in url:
            return url

        if "timestamp=" in url and "sign=" in url:
            return url

        base, secret = url.split("secret=", 1)
        secret = secret.strip()
        timestamp = str(round(time.time() * 1000))
        sign = hmac.new(secret.encode("utf-8"), f"{timestamp}\n{secret}".encode("utf-8"), hashlib.sha256).digest()
        encoded = urllib.parse.quote_plus(base64.b64encode(sign))
        connector = "&" if "?" in base else "?"
        return f"{base}{connector}timestamp={timestamp}&sign={encoded}"
