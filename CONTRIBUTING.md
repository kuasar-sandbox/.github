# Contributing to Kuasar Sandbox

Thank you for helping improve Kuasar Sandbox. This guide provides the organization-wide defaults; a repository may add more specific build or review requirements.

## Choose the owning repository

| Change | Repository |
| --- | --- |
| Project overview, aggregate release, cross-component E2E, demo, or shared CI | `kuasar-sandbox/kuasar-sandbox` |
| E2B API, node lifecycle, proxy, resource admission, or cluster control plane | `kuasar-sandbox/orchestrator` |
| MicroVM lifecycle, snapshot/restore, guest control, VMM integration, or vhost block path | `kuasar-sandbox/sandboxer` |
| Image/snapshot data access, storage, manifest, cache, encryption, or image flattening | `kuasar-sandbox/accelerator` |
| eBPF vSwitch, network allocation, isolation, tunnel, or external policy-gateway integration | `kuasar-sandbox/connector` |
| Guest kernel, runtime image, init environment, or image-building inputs | `kuasar-sandbox/guest-runtime` |

Use the project repository for a cross-component design discussion, but implement each component-owned change in its own repository.

## Workspace

The standard source workspace places the project repository and five component repositories next to one another:

```text
workspace/
├── kuasar-sandbox/
├── orchestrator/
├── sandboxer/
├── accelerator/
├── connector/
└── guest-runtime/
```

Clone only the repository needed for a component-local change. Clone all six when running project-level builds or exact-source integration tests. Each repository README documents its supported local commands and prerequisites.

## Issues and proposals

Search existing issues before opening a new one. Describe the user problem and desired behavior before prescribing a large implementation. For architecture or cross-component changes, include goals, non-goals, affected ownership boundaries, compatibility implications, deployment impact, security considerations, and the smallest viable change.

Do not put credentials, customer data, private infrastructure details, or unredacted production logs in an issue. Report vulnerabilities through the project repository's private security channel.

## Pull requests

- Base work on the latest default branch and keep the pull request focused.
- Link the owning issue when one exists.
- Separate unrelated cleanup and functional changes.
- Explain the rationale, user-visible behavior, validation performed, and intentionally excluded scope.
- Preserve existing copyright, attribution, NOTICE, SPDX, and third-party license declarations.
- Do not commit generated reports, caches, credentials, private data, or local build artifacts unless the repository explicitly requires them.

For a cross-repository change, open reviewable companion pull requests and link them in both directions. Record the exact companion repository, pull-request number, branch, and commit used for integration validation. Do not assume that merging one repository silently updates another.

## Validation

Run the repository's documented unit, race, static-analysis, and build checks that apply to the change. Tests requiring KVM, root, eBPF, systemd, external storage, or the complete source workspace must state those prerequisites and must not report a skipped suite as a completed validation.

Kuasar Sandbox uses privileged cross-component validation for selected changes. Untrusted fork code does not receive release credentials or automatic access to privileged runners; maintainers may approve an appropriate integration run after reviewing the change.

## Licensing of contributions

By submitting a contribution, you agree that it is licensed under the license that applies to the files being changed. New project files without a different explicit license declaration are contributed under the Apache License 2.0.

Only submit material that you have the right to contribute. Third-party or differently licensed files, patches, generated sources, kernel material, and bundled binaries must retain their applicable notices and source obligations.

## Community conduct

Participation is governed by the organization [Code of Conduct](https://github.com/kuasar-sandbox/.github/blob/main/CODE_OF_CONDUCT.md).
