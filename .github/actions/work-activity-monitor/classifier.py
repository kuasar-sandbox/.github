"""Event normalization and high-confidence activity classification."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from github_api import GitHubAPI, previous_participation
from signals import (
    BLOCKER_LABEL_RE,
    BLOCKER_RE,
    BY_DATE_RE,
    DATE_LIKE_RE,
    DEADLINE_LABEL_RE,
    DEADLINE_WORD_RE,
    DECISION_LABEL_RE,
    DECISION_RE,
    DIRECTIVE_RE,
    FOLLOWUP_LABEL_RE,
    REVIEW_LABEL_RE,
    REVIEW_TEXT_RE,
    STRONG_FOLLOWUP_RE,
    is_design_thread,
    strip_inert_markdown,
    text_mentions,
)


def login(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return str(value.get("login") or value.get("name") or "")
    return ""


def label_name(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return str(value.get("name") or "")
    return ""


def labels_of(subject: Mapping[str, Any] | None) -> list[str]:
    if not subject:
        return []
    labels = subject.get("labels") or []
    if not isinstance(labels, Sequence) or isinstance(labels, (str, bytes)):
        return []
    return [name for item in labels if (name := label_name(item))]


def assignees_of(subject: Mapping[str, Any] | None) -> set[str]:
    if not subject:
        return set()
    result = {login(item).lower() for item in (subject.get("assignees") or []) if login(item)}
    if single := login(subject.get("assignee")):
        result.add(single.lower())
    return result


def subject_from_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in ("pull_request", "issue", "discussion", "milestone"):
        value = payload.get(key)
        if isinstance(value, Mapping):
            return value
    return {}


def event_text(payload: Mapping[str, Any], subject: Mapping[str, Any]) -> tuple[str, str]:
    body = ""
    for candidate in (payload.get("comment"), payload.get("review"), subject):
        if isinstance(candidate, Mapping):
            possible = candidate.get("body") or candidate.get("description")
            if isinstance(possible, str) and possible.strip():
                body = possible
                break
    return str(subject.get("title") or ""), body


def new_text_for_event(
    event_name: str,
    action: str,
    payload: Mapping[str, Any],
    title: str,
    body: str,
) -> tuple[str, str, str]:
    """Return new text eligible for classification and a body safe to quote.

    Metadata-only events include the subject's current body in their payload, but
    that body is not new. Reclassifying it on close, assignment, label, or
    milestone changes creates stale duplicate blocker/follow-up alerts.
    """
    if event_name in ("issue_comment", "pull_request_review_comment", "discussion_comment"):
        if action in ("created", "edited"):
            return "", body, body
        return "", "", ""

    if event_name == "pull_request_review":
        if action in ("submitted", "edited"):
            return "", body, body
        return "", "", ""

    if event_name not in ("issues", "pull_request", "pull_request_target", "discussion", "milestone"):
        return "", "", ""

    if action in ("opened", "created"):
        return title, body, body

    if action != "edited":
        return "", "", ""

    changes = payload.get("changes")
    if not isinstance(changes, Mapping):
        return "", "", ""
    title_changed = "title" in changes
    body_key = "description" if event_name == "milestone" else "body"
    body_changed = body_key in changes
    return (
        title if title_changed else "",
        body if body_changed else "",
        body if body_changed else "",
    )


def source_url(payload: Mapping[str, Any], subject: Mapping[str, Any]) -> str:
    for candidate in (payload.get("comment"), payload.get("review"), subject):
        if isinstance(candidate, Mapping):
            url = candidate.get("html_url") or candidate.get("url")
            if isinstance(url, str) and url:
                return url
    return ""


def object_id(payload: Mapping[str, Any], subject: Mapping[str, Any]) -> str:
    for candidate in (payload.get("comment"), payload.get("review"), subject):
        if isinstance(candidate, Mapping):
            value = candidate.get("node_id") or candidate.get("id") or candidate.get("number")
            if value is not None:
                return str(value)
    return "unknown"


def updated_at(payload: Mapping[str, Any], subject: Mapping[str, Any]) -> str:
    for candidate in (payload.get("comment"), payload.get("review"), subject):
        if isinstance(candidate, Mapping):
            value = candidate.get("updated_at") or candidate.get("submitted_at") or candidate.get("created_at")
            if value:
                return str(value)
    return ""


def review_state(payload: Mapping[str, Any]) -> str:
    review = payload.get("review")
    return str(review.get("state") or "").lower() if isinstance(review, Mapping) else ""


def requested_reviewer(payload: Mapping[str, Any]) -> str:
    return login(payload.get("requested_reviewer"))


def requested_team(payload: Mapping[str, Any]) -> str:
    team = payload.get("requested_team")
    return str(team.get("slug") or team.get("name") or "") if isinstance(team, Mapping) else ""


def author_of(subject: Mapping[str, Any]) -> str:
    return login(subject.get("user") or subject.get("author"))


def thread_number(subject: Mapping[str, Any]) -> int | None:
    value = subject.get("number")
    return int(value) if isinstance(value, int) else None


def due_on(payload: Mapping[str, Any], subject: Mapping[str, Any]) -> str:
    milestone = payload.get("milestone")
    if isinstance(milestone, Mapping) and milestone.get("due_on"):
        return str(milestone["due_on"])
    milestone = subject.get("milestone")
    if isinstance(milestone, Mapping) and milestone.get("due_on"):
        return str(milestone["due_on"])
    return ""


@dataclass
class Classification:
    categories: set[str] = field(default_factory=set)
    reasons: list[str] = field(default_factory=list)
    potential_text_signal: bool = False
    direct_relevance: bool = False
    design_thread: bool = False

    def add(self, category: str, reason: str) -> None:
        self.categories.add(category)
        if reason not in self.reasons:
            self.reasons.append(reason)


def classify(
    event_name: str,
    payload: Mapping[str, Any],
    recipient: str,
    api: GitHubAPI | None = None,
    repository: str | None = None,
) -> tuple[Classification, Mapping[str, Any], str, str]:
    action = str(payload.get("action") or "")
    subject = subject_from_payload(payload)
    title, body = event_text(payload, subject)
    signal_title, signal_body, alert_body = new_text_for_event(event_name, action, payload, title, body)
    labels = labels_of(subject)
    clean_body = strip_inert_markdown(signal_body)
    clean_text = f"{signal_title}\n{clean_body}".strip()
    subject_body = str(subject.get("body") or subject.get("description") or "")
    relationship_text = strip_inert_markdown(f"{title}\n{subject_body}")
    recipient_lower = recipient.lower()

    result = Classification(design_thread=is_design_thread(title, labels))
    author = author_of(subject).lower()
    assignees = assignees_of(subject)
    mention = text_mentions(clean_text, recipient)
    thread_mention = text_mentions(relationship_text, recipient)
    assigned_now = action == "assigned" and login(payload.get("assignee")).lower() == recipient_lower
    unassigned_now = action == "unassigned" and login(payload.get("assignee")).lower() == recipient_lower
    reviewer_now = action == "review_requested" and requested_reviewer(payload).lower() == recipient_lower
    subject_requested = {
        login(item).lower() for item in (subject.get("requested_reviewers") or []) if login(item)
    }
    result.direct_relevance = any((
        author == recipient_lower,
        recipient_lower in assignees,
        recipient_lower in subject_requested,
        mention,
        thread_mention,
        assigned_now,
        unassigned_now,
        reviewer_now,
    ))

    number = thread_number(subject)
    is_pr = bool(payload.get("pull_request") or subject.get("pull_request"))
    participation_checked = False

    def relationship_relevant() -> bool:
        nonlocal participation_checked
        if result.direct_relevance or result.design_thread:
            return True
        if participation_checked:
            return False
        participation_checked = True
        if (
            api is None
            or not repository
            or number is None
            or event_name in ("discussion", "discussion_comment", "milestone")
        ):
            return False
        try:
            result.direct_relevance = previous_participation(api, repository, number, recipient, is_pr)
        except Exception as exc:
            print(f"::warning::Could not inspect prior participation: {exc}")
        return result.direct_relevance

    if event_name == "workflow_dispatch":
        result.add("TEST", "Manual monitor test was requested")
        return result, subject, title, alert_body
    if assigned_now:
        result.add("FOLLOW-UP", f"Issue or pull request assigned to @{recipient}")
    if unassigned_now:
        result.add("DECISION", f"Issue or pull request unassigned from @{recipient}")
    if reviewer_now:
        result.add("REVIEW REQUIRED", f"Review explicitly requested from @{recipient}")
    if action == "review_request_removed" and requested_reviewer(payload).lower() == recipient_lower:
        result.add("DECISION", f"Review request for @{recipient} was removed")
    if (team := requested_team(payload)) and action == "review_requested" and relationship_relevant():
        result.add("REVIEW REQUIRED", f"Review requested from team `{team}`")

    state = review_state(payload)
    if event_name == "pull_request_review" and action == "submitted":
        if state == "changes_requested" and relationship_relevant():
            result.add("CHANGES REQUESTED", "A submitted review requested changes")
            result.add("FOLLOW-UP", "Review feedback requires a response or code change")
        elif state == "approved" and relationship_relevant():
            result.add("DECISION", "A submitted review approved the pull request")
        elif state == "commented" and relationship_relevant():
            result.add("REVIEW REQUIRED", "A review was submitted with comments")
    elif event_name == "pull_request_review" and action == "dismissed" and relationship_relevant():
        result.add("DECISION", "A previously submitted review was dismissed")

    if event_name in ("pull_request", "pull_request_target"):
        if action == "closed" and bool(subject.get("merged")) and relationship_relevant():
            result.add("DECISION", "Pull request was merged")
        elif action == "closed" and relationship_relevant():
            result.add("DECISION", "Pull request was closed without merging")
        elif action == "ready_for_review" and relationship_relevant():
            result.add("REVIEW REQUIRED", "Draft pull request was marked ready for review")
        elif action == "converted_to_draft" and relationship_relevant():
            result.add("DECISION", "Pull request was converted back to draft")
        elif action == "reopened" and relationship_relevant():
            result.add("FOLLOW-UP", "Pull request was reopened")

    if event_name == "issues" and action == "closed" and relationship_relevant():
        result.add("DECISION", f"Issue was closed ({subject.get('state_reason') or 'completed'})")
    elif event_name == "issues" and action == "reopened" and relationship_relevant():
        result.add("FOLLOW-UP", "Issue was reopened")

    if event_name == "discussion" and action == "answered" and (
        result.direct_relevance or result.design_thread
    ):
        result.add("DECISION", "A discussion answer was selected")
    elif event_name == "discussion" and action == "unanswered" and (
        result.direct_relevance or result.design_thread
    ):
        result.add("FOLLOW-UP", "The selected discussion answer was removed")

    label = label_name(payload.get("label"))
    if label:
        if BLOCKER_LABEL_RE.search(label):
            if action in ("labeled", "created", "edited"):
                result.add("BLOCKER", f"Blocker-like label `{label}` was added")
            elif action == "unlabeled":
                result.add("DECISION", f"Blocker-like label `{label}` was removed")
        if DECISION_LABEL_RE.search(label):
            result.add("DECISION", f"Decision-like label `{label}` changed")
        if DEADLINE_LABEL_RE.search(label):
            result.add("DEADLINE", f"Deadline-like label `{label}` changed")
        if REVIEW_LABEL_RE.search(label):
            result.add("REVIEW REQUIRED", f"Review-like label `{label}` changed")
        if FOLLOWUP_LABEL_RE.search(label):
            result.add("FOLLOW-UP", f"Follow-up-like label `{label}` changed")

    if due := due_on(payload, subject):
        milestone_event = event_name == "milestone"
        relevant_subject_event = action in ("milestoned", "edited", "created", "opened") and relationship_relevant()
        if milestone_event or relevant_subject_event:
            result.add("DEADLINE", f"Milestone due date is {due}")
    if (
        action == "demilestoned"
        and isinstance(payload.get("milestone"), Mapping)
        and relationship_relevant()
    ):
        removed_title = str(payload["milestone"].get("title") or "milestone")
        result.add("DECISION", f"Milestone `{removed_title}` was removed")

    blocker_signal = bool(BLOCKER_RE.search(clean_text))
    decision_signal = bool(DECISION_RE.search(clean_text))
    deadline_signal = bool(DEADLINE_WORD_RE.search(clean_text) or BY_DATE_RE.search(clean_text))
    if deadline_signal and not DEADLINE_WORD_RE.search(clean_text):
        deadline_signal = bool(DATE_LIKE_RE.search(clean_text))
    review_signal = bool(REVIEW_TEXT_RE.search(clean_text))
    followup_signal = bool(STRONG_FOLLOWUP_RE.search(clean_text))
    directive_signal = bool(DIRECTIVE_RE.search(clean_body))
    result.potential_text_signal = any((
        blocker_signal,
        decision_signal,
        deadline_signal,
        review_signal,
        followup_signal,
        directive_signal,
    ))

    relevant_for_text = result.direct_relevance or result.design_thread
    if not relevant_for_text and result.potential_text_signal:
        relevant_for_text = relationship_relevant()

    if relevant_for_text:
        if blocker_signal:
            result.add("BLOCKER", "New text contains an explicit blocker signal")
        if decision_signal:
            result.add("DECISION", "New text contains an explicit decision or consensus signal")
        if deadline_signal:
            result.add("DEADLINE", "New text contains an explicit deadline signal")
        if review_signal:
            result.add("REVIEW REQUIRED", "New text explicitly asks for review")
        if followup_signal:
            result.add("FOLLOW-UP", "New text contains an explicit action item or next step")
        comment_events = ("issue_comment", "pull_request_review", "pull_request_review_comment", "discussion_comment")
        if directive_signal and (mention or event_name in comment_events):
            reason = (
                f"New text directs an action to @{recipient}"
                if mention
                else "New relevant comment contains an action directive"
            )
            result.add("FOLLOW-UP", reason)
    elif mention:
        result.add("FOLLOW-UP", f"New text explicitly mentions @{recipient}")

    return result, subject, title, alert_body
