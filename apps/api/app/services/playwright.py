from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

import httpx

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - import-time guard
    sync_playwright = None  # type: ignore[assignment]


@dataclass(slots=True)
class PageCaptureResult:
    source_url: str
    title: str
    html_path: str
    screenshot_path: str
    html_content: str
    page_text: str
    screenshot_bytes: bytes
    status: str
    detail: str


class PlaywrightWorker:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path.cwd()
        self.capture_dir = self.base_dir / "captures"
        self.capture_dir.mkdir(parents=True, exist_ok=True)

    def health(self) -> dict[str, str]:
        if sync_playwright is None:
            return {
                "name": "playwright_worker",
                "status": "degraded",
                "description": "playwright 未安装，当前只支持 http 回退抓取",
            }
        return {
            "name": "playwright_worker",
            "status": "ready",
            "description": "页面抓取与截图已接入，可执行真实页面采集",
        }

    def capture(self, url: str, title: str) -> PageCaptureResult:
        capture_slug = self._slugify(url)
        html_file = self.capture_dir / f"{capture_slug}.html"
        screenshot_file = self.capture_dir / f"{capture_slug}.png"

        if sync_playwright is None:
            return self._capture_via_http(url=url, title=title, html_file=html_file, screenshot_file=screenshot_file)

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1440, "height": 1600})
                page.goto(url, wait_until="domcontentloaded", timeout=20_000)
                html_content = page.content()
                page_text = page.locator("body").inner_text(timeout=5_000) if page.locator("body").count() else ""
                screenshot_bytes = page.screenshot(full_page=True, type="png")
                resolved_title = page.title().strip() or title
                browser.close()

            html_file.write_text(html_content, encoding="utf-8")
            screenshot_file.write_bytes(screenshot_bytes)
            return PageCaptureResult(
                source_url=url,
                title=resolved_title,
                html_path=html_file.relative_to(self.base_dir).as_posix(),
                screenshot_path=screenshot_file.relative_to(self.base_dir).as_posix(),
                html_content=html_content,
                page_text=page_text,
                screenshot_bytes=screenshot_bytes,
                status="captured",
                detail="playwright 抓取成功",
            )
        except Exception as exc:  # pragma: no cover - browser failure path
            return self._capture_via_http(
                url=url,
                title=title,
                html_file=html_file,
                screenshot_file=screenshot_file,
                fallback_error=exc,
            )

    def _capture_via_http(
        self,
        *,
        url: str,
        title: str,
        html_file: Path,
        screenshot_file: Path,
        fallback_error: Exception | None = None,
    ) -> PageCaptureResult:
        if self._looks_like_example_domain(url):
            html_content = (
                "<html><head><title>{title}</title></head>"
                "<body><main><h1>{title}</h1><p>演示抓取内容，来自离线示例域名。</p></main></body></html>"
            ).format(title=title)
            detail = "示例域名使用离线回退内容"
        else:
            try:
                response = httpx.get(url, timeout=15.0, follow_redirects=True)
                response.raise_for_status()
                html_content = response.text
                detail = "HTTP 回退抓取成功"
            except Exception as exc:  # pragma: no cover - network failure path
                html_content = (
                    "<html><head><title>{title}</title></head>"
                    "<body><main><h1>{title}</h1><p>抓取失败，已使用占位内容保底。</p></main></body></html>"
                ).format(title=title)
                detail = f"HTTP 回退抓取失败：{exc}"
                if fallback_error is not None:
                    detail = f"playwright 失败：{fallback_error}; {detail}"

        page_text = self._extract_text(html_content)
        html_file.write_text(html_content, encoding="utf-8")
        if not screenshot_file.exists():
            screenshot_file.write_bytes(b"")
        return PageCaptureResult(
            source_url=url,
            title=title,
            html_path=html_file.relative_to(self.base_dir).as_posix(),
            screenshot_path=screenshot_file.relative_to(self.base_dir).as_posix(),
            html_content=html_content,
            page_text=page_text,
            screenshot_bytes=b"",
            status="degraded",
            detail=detail,
        )

    @staticmethod
    def _slugify(url: str) -> str:
        return sha256(url.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _extract_text(html_content: str) -> str:
        text = re.sub(r"<script[\s\S]*?</script>", " ", html_content, flags=re.IGNORECASE)
        text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def _looks_like_example_domain(url: str) -> bool:
        return "example.com" in url or "example.org" in url or "example.net" in url
