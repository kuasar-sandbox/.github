[English](README.md) | [简体中文](README_zh.md)

# Kuasar Sandbox

**Kuasar Sandbox 是面向 AI Agent、Serverless 与强化学习工作负载的生产级 MicroVM 沙箱平台。**

项目将独立 Guest Kernel 隔离、快照驱动的生命周期管理、灵活的本地与远程数据路径、高密资源治理和沙箱级网络结合起来，提供快照模板实例化、有状态暂停恢复和按需数据访问。公开 API 兼容 E2B SDK；同一套组件既可部署在单节点，也可组装为多节点集群。

## 从这里开始

- [项目总览与源码工作区](https://github.com/kuasar-sandbox/kuasar-sandbox/blob/main/README_zh.md)
- [快速开始](https://github.com/kuasar-sandbox/kuasar-sandbox/blob/main/docs/quickstart_zh.md)
- [系统架构](https://github.com/kuasar-sandbox/kuasar-sandbox/blob/main/docs/kuasar-sandbox_zh.md)
- [最新 Stable 发布](https://github.com/kuasar-sandbox/kuasar-sandbox/releases/latest)
- [使用问题与设计讨论](https://github.com/kuasar-sandbox/kuasar-sandbox/discussions)
- [私密安全报告](https://github.com/kuasar-sandbox/kuasar-sandbox/security)

## 仓库

| 仓库 | 职责 |
| --- | --- |
| [kuasar-sandbox](https://github.com/kuasar-sandbox/kuasar-sandbox) | 项目入口、系统设计、跨组件验证、演示和聚合发布 |
| [orchestrator](https://github.com/kuasar-sandbox/orchestrator) | 兼容 E2B 的节点服务与多节点控制面 |
| [sandboxer](https://github.com/kuasar-sandbox/sandboxer) | MicroVM 生命周期、快照与恢复、Guest 控制和按需数据加载 |
| [accelerator](https://github.com/kuasar-sandbox/accelerator) | 数据访问、存储、加密、内容组织和缓存基础设施 |
| [connector](https://github.com/kuasar-sandbox/connector) | 高密 eBPF 网络、隔离和沙箱级网络身份 |
| [guest-runtime](https://github.com/kuasar-sandbox/guest-runtime) | Guest 内核、Runtime Bundle 和镜像构建工具 |

五个组件仓保持松耦合：它们共同构成完整的 Kuasar Sandbox 平台，同时保留独立的构建、部署、发布和演进路径。

五个组件仓当前仍为私有，等待[项目 #82](https://github.com/kuasar-sandbox/kuasar-sandbox/issues/82)跟踪的协调源码公开窗口。切换前，组件链接需要授权访问；公开的项目入口和聚合发布仍然可用。

## 参与贡献

请先阅读[组织贡献指南（英文）](https://github.com/kuasar-sandbox/.github/blob/main/CONTRIBUTING.md)。选择实际拥有变更的仓库，保持 PR 聚焦；变更跨越仓库边界时，互相链接 companion PR。

安全漏洞不得通过公开 Issue 报告，请遵循[安全策略](https://github.com/kuasar-sandbox/kuasar-sandbox/security/policy)。
