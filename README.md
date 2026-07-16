# NanoHarness 学习与面试笔记

这是 NanoHarness 的个人学习、代码阅读和面试准备仓库。

运行时代码、正式架构契约、能力边界和评测证据属于
[NanoHarness](https://github.com/semi-hollow/NanoHarness)；教学材料和个人准备内容统一维护在这里，避免公开项目仓库同时承担产品展示和学习笔记两种职责。

## 推荐阅读顺序

1. [Agent Forge 总体架构与运行链路](learning/architecture/AgentForge总体架构与运行链路.md)
2. [Python 分层与调用关系](learning/architecture/Python分层与调用关系.md)
3. [NanoHarness 代码阅读地图](learning/architecture/NanoHarness代码阅读地图.md)
4. [Runtime 学习路径](learning/architecture/Runtime学习路径.md)
5. [核心组件索引与职责边界](learning/architecture/核心组件索引与职责边界.md)
6. [上下文、记忆与模型适配](learning/architecture/上下文记忆与模型适配.md)
7. [Runtime 能力导览](learning/capabilities/Runtime能力导览.md)
8. [Multi-Agent 协作与对比评测](learning/capabilities/多Agent协作机制与对比评测说明.md)
9. [评测目录与 SWE-bench 使用入口](learning/evaluation/评测目录说明与SWE-bench使用入口.md)
10. [Benchmark 闭环设计与面试表达](learning/evaluation/Benchmark闭环设计与面试表达.md)

## 面试准备

- [Clowder 面经回答思路：NanoHarness 查漏补缺版](interview/answers/Clowder_AI_Agent_面经回答思路_NanoHarness查漏补缺.md)
- [Clowder AI Agent 面经精练版](interview/references/Clowder_AI_Agent_面经精练版.md)
- [五分钟演示脚本](interview/demo/五分钟面试演示脚本.md)
- [AI Agent 项目问答](interview/defense/AI智能体项目面试问答.md)
- [Agent Engineer 面试题库](interview/defense/AI智能体项目面试题库.md)
- [安全边界讲解](interview/defense/Agent安全边界与权限防守说明.md)
- [失败分类与排查话术](interview/defense/失败分类体系与排查话术.md)

## 目录职责

| 目录 | 内容 |
| --- | --- |
| `learning/architecture/` | 架构、分层、调用链和代码阅读地图 |
| `learning/capabilities/` | Runtime、Multi-Agent 等核心能力导览 |
| `learning/evaluation/` | Evaluation、SWE-bench 和证据阅读入口 |
| `learning/legacy/` | 仍有参考价值但可能落后于当前实现的旧版学习资料 |
| `interview/` | 面经、回答稿、演示脚本和技术防守材料 |
| `history/` | 历史设计规格、实施计划和 handoff，仅用于理解演进过程 |
| `local-archive/` | Git bundle、PDF、完整 demo evidence 等本地归档，不推送 GitHub |

## 内容边界

- `learning/` 中的最新文档应以 NanoHarness 当前代码为准。
- `learning/legacy/` 和 `history/` 用于理解历史，不代表当前能力承诺。
- 面试回答必须区分“已经由 Runtime 执行”“仅有实验接口”和“项目明确不覆盖”。
- 项目行为或接口发生实质变化时，同步更新相应学习文档，不把教学说明重新放回 NanoHarness。
