"""Signal patterns and Markdown helpers for the work-activity monitor."""

from __future__ import annotations

import re
from typing import Sequence

MAX_EXCERPT = 700
DESIGN_LABEL_HINTS = ("design", "proposal", "rfc", "architecture", "spec")
DESIGN_TITLE_RE = re.compile(
    r"(?:^|[\[（(\s])(?:rfc|design|proposal|spec|architecture)(?:[\]）):：\s-]|$)"
    r"|设计|提案|方案讨论|架构",
    re.IGNORECASE,
)
BLOCKER_RE = re.compile(
    r"\b(?:blocker|blocked(?:\s+by)?|blocking|cannot\s+proceed|can't\s+proceed|"
    r"unable\s+to\s+proceed|waiting\s+on|stuck|hard\s+dependency)\b"
    r"|阻塞|被阻塞|卡住|无法继续|不能继续|等待.{0,40}(?:完成|解决|确认|合入)|依赖.{0,40}才能",
    re.IGNORECASE | re.DOTALL,
)
DECISION_RE = re.compile(
    r"\b(?:final\s+decision|decision\s*(?:is|:)|decided|we\s+(?:agreed|will\s+proceed)|"
    r"consensus|accepted|rejected|approved|resolved|not\s+planned|won't\s+do|will\s+not\s+do)\b"
    r"|(?:最终)?结论|决定(?:采用|不采用|按|为|是)|已定|达成一致|同意采用|采纳(?:该|此)?方案|"
    r"不采纳|批准|拒绝|不计划|按.{0,30}(?:方案|设计|实现)(?:推进|处理|执行)",
    re.IGNORECASE | re.DOTALL,
)
DEADLINE_WORD_RE = re.compile(
    r"\b(?:deadline|due\s+date|due\s+by|no\s+later\s+than|must\s+(?:land|finish|complete)\s+by|"
    r"target\s+date|time[- ]sensitive)\b|截止|最晚|到期|期限|必须在.{0,30}之前",
    re.IGNORECASE | re.DOTALL,
)
DATE_LIKE_RE = re.compile(
    r"\b(?:20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}(?:[-/.]\d{2,4})?|"
    r"(?:mon|tues?|wed(?:nes)?|thu(?:rs)?|fri|sat(?:ur)?|sun)(?:day)?|"
    r"today|tomorrow|this\s+week|next\s+week|end\s+of\s+(?:day|week|month)|eod|eow)\b"
    r"|(?:20\d{2}年)?\d{1,2}月\d{1,2}日|今天|明天|本周|下周|月底|周[一二三四五六日天]",
    re.IGNORECASE,
)
BY_DATE_RE = re.compile(
    r"\bby\s+(?:20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}|"
    r"(?:mon|tues?|wed(?:nes)?|thu(?:rs)?|fri|sat(?:ur)?|sun)(?:day)?|"
    r"today|tomorrow|end\s+of\s+(?:day|week|month)|eod|eow)\b",
    re.IGNORECASE,
)
REVIEW_TEXT_RE = re.compile(
    r"\b(?:please\s+review|review\s+(?:needed|required|requested)|needs?\s+review|request(?:ing)?\s+review)\b"
    r"|请.{0,20}(?:评审|检视|review)|需要.{0,20}(?:评审|检视|review)",
    re.IGNORECASE | re.DOTALL,
)
STRONG_FOLLOWUP_RE = re.compile(
    r"\b(?:action\s+item|follow[- ]?up|required\s+follow[- ]?up|next\s+step|todo)\b"
    r"|行动项|待办|后续跟进|需要跟进|下一步",
    re.IGNORECASE,
)
DIRECTIVE_RE = re.compile(
    r"\b(?:please|must|need(?:s)?\s+to|required\s+to)\b|请|必须|需要",
    re.IGNORECASE,
)
BLOCKER_LABEL_RE = re.compile(r"(?:^|[/ _-])(?:blocker|blocked|blocking|critical)(?:$|[/ _-])", re.I)
DECISION_LABEL_RE = re.compile(r"(?:decision|accepted|approved|rejected|resolved|not[- _]?planned)", re.I)
DEADLINE_LABEL_RE = re.compile(r"(?:deadline|due[- _]?date|time[- _]?sensitive)", re.I)
REVIEW_LABEL_RE = re.compile(r"(?:needs?[- _]?review|review[- _]?(?:needed|required)|ready[- _]?for[- _]?review)", re.I)
FOLLOWUP_LABEL_RE = re.compile(r"(?:follow[- _]?up|action[- _]?item|todo|needs?[- _]?(?:info|work|changes))", re.I)

CATEGORY_ORDER = {
    "BLOCKER": 0,
    "DEADLINE": 1,
    "REVIEW REQUIRED": 2,
    "CHANGES REQUESTED": 3,
    "DECISION": 4,
    "FOLLOW-UP": 5,
    "TEST": 6,
}


def strip_inert_markdown(text: str) -> str:
    """Remove quoted/code/HTML-comment content before keyword classification."""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    inline_code = re.compile(r"`[^`]*`")
    return "\n".join(
        inline_code.sub(" ", line)
        for line in text.splitlines()
        if not line.lstrip().startswith(">")
    )


def text_mentions(text: str, user: str) -> bool:
    return bool(re.search(rf"(?<![A-Za-z0-9_-])@{re.escape(user)}(?![A-Za-z0-9_-])", text, re.I))


def is_design_thread(title: str, labels: Sequence[str]) -> bool:
    lowered = [item.lower() for item in labels]
    return bool(DESIGN_TITLE_RE.search(title)) or any(
        any(hint in item for hint in DESIGN_LABEL_HINTS) for item in lowered
    )


def neutralize_mentions(text: str) -> str:
    return re.sub(r"@(?=[A-Za-z0-9])", "@\u200b", text)


def markdown_link_text(text: str) -> str:
    return neutralize_mentions(text).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def excerpt(text: str) -> str:
    compact = text.strip()
    if not compact:
        return ""
    if len(compact) > MAX_EXCERPT:
        compact = compact[: MAX_EXCERPT - 1].rstrip() + "…"
    compact = neutralize_mentions(compact)
    return "\n".join(f"> {line}" if line else ">" for line in compact.splitlines())
