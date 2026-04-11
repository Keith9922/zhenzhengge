import hashlib
import hmac
import time
from email.message import EmailMessage
import smtplib

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
            "description": "通知渠道已接入，可进行配置和测试；未配置 SMTP 时邮件发送会降级。",
        }

    def list_channels(self) -> list[NotificationChannelRecord]:
        return self.storage.list_notification_channels()

    def create_channel(self, payload: NotificationChannelCreateRequest) -> NotificationChannelRecord:
        return self.storage.create_notification_channel(payload)

    def get_channel(self, channel_id: str) -> NotificationChannelRecord | None:
        return self.storage.get_notification_channel(channel_id)

    def send_dingtalk(self, target: str, subject: str, body: str) -> dict[str, str]:
        if not target.startswith("http"):
            return {"channel": "dingtalk", "status": "dry-run", "detail": f"未配置有效 webhook：{subject}"}

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
            return {"channel": "email", "status": "dry-run", "detail": f"SMTP 未配置，未实际发送：{subject}"}

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

    def test_channel(self, channel_id: str, *, subject: str, body: str) -> dict[str, str]:
        channel = self.get_channel(channel_id)
        if channel is None:
            raise ValueError("通知渠道不存在")
        if not channel.enabled:
            return {"channel": channel.channel_type.value, "status": "disabled", "detail": "通知渠道已停用"}
        if channel.channel_type.value == "dingtalk":
            return self.send_dingtalk(channel.target, subject, body)
        return self.send_email(channel.target, subject, body)

    def _with_dingtalk_signature(self, url: str) -> str:
        if "secret=" not in url:
            return url

        if "timestamp=" in url and "sign=" in url:
            return url

        base, secret = url.split("secret=", 1)
        secret = secret.strip()
        timestamp = str(round(time.time() * 1000))
        sign = hmac.new(secret.encode("utf-8"), f"{timestamp}\n{secret}".encode("utf-8"), hashlib.sha256).digest()
        import base64
        import urllib.parse

        encoded = urllib.parse.quote_plus(base64.b64encode(sign))
        connector = "&" if "?" in base else "?"
        return f"{base}{connector}timestamp={timestamp}&sign={encoded}"
