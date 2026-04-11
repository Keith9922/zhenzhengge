from dataclasses import dataclass


@dataclass(slots=True)
class PageCaptureResult:
    source_url: str
    title: str
    html_path: str
    screenshot_path: str


class PlaywrightWorker:
    def __init__(self) -> None:
        self._status = "stub"

    def health(self) -> dict[str, str]:
        return {
            "name": "playwright_worker",
            "status": self._status,
            "description": "页面抓取与截图预留位",
        }

    def capture(self, url: str, title: str) -> PageCaptureResult:
        safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_")
        return PageCaptureResult(
            source_url=url,
            title=title,
            html_path=f"captures/{safe_name}.html",
            screenshot_path=f"captures/{safe_name}.png",
        )

