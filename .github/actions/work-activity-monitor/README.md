# Work activity monitor

A composite GitHub Action that surfaces high-confidence reviews, decisions, deadlines, blockers, and required follow-ups into a rolling per-repository issue.

The caller must provide a repository-scoped token with `issues: write` and the GitHub login that should receive alerts. The action is designed for event-driven use and does not inspect pull-request code or require third-party services.
