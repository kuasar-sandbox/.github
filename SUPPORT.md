# Kuasar Sandbox Support

## Questions and usage help

Use [Kuasar Sandbox Discussions](https://github.com/kuasar-sandbox/kuasar-sandbox/discussions) for architecture questions, deployment guidance, integration help, and general usage discussion. Include the aggregate release or component commit, deployment mode, CPU architecture, Linux kernel, storage path, and relevant sanitized logs.

## Bugs

Open a bug in the repository that owns the failing behavior. The organization issue form helps collect:

- aggregate release and component version or commit;
- single-node or cluster deployment mode;
- host architecture, kernel, KVM/eBPF/systemd prerequisites, and storage/network backend;
- minimal reproduction steps;
- expected and actual behavior;
- sanitized logs and whether the issue is reproducible.

Project-level packaging, aggregate release, shared CI, demos, or cross-component failures belong in `kuasar-sandbox/kuasar-sandbox`.

## Feature requests and designs

Open component-local requests in the owning component repository. Use the project repository for proposals that change multiple components or system-level contracts. Explain the underlying user need, goals, non-goals, alternatives, compatibility, deployment, security, and operational impact.

## Security vulnerabilities

Do not open a public issue. Follow the [project security policy](https://github.com/kuasar-sandbox/kuasar-sandbox/security/policy) and use its private reporting channel.

## Service expectations

Kuasar Sandbox is an open-source project. Maintainers prioritize issues according to impact, reproducibility, safety, and available capacity; no response-time or support SLA is implied. Production support arrangements, if any, are outside the public issue tracker.
