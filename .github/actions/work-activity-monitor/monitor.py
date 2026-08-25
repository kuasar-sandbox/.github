#!/usr/bin/env python3
"""Publish alerts for actionable GitHub activity in a monitored repository."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from classifier import (
    Classification,
    classify,
    login,
    object_id,
    source_url,
    subject_from_payload,
    updated_at,
)
from github_api import GitHubAPI, TRACKER_MARKER_PREFIX, publish_alert
from signals import CATEGORY_ORDER, excerpt, markdown_link_text


def env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None or value == "":
        raise RuntimeError(f"required environment variable {name} is not set")
    return value


def read_payload(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("GitHub event payload must be a JSON object")
    return data


def make_fingerprint(
    repository: str,
    event_name: str,
    action: str,
    object_key: str,
    updated: str,
    categories: Sequence[str],
) -> str:
    raw = "\0".join((repository, event_name, action, object_key, updated, ",".join(categories)))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def render_alert(
    recipient: str,
    repository: str,
    event_name: str,
    action: str,
    actor: str,
    title: str,
    body: str,
    url: str,
    classification: Classification,
    fingerprint: str,
) -> str:
    categories = sorted(classification.categories, key=lambda item: CATEGORY_ORDER.get(item, 99))
    heading = " · ".join(categories)
    source_name = markdown_link_text(title.strip() or f"{event_name}.{action or 'event'}")
    source = f"[{source_name}]({url})" if url else f"`{source_name}`"
    detected = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    reasons = "\n".join(f"- {reason}" for reason in classification.reasons)
    quote = excerpt(body)
    quote_section = f"\n\n**New content**\n\n{quote}" if quote else ""
    return (
        f"@{recipient}\n\n"
        f"### {heading}\n"
        f"**Source:** {source}  \n"
        f"**Repository:** `{repository}`  \n"
        f"**Event:** `{event_name}.{action or 'event'}` by `@{actor}`  \n"
        f"**Detected:** {detected}\n\n"
        f"**Why this was surfaced**\n{reasons}"
        f"{quote_section}\n\n"
        f"<!-- kuasar-work-alert:{fingerprint} -->"
    )


def main() -> int:
    event_name = env("GITHUB_EVENT_NAME")
    repository = env("GITHUB_REPOSITORY")
    recipient = env("MONITOR_RECIPIENT")
    actor = os.environ.get("GITHUB_ACTOR", "unknown")
    payload = read_payload(env("GITHUB_EVENT_PATH"))

    sender = payload.get("sender")
    sender_login = login(sender) or actor
    sender_type = str(sender.get("type") if isinstance(sender, Mapping) else "")
    if sender_type.lower() == "bot" or sender_login.lower().endswith("[bot]"):
        print(f"Ignoring bot-authored event from {sender_login}")
        return 0

    subject = subject_from_payload(payload)
    title = str(subject.get("title") or "")
    if TRACKER_MARKER_PREFIX in str(subject.get("body") or "") or title.startswith("[Work monitor]"):
        print("Ignoring activity on the monitor tracker itself")
        return 0

    api = GitHubAPI(env("GITHUB_TOKEN"), os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    classification, subject, title, body = classify(event_name, payload, recipient, api, repository)
    if not classification.categories:
        print("No actionable review, decision, deadline, blocker, or follow-up detected")
        return 0

    action = str(payload.get("action") or "")
    categories = sorted(classification.categories, key=lambda item: CATEGORY_ORDER.get(item, 99))
    fingerprint = make_fingerprint(
        repository,
        event_name,
        action,
        object_id(payload, subject),
        updated_at(payload, subject),
        categories,
    )
    alert = render_alert(
        recipient,
        repository,
        event_name,
        action,
        sender_login,
        title,
        body,
        source_url(payload, subject),
        classification,
        fingerprint,
    )
    publish_alert(api, repository, recipient, alert, fingerprint)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"::error::{exc}")
        raise
