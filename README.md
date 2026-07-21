# NanoHarness 学习总入口

**永远只从本页决定下一篇。** 文件编号表示主题 owner，不表示阅读顺序；其他 Markdown 只负责
一个节点并返回这里。运行事实、代码和正式 claim 以 [NanoHarness](https://github.com/semi-hollow/NanoHarness)
主仓为准；本页是“我该怎么学”的唯一 owner。

> **首次主线指针：从 A1 开始。** A1 未完成时只打开主仓 Debug Lab，按 1 → 4 调试到底；
> 完成后回本页进入 A2。不要同时摊开其他文档。

## 文档树：只认这一棵

<!-- DOC_MAP:START -->
- **A. 首次必须完成的主学习链**
  1. **A1 动态掌握：**[NanoHarness Debug Lab](https://github.com/semi-hollow/NanoHarness/blob/master/examples/debug_lab/README.md)——按四个共享配置调试控制面、固定修复、真实 DeepSeek 与 Astropy Evidence；断点、fixture、路径和恢复均已准备。
  2. **A2 建立骨架：**[系统地图与代码入口](learning/01-系统地图与代码入口.md)——用自己的 trace 对照黄金主链，随机定位一个 symbol 才退出。
  3. **A3 理解机制：**[核心机制与设计边界](learning/02-核心机制与设计边界.md)——闭卷讲 AgentLoop、Context、Tool、HITL、Recovery 的因果与边界。
  4. **A4 读懂证据：**[Benchmark 与证据闭环](learning/03-Benchmark与证据闭环.md)——用自己的 artifact 区分 candidate/local/official。
  5. **A5 验收掌握：**[闭卷自测与反馈](learning/04-闭卷自测与反馈.md)——达到 13/15、无 0 分，并通过随机 symbol/artifact 定位。
  6. **A6 面试交付：**[五分钟现场演示](interview/demo/五分钟面试演示脚本.md)——完整演示并填写演示后自评。
- **B. 只在出现对应问题时查**
  - **B1 定位与取舍：**[北京 Agent 市场与 NanoHarness 定位](interview/strategy/2026-07-19_北京Agent招聘市场与NanoHarness定位.md)——岗位、框架质疑、简历口径或范围决策。
  - **B2 外部题库：**[Clowder Agent 面经](interview/references/Clowder_AI_Agent_面经精练版.md)——只提供新问题，不提供项目事实或答案。
- **C. 一手档案，只检索、不顺序学习**
  - **C1 真实面试：**[2026-07-17 模拟面试复盘](records/interviews/2026-07-17_NanoHarness模拟面试复盘与标准回答.md)——保留当时问题、错误和修正依据，不当通用答案稿。
<!-- DOC_MAP:END -->

## 你现在怎么学

首次只走：`A1 实操 -> A2 系统 -> A3 机制 -> A4 Evidence -> A5 自测 -> A6 演示`。

首次通过后改为短循环：`A5 自测 -> 只补最低分的 A2/A3/A4 -> A5 复测 -> A6`。当天、1 天后、
7 天后复测；连续两次满分的主题退出当前队列。B/C 永远不进入顺序通读。

## 卡住时只按问题路由

| 我卡在哪里 | 只打开 | 看到哪里立即停止 |
| --- | --- | --- |
| 不会命令、路径、断点、artifact 或 Astropy 实跑 | A1 | 填完完成记录 |
| 随机类/方法不知道谁调用、为何存在、能否删 | A2 | 两分钟定位题通过 |
| AgentLoop、Context、Tool、审批或 Resume 讲不清 | A3 | Core 机制和边界；Advanced 不展开 |
| patch/local/official、producer/consumer 或实验结论混乱 | A4 | claim boundary；不读 JSON renderer |
| 不知道自己到底会不会 | A5 | 13/15、无 0 分、随机定位通过 |
| 要准备现场面试 | A6 | 演示后自评完成 |
| 为什么不用 LangGraph、项目定位、架构或简历口径 | B1 | 只查对应小节 |
| 某次真实面试为何答错 / 第三方又问了什么 | C1 / B2 | 只取事实或题目，不抄成答案 |
| 精确 CLI、架构或 Case 事实 | 主仓 Facade / Architecture / Case | 查到一手合同即返回当前节点 |

主仓按需入口：[Facade](https://github.com/semi-hollow/NanoHarness/blob/master/docs/architecture/facade-catalog.md)、
[Architecture](https://github.com/semi-hollow/NanoHarness/blob/master/docs/ARCHITECTURE.md)、
[Astropy Case](https://github.com/semi-hollow/NanoHarness/blob/master/docs/case-studies/astropy-12907.md)。

## 绝对不要这样读

- 不按目录或 `01 -> 05` 机械顺读；编号不是顺序。
- 不通读 NanoHarness 主仓 `docs/`；学习 owner 要求证据时才查一手合同。
- 不从 B2/C1 开始，也不把第三方材料或一次面试复盘当项目答案。
- Core 未通过前不读 Memory、Multi/Fanout、MCP、Skills、Campaign。
- 不学习 tests、JSON/Markdown/HTML renderer、Official 兼容解析和临时目录清理的实现细节。
- 一个问题只看一个 owner；答完立即回本页，不跨多篇搜平行答案。

## 掌握预算与通过标准

| 层级 | 标准 |
| --- | --- |
| Core | 闭卷讲因果和边界，能沿代码与 artifact 找到证据 |
| Follow-up | 知道入口和设计取舍，被追问时再展开 |
| Advanced | 只知道用途、边界和查询入口，不背实现 |

首次代码面限制在 A2 的 10–12 个 Core 文件。总通过标准：A5 至少 13/15 且无 0 分、随机定位通过、
A1 有真实 run/resume/Local/Official 记录、A6 可在五分钟完成。

## 唯一 owner 与受保护事实

- 同一知识点只能由树中一个节点回答；其他文档只能链接，不复制一套解释。
- [开发故障档案](https://github.com/semi-hollow/NanoHarness/blob/master/docs/evaluation/failure-driven-improvements.md)
  和 C1 是追加式一手事实。删除、截断、迁移或用摘要替换，必须得到用户当次明确确认。
- 新内容归属：运行事实进主仓；开发故障进故障档案；真实面试进 C1；理解补充进 A2/A3/A4；
  完整操作进 A1；错题进 A5；现场动作进 A6；定位/治理进 B1；第三方材料进 B2；计划只进 issue/commit/history。
- 只有现有节点无法归属且能进入学习链时才可新建 Markdown，并必须先更新本页与门禁。

## 防劣化门禁

```bash
python3 scripts/check_docs.py
```

门禁拒绝：第二个 README、未挂到文档树或重复挂载的 Markdown、没有返回总入口的子文档、超预算、
失效链接，以及一手记录被删除或压缩。
