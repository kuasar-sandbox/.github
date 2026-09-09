# Contributing to Kuasar Sandbox

Thank you for helping improve Kuasar Sandbox. This guide provides the organization-wide defaults; a repository may add more specific build or review requirements.

## Choose the owning repository

| Change | Repository |
| --- | --- |
| Project overview, aggregate release, cross-component E2E, demo, or shared CI | `kuasar-sandbox/kuasar-sandbox` |
| E2B API, node lifecycle, proxy, resource admission, or cluster control plane | `kuasar-sandbox/orchestrator` |
| MicroVM lifecycle, snapshot/restore, guest control, VMM integration, or vhost block path | `kuasar-sandbox/sandboxer` |
| Image/snapshot data access, storage, manifest, cache, or encryption | `kuasar-sandbox/accelerator` |
| eBPF vSwitch, network allocation, isolation, tunnel, or external policy-gateway integration | `kuasar-sandbox/connector` |
| Guest kernel, runtime bundle, init environment, or flatten-ctl image-building tools | `kuasar-sandbox/guest-runtime` |

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

## Public Fork workflow

Use GitHub's **Fork** action for the repository that owns the change, clone your public Fork, and keep the upstream repository as a separate remote:

```sh
git clone https://github.com/<you>/<repository>.git
cd <repository>
git remote add upstream https://github.com/kuasar-sandbox/<repository>.git
git fetch upstream
git switch -c <topic> upstream/main
```

Commit and push the topic branch to your Fork, then open a pull request against the owning upstream branch through GitHub. Do not put credentials in a remote URL. A pull request does not need organization membership to be opened or reviewed.

To update an unchanged Fork default branch, use a fast-forward:

```sh
git fetch upstream
git switch main
git merge --ff-only upstream/main
git push origin main
```

If the fast-forward refuses because your Fork `main` contains work, preserve that work and reconcile it on a topic branch. Do not make `reset --hard` or a force-push of Fork `main` the default synchronization procedure. Rebase or merge a topic branch when appropriate for the repository, and use `--force-with-lease` only for a topic branch whose history you intentionally own.

## Issues and proposals

Search existing issues before opening a new one. Describe the user problem and desired behavior before prescribing a large implementation. For architecture or cross-component changes, include goals, non-goals, affected ownership boundaries, compatibility implications, deployment impact, security considerations, and the smallest viable change.

Do not put credentials, customer data, private infrastructure details, or unredacted production logs in an issue. Report vulnerabilities through the project repository's private security channel.

## Pull requests

- Base work on the latest appropriate target branch (`main`, or a supported `release/vMAJOR.MINOR.x` maintenance line) and keep the pull request focused.
- Link the owning issue when one exists.
- Separate unrelated cleanup and functional changes.
- Explain the rationale, user-visible behavior, validation performed, and intentionally excluded scope.
- Preserve existing copyright, attribution, NOTICE, SPDX, and third-party license declarations.
- Do not commit generated reports, caches, credentials, private data, or local build artifacts unless the repository explicitly requires them.

For a cross-repository change, open reviewable companion pull requests and link them in both directions. Record the exact companion repository, pull-request number, branch, and commit used for integration validation. Do not assume that merging one repository silently updates another.

## Validation

Run the repository's documented unit, race, static-analysis, and build checks that apply to the change. Tests requiring KVM, root, eBPF, systemd, external storage, or the complete source workspace must state those prerequisites and must not report a skipped suite as a completed validation.

Kuasar Sandbox uses privileged Integration E2E for selected changes. Public Fork pull requests remain available for ordinary review, but untrusted Fork code is not admitted to a privileged runner merely because somebody approved the pull request. After review, a maintainer can preserve the contributor's authorship while preparing an exact organization-repository candidate; that candidate must pass the normal merge gate. Before execution, CI operators must verify that candidate code cannot access release credentials, source-materialization tokens, persistent Runner credentials or another task's writable state. Separate runner labels or root filesystems alone do not establish that boundary. If the execution environment cannot meet these requirements, keep privileged candidate execution blocked and coordinate the environment repair; do not treat a skipped test as acceptance. See the [central CI contract](https://github.com/kuasar-sandbox/kuasar-sandbox/blob/main/docs/ci.md) for exact admission, companion declarations and integration-commit validation.

## Documentation changes

Follow the [documentation policy](https://github.com/kuasar-sandbox/kuasar-sandbox/blob/main/CONTRIBUTING.md#documentation-contributions). Publish complete English at `name.md`; preserve existing Chinese as `name_zh.md` with reciprocal language selectors. Existing complete English-only documents may remain English-only. Keep requirements, API/configuration identifiers, examples, diagrams, facts and links synchronized across a maintained pair. Record source revisions and evidence for factual corrections. A summary or a passing language detector does not establish a complete translation.

## Licensing of contributions

By submitting a contribution, you agree that it is licensed under the license that applies to the files being changed. New project files without a different explicit license declaration are contributed under the Apache License 2.0.

Only submit material that you have the right to contribute. Third-party or differently licensed files, patches, generated sources, kernel material, and bundled binaries must retain their applicable notices and source obligations.

## Community conduct

Participation is governed by the organization [Code of Conduct](https://github.com/kuasar-sandbox/.github/blob/main/CODE_OF_CONDUCT.md).
