# Kuasar Sandbox

**Kuasar Sandbox is a production-ready MicroVM sandbox platform for AI agents, serverless workloads, and reinforcement-learning environments.**

It combines independent guest-kernel isolation with snapshot-based lifecycle management, flexible local and remote data paths, high-density resource governance, and sandbox-level networking. The public API is compatible with the E2B SDK, and the same components can be deployed on a single node or assembled into a multi-node cluster.

> Kuasar Sandbox 是面向 AI Agent、Serverless 与强化学习工作负载的生产级 MicroVM 沙箱平台。项目提供独立 Guest Kernel 隔离、快照模板实例化、有状态暂停恢复、按需数据访问、高密资源治理和沙箱级网络能力。

## Start here

- [Project overview and source workspace](https://github.com/kuasar-sandbox/kuasar-sandbox)
- [Quick Start](https://github.com/kuasar-sandbox/kuasar-sandbox/blob/main/docs/quickstart.md)
- [Architecture](https://github.com/kuasar-sandbox/kuasar-sandbox/blob/main/docs/kuasar-sandbox.md)
- [Latest stable release](https://github.com/kuasar-sandbox/kuasar-sandbox/releases/latest)
- [Questions and design discussions](https://github.com/kuasar-sandbox/kuasar-sandbox/discussions)
- [Private security reporting](https://github.com/kuasar-sandbox/kuasar-sandbox/security)

## Repositories

| Repository | Responsibility |
| --- | --- |
| [kuasar-sandbox](https://github.com/kuasar-sandbox/kuasar-sandbox) | Project entry point, system design, cross-component validation, demos, and aggregate releases |
| [orchestrator](https://github.com/kuasar-sandbox/orchestrator) | E2B-compatible node service and multi-node control plane |
| [sandboxer](https://github.com/kuasar-sandbox/sandboxer) | MicroVM lifecycle, snapshot and restore, guest control, and on-demand data loading |
| [accelerator](https://github.com/kuasar-sandbox/accelerator) | Data access, storage, encryption, content organization, and cache infrastructure |
| [connector](https://github.com/kuasar-sandbox/connector) | High-density eBPF networking, isolation, and sandbox-level network identity |
| [guest-runtime](https://github.com/kuasar-sandbox/guest-runtime) | Guest kernel, runtime image, and image-building tools |

The five component repositories are loosely coupled: they form the complete Kuasar Sandbox platform together, while retaining independent build, deployment, release, and evolution paths.

## Contributing

Start with the [organization contribution guide](https://github.com/kuasar-sandbox/.github/blob/main/CONTRIBUTING.md). Choose the repository that owns the change, keep pull requests focused, and link companion pull requests when a change crosses repository boundaries.

Security vulnerabilities must not be reported in public issues. Follow the [security policy](https://github.com/kuasar-sandbox/kuasar-sandbox/security/policy) instead.
