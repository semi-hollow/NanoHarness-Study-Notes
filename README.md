# NanoHarness 学习训练册

这个仓库只服务两个结果：

1. 能闭卷解释 NanoHarness 的黄金主链、核心机制、证据和边界。
2. 面对任意重要 symbol 或 artifact，能快速定位它的上游、下游、存在理由和证据作用。

运行代码、正式架构和公开 claim 以
[NanoHarness](https://github.com/semi-hollow/NanoHarness)为准。本仓库只保存学习训练、面试演示和
个人定位材料。**本 README 是文档结构的唯一控制入口。**

## 唯一学习路线

先测后学，不按文件顺序通读：

1. 用[闭卷自测与反馈](learning/04-闭卷自测与反馈.md)完成五个必会问题。
2. 如果还没有亲手跑过完整链路，按
   [从命令到 Evidence：macOS 全链路实操](learning/05-从命令到Evidence全链路实操.md)
   完成一次 CLI、断点、artifact、resume 和真实 Astropy Case。
3. 只补最低分主题：[系统地图与代码入口](learning/01-系统地图与代码入口.md)、
   [核心机制与设计边界](learning/02-核心机制与设计边界.md)或
   [Benchmark 与证据闭环](learning/03-Benchmark与证据闭环.md)。
4. 随机抽一个生产 symbol 和一个 run artifact，完成定位训练；不要只重复熟悉入口。
5. 回到同一份自测闭卷重答，达标后练[五分钟现场演示](interview/demo/五分钟面试演示脚本.md)。
6. 只在岗位选择、框架质疑或范围决策时查
   [北京 Agent 市场与 NanoHarness 定位](interview/strategy/2026-07-19_北京Agent招聘市场与NanoHarness定位.md)。

原始外部面经只作出题来源，不要求通读：
[Clowder Agent 面经](interview/references/Clowder_AI_Agent_面经精练版.md)。

## 学习范围预算

主学习面只有一条黄金主链和五个问题。首次阅读限制在 `00 NanoHarness Review Path` 的
10–12 个核心文件；CLI parser、序列化细节、Multi/Fanout、Memory、MCP、Skills 和完整 Benchmark
均为按需追问，不得挤入主演示。

学习时使用三个层级：

| 层级 | 掌握标准 |
| --- | --- |
| Core | 能闭卷讲机制，沿调用链找到 owner，并用 artifact 证明结论 |
| Follow-up | 能解释设计边界和入口；被追问时再展开源码 |
| Advanced | 知道用途、限制和查询入口，不要求背实现 |

新设备先按[系统地图与代码入口](learning/01-系统地图与代码入口.md)安装 PyCharm Scope。

## 五类文档

| 分类 | 文档 | 使用时机 |
| --- | --- | --- |
| 加深理解 | 01 系统地图、02 核心机制、03 Benchmark | 自测暴露知识缺口后定向阅读 |
| 检验掌握 | 04 闭卷自测与反馈 | 每轮学习前后，必须留下分数和错误 |
| 面试反制 | 五分钟演示、岗位定位 | 现场证明能力，预先处理常见质疑 |
| 外部输入 | Clowder 面经 | 只提供新问题，不作为项目事实来源 |
| 一手记录 | 开发故障档案、真实面试复盘 | 保留当时事实，用于复查认知变化，不要求顺序通读 |

## 内容唯一归属

同一知识点只能有一个 owner，其他文档只链接，不复制答案。

| 内容 | 唯一 owner |
| --- | --- |
| 黄金主链、六边形依赖、symbol 定位 | `learning/01` |
| Runtime、Context、Tool、HITL、Recovery 机制 | `learning/02` |
| Run Story、artifact 血缘、evaluation 与实验归因 | `learning/03` |
| 五个必会问题、追问卡、评分与复测记录 | `learning/04` |
| macOS 核心命令实操顺序、断点和观察记录 | `learning/05` |
| 五分钟展示取舍、现场话术、失败备用方案 | `interview/demo` |
| 项目口径、架构取舍、理解成本硬约束、质疑应答 | `interview/strategy` |
| 第三方原始材料 | `interview/references` |
| 真实面试复盘 | `records/interviews` |

## 受保护的一手记录

- [开发故障档案](https://github.com/semi-hollow/NanoHarness/blob/master/docs/evaluation/failure-driven-improvements.md)
  是代码仓库中的追加式事实源，不得用摘要替换或移入 Git 历史。
- [2026-07-17 NanoHarness 模拟面试复盘](records/interviews/2026-07-17_NanoHarness模拟面试复盘与标准回答.md)
  保留原始问题、当时错误和修正依据，不和通用回答稿合并。
- 文档清理可以删除重复解释和过时计划；删除、截断或迁移一手记录必须获得用户当次明确确认。

## 新内容决策

新增内容时按顺序判断：

1. 运行时事实、公开能力或正式证据：更新 NanoHarness 主仓库。
2. 实际开发故障：追加到公开开发故障档案，保留现象到验证的完整链路。
3. 真实面试及其复盘：保存到 `records/interviews`，不能只留下提炼答案。
4. 帮助理解已有能力：合并进 `learning/01`、`02` 或 `03`；完整实操步骤只进入 `learning/05`。
5. 脱离真实事件的新练习题或一次答错：只进入 `learning/04` 的追问和复测记录。
6. 现场演示动作：更新五分钟演示脚本。
7. 定位、架构取舍或治理约束：更新现有 strategy owner。
8. 第三方原始材料：只进入 `interview/references`。
9. 实施计划、阶段记录或过时方案：使用 Git issue、commit 或历史，不进入学习树。

只有内容跨越现有 owner、需要独立维护且能进入学习路线时，才允许新建文档；同时必须更新
本 README 和自动检查白名单。不能为同一能力增加平行解释。

## 学习与反馈规则

- **先输出，后校对。** 每题先口述或手画，再看评分锚点。
- **认得不算会。** 定义记 1 分；因果与边界记 2 分；代码和 evidence 都能定位才记 3 分。
- **随机定位。** 熟悉 `Harness.run` 不等于能掌握项目；每轮必须换一个 symbol 和 artifact。
- **每次只补最低分。** 已连续两次达到 3 分的主题退出当前学习队列。
- **间隔复测。** 当天、1 天后、7 天后复测，并记录可执行的下一动作。

通过标准：五个必会问题至少 13/15 分、没有 0 分；随机 symbol/artifact 定位和五分钟演示均通过。

## 防劣化门禁

```bash
python3 scripts/check_docs.py
```

检查拒绝未归类 Markdown、超出体量预算、缺少反馈入口、README 漏链和失效本地链接。文件上限
不是写作目标；触线时先删除重复内容，不新增一套说明。
