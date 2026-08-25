"""Minimal GitHub REST client and rolling tracker issue management."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Iterable, Mapping

API_VERSION = "2022-11-28"
TRACKER_MARKER_PREFIX = "kuasar-work-monitor"
ALERT_MARKER_PREFIX = "kuasar-work-alert"


class GitHubAPI:
    def __init__(self, token: str, api_url: str) -> None:
        self.api_url = api_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "kuasar-work-activity-monitor/2.0",
        }

    def request(self, method: str, path: str, data: Mapping[str, Any] | None = None) -> Any:
        url = path if path.startswith("http") else f"{self.api_url}{path}"
        encoded = None
        headers = dict(self.headers)
        if data is not None:
            encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"

        last_error: Exception | None = None
        for attempt in range(3):
            request = urllib.request.Request(url, data=encoded, headers=headers, method=method)
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    raw = response.read()
                    return json.loads(raw.decode("utf-8")) if raw else None
            except urllib.error.HTTPError as exc:
                raw = exc.read().decode("utf-8", errors="replace")
                if exc.code in (429, 502, 503, 504) and attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    last_error = exc
                    continue
                raise RuntimeError(f"GitHub API {method} {url} failed: HTTP {exc.code}: {raw[:1000]}") from exc
            except urllib.error.URLError as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise RuntimeError(f"GitHub API {method} {url} failed: {exc}") from exc
        raise RuntimeError(f"GitHub API {method} {url} failed: {last_error}")

    def paginate(self, path: str) -> Iterable[Any]:
        separator = "&" if "?" in path else "?"
        page = 1
        while True:
            batch = self.request("GET", f"{path}{separator}per_page=100&page={page}")
            if not isinstance(batch, list):
                raise RuntimeError(f"expected list response while paging {path}")
            yield from batch
            if len(batch) < 100:
                return
            page += 1


def _login(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return str(value.get("login") or value.get("name") or "")
    return ""


def previous_participation(api: GitHubAPI, repository: str, number: int, recipient: str, is_pr: bool) -> bool:
    owner, repo = repository.split("/", 1)
    recipient = recipient.lower()
    for item in api.paginate(f"/repos/{owner}/{repo}/issues/{number}/comments"):
        if isinstance(item, Mapping) and _login(item.get("user")).lower() == recipient:
            return True
    if is_pr:
        for path in (
            f"/repos/{owner}/{repo}/pulls/{number}/reviews",
            f"/repos/{owner}/{repo}/pulls/{number}/comments",
        ):
            for item in api.paginate(path):
                if isinstance(item, Mapping) and _login(item.get("user")).lower() == recipient:
                    return True
    return False


def tracker_marker(recipient: str) -> str:
    return f"<!-- {TRACKER_MARKER_PREFIX}:{recipient.lower()} -->"


def find_tracker(api: GitHubAPI, repository: str, recipient: str) -> Mapping[str, Any] | None:
    owner, repo = repository.split("/", 1)
    marker = tracker_marker(recipient)
    path = f"/repos/{owner}/{repo}/issues?state=open&sort=created&direction=desc"
    for item in api.paginate(path):
        if not isinstance(item, Mapping) or "pull_request" in item:
            continue
        if marker in str(item.get("body") or ""):
            return item
    return None


def already_posted(api: GitHubAPI, repository: str, tracker: Mapping[str, Any], marker: str) -> bool:
    if marker in str(tracker.get("body") or ""):
        return True
    owner, repo = repository.split("/", 1)
    number = int(tracker["number"])
    for item in api.paginate(f"/repos/{owner}/{repo}/issues/{number}/comments"):
        if isinstance(item, Mapping) and marker in str(item.get("body") or ""):
            return True
    return False


def publish_alert(api: GitHubAPI, repository: str, recipient: str, alert: str, fingerprint: str) -> None:
    owner, repo = repository.split("/", 1)
    marker = f"<!-- {ALERT_MARKER_PREFIX}:{fingerprint} -->"
    tracker = find_tracker(api, repository, recipient)
    if tracker is not None and already_posted(api, repository, tracker, marker):
        print(f"Alert {fingerprint} was already posted; skipping duplicate")
        return

    if tracker is None:
        intro = (
            f"{tracker_marker(recipient)}\n"
            "This rolling issue is maintained by the Kuasar work-activity monitor. "
            "It records only high-confidence reviews, decisions, deadlines, blockers, "
            "and required follow-ups. Close this issue to start a fresh tracker on the next alert.\n\n"
            "---\n\n"
        )
        payload = {
            "title": f"[Work monitor] Actionable activity for @{recipient}",
            "body": intro + alert,
            "assignees": [recipient],
        }
        try:
            created = api.request("POST", f"/repos/{owner}/{repo}/issues", payload)
        except RuntimeError as exc:
            if "HTTP 422" not in str(exc):
                raise
            payload.pop("assignees", None)
            created = api.request("POST", f"/repos/{owner}/{repo}/issues", payload)
        print(f"Created tracker issue #{created.get('number')} with alert {fingerprint}")
        return

    number = int(tracker["number"])
    api.request("POST", f"/repos/{owner}/{repo}/issues/{number}/comments", {"body": alert})
    print(f"Posted alert {fingerprint} to tracker issue #{number}")
