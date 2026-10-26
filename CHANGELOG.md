# 变更日志

本文件记录 prd-skill 仓库的版本变更。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

变更分类：新增（Added）／变更（Changed）／弃用（Deprecated）／移除（Removed）／修复（Fixed）／安全（Security）。

---

## [2.0.0] - 2026-10-26

从「一份可复制的 SKILL.md」升级为「按 Agent Skills 规范组织的可发布技能」：补齐模式、阶段、质量门禁、参考文件、校验脚本与示例，并修正目录结构与格式问题。

### 新增（Added）

- `prd-writer/SKILL.md` 重构为 11 个章节：技能定位、模式判定、七阶段工作流、模式细则、全局输出规范、模板与字段规范、测试用例、质量门禁、禁止事项、参考文件索引、快速对应表。
- 模式判定表：新增 A 完整生成、B 增量更新、C 评审、D 仅功能盘点、E 测试用例 5 种模式，并给出模式组合规则与默认模式。
- 七阶段工作流（阶段 0–6）：范围确认 → 功能盘点 → 访谈补全 → 骨架确认 → 分迭代起草 → 自查与门禁 → 交付，每个阶段补充关键动作、产物与完成判据。
- 功能盘点阶段独立成章：要求逐条登记代码证据（`文件路径:行号` 或符号名）、置信度（高/中/低）与建议迭代，低置信度项强制进入【待确认】。
- 质量门禁 G1–G9：结构完整、功能一致、字段齐全、编号规范、证据充分、交互深度、可测性、交付格式、语言与占位。
- 禁止事项 9 条与三条底线（证据优先、结构固定、写到可执行）。
- `prd-writer/templates/prd-template.md` 完整模板：产品需求背景 9 个小节、通用设计机制 10 类规范、两列功能表、附录 A、待确认清单。
- `prd-writer/references/` 参考文件 7 个，按渐进披露由 `SKILL.md` 按需索引：
  - `code-analysis-guide.md`：代码到功能盘点的扫描路径、证据格式、置信度判定；
  - `field-spec.md`：功能点 9 个字段的写法、「具体说明」细化标准与正反例；
  - `testcase-spec.md`：测试用例 8 列表头、四类场景、覆盖与分表规则；
  - `interview-guide.md`：分层问题库、提问话术、默认值策略；
  - `review-guide.md`：评审维度、问题分级、报告模板；
  - `delivery-guide.md`：Markdown 转 Word、功能框架图渲染、嵌入 Excel、WPS 打开与降级方案；
  - `quality-checklist.md`：交付前逐项检查清单。
- `prd-writer/scripts/validate_prd.py`：PRD 结构与一致性校验脚本，覆盖质量门禁中可机械判断的部分，支持 `--skill`、`--strict`、`--json`、`--quiet` 参数与 0/1/2 退出码。
- `prd-writer/examples/` 示例目录：提供精简 PRD 示例与功能盘点示例，兼作校验脚本的 fixture。
- 发布配套文档：`README.md`、`docs/install.md`、`docs/usage.md`、`CHANGELOG.md`、`LICENSE`、`.gitignore`。

### 变更（Changed）

- 目录结构由嵌套的 `prd-writer/prd-writer/...` 修正为单层：`prd-writer/SKILL.md`、`prd-writer/templates/`、`prd-writer/references/`、`prd-writer/scripts/`。
- 技能目录名与 frontmatter 的 `name: prd-writer` 对齐；`license` 与仓库 LICENSE 一致为 MIT；版本号写入 `metadata`。
- 功能点字段规范固化为 9 项且顺序固定（标题、更新时间、优先级、迭代版本、任务规划、功能描述、核心流程、具体说明、限制条件）。
- 全局输出规范拆分为编号格式、不确定信息、更新时间、代码证据、交付格式、功能框架图、输出长度管理、原型图、文件命名等独立小节。
- 测试用例由「随正文顺带生成」改为「按需生成」：demo 未定型阶段默认不生成，用户明确指令后再生成。
- 交付要求明确：Word 中标题与「具体说明」使用自动多级编号，功能框架图渲染为图片，测试用例以嵌入 Excel 对象呈现，生成后用 WPS 打开。
- 版本号统一为 `2.0.0`（SKILL.md、README、CHANGELOG 一致）。

### 修复（Fixed）

- 清理 SKILL.md 与模板中的字面量 HTML 实体，单元格内换行统一使用 `<br>`。
- 修正 SKILL.md 内部章节交叉引用，避免「见第 X 节」指向错误或编号错位。
- 修复模板中重复嵌套的 `prd-writer/prd-writer` 路径与失效的相对路径。
- 统一模板占位符为【】形式；校验脚本对字段语境中的 `yyyy-mm-dd`、`xxx` 等残留给出 ERROR，对数据格式说明中的 `yyyy-mm-dd` 仅给 INFO。

---

## [1.0.0 – 1.8.1]

早期版本（2026-09-15 至 2026-10-10）为技能初版与多轮迭代，未单独维护变更记录，因此不在此逐条罗列，也不补写未经记录的改动。如需追溯，请查阅 git 提交历史。

早期版本仅包含 `SKILL.md` 与 PRD 模板，尚未拆分 `references/`、`scripts/`、`examples/`，也没有本变更日志。
