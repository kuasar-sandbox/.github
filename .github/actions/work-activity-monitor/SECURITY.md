# Security model

This action runs only trusted code pinned by the caller to a full commit SHA. It reads GitHub event metadata, uses the caller repository's scoped `GITHUB_TOKEN`, writes only issue alerts in that repository, does not check out pull-request code, and sends no data to third-party services.
