# prd-skill

基于已有代码仓库，反向生成、补全、更新与评审产品需求文档（PRD）的 Agent Skill。遵循 [Agent Skills 开放标准](https://agentskills.io/specification)，可作为 TRAE 技能安装，也兼容 Claude Code、Cursor 等客户端。

技能读取仓库中的路由、页面、接口、数据模型与权限配置，把已经实现的产品事实翻译成研发可估时、UI 可出图、QA 可写用例的 PRD。输出遵循固定的章节骨架与字段规范，无法从代码中找到依据的内容一律标注【待确认】，不编造。当前版本：`2.0.0`。

## 1. 核心能力

- **五种工作模式**：完整生成、增量更新、评审、仅功能盘点、测试用例。支持组合使用，例如「先盘点功能点，确认后再写 PRD」。
- **七阶段工作流（阶段 0–6）**：范围确认 → 功能盘点 → 访谈补全 → 骨架确认 → 分迭代起草 → 自查与门禁 → 交付。每个阶段有明确产物与完成判据，不满足判据不进入下一阶段。
- **代码证据可追溯**：功能盘点逐条登记代码证据（`文件路径:行号` 或符号名）与置信度（高/中/低），低置信度项强制进入【待确认】清单。
- **固定模板与字段规范**：PRD 章节骨架不可增删；每个子功能固定 9 个字段（功能点标题、更新时间、优先级、迭代版本、任务规划、功能描述、核心流程、具体说明、限制条件），「具体说明」细化到 RD 可估时、UI 可出图、QA 可写用例的粒度。
- **一致性要求**：功能清单、功能框架图、正文的功能数量与命名必须完全一致；测试用例可追溯到功能点与「具体说明」叶子条目。
- **质量门禁**：G1–G9 九项门禁覆盖结构、功能一致、字段、编号、证据、交互深度、可测性、交付格式、语言与占位。
- **交付规范**：最终交付 Word（`.docx`）；标题与「具体说明」使用自动多级编号，功能框架图渲染为 PNG，测试用例以嵌入 Excel 对象呈现，生成后自动用 WPS 打开（未安装时回退到默认应用并说明）。
- **渐进披露**：`SKILL.md` 以流程、门禁与索引为主，详细规范拆到 `prd-writer/references/` 按需读取，避免一次占用过多上下文。
- **校验脚本**：`scripts/validate_prd.py` 对 PRD 的结构、字段、编号与一致性做机械检查，可接入交付前自检。

### 1.1 适用与不适用

| 适用 | 不适用 |
|------|--------|
| 已有代码仓库（含 demo、原型、生产系统），需要补写或补全 PRD | 从零构思新产品，仓库里没有可参考的实现 |
| 按版本、迭代梳理功能清单，规划研发排期 | 纯市场方案、商业计划书、竞品分析 |
| 评审已有 PRD 是否完整、可执行、可测试 | 需要编造数据、指标、人名、时间的文档 |
| 代码变更后同步更新 PRD 对应章节 | 没有代码证据、仅凭口头描述就想定稿的需求 |

## 2. 与普通 prompt 的区别

| 维度 | 普通 prompt | prd-writer 技能 |
|------|-------------|-----------------|
| 输入依据 | 依赖用户口述与模型先验，容易补全不存在的功能 | 先扫描代码形成功能盘点，每条功能登记代码证据与置信度 |
| 输出结构 | 每次结构不同，章节与字段靠模型自由发挥 | 固定模板、固定编号层级与 9 个功能点字段 |
| 工作流程 | 一次生成，缺少确认点 | 七阶段推进，功能盘点与骨架确认都要用户确认 |
| 一致性 | 功能清单、框架图、正文容易互相冲突 | G2 门禁要求三处数量与命名一致，脚本可校验 |
| 不确定信息 | 常被直接编造或含糊带过 | 在正文对应位置标注【待确认】，Word 中红色显示，不跳转、不另列表格 |
| 交付质量 | 只给 Markdown 文本，格式与编号无保证 | 按交付规范转 Word：自动多级编号、框架图 PNG、嵌入 Excel 测试用例 |
| 可复用性 | 每次重新写 prompt，结果不稳定 | 技能 + 模板 + 参考规范 + 校验脚本，输出稳定可复现 |

## 3. 仓库结构

```text
prd-skill/
├── README.md                           # 项目说明（本文件）
├── LICENSE                             # MIT 许可证
├── CHANGELOG.md                        # 版本变更记录
├── .gitignore
├── prd-writer/                         # 技能目录（安装时整体复制）
│   ├── SKILL.md                        # 技能入口：模式、工作流、门禁、禁止事项、参考索引
│   ├── templates/
│   │   └── prd-template.md             # 固定 PRD 模板：章节骨架、两列功能表
│   ├── references/                     # 按需加载的详细规范（7 个）
│   │   ├── code-analysis-guide.md      # 代码 → 功能盘点的扫描路径与证据规范
│   │   ├── field-spec.md               # 功能点 9 个字段的写法与正反例
│   │   ├── testcase-spec.md            # 测试用例 8 列、四类场景、覆盖规则
│   │   ├── interview-guide.md          # 访谈问题库、提问话术、默认值策略
│   │   ├── review-guide.md             # 评审维度、问题分级、报告模板
│   │   ├── delivery-guide.md           # Markdown 转 Word、框架图渲染、嵌入 Excel
│   │   └── quality-checklist.md        # 交付前逐项检查清单
│   ├── examples/                       # 示例输出，兼作校验脚本 fixture
│   │   ├── README.md                   # 示例说明与自测方法
│   │   ├── PRD-示例-在线考试系统.md    # 精简 PRD 示例
│   │   └── 功能盘点-示例.md            # 功能盘点示例
│   └── scripts/
│       └── validate_prd.py             # PRD 结构与一致性校验（仅标准库）
└── docs/
    ├── install.md                      # 安装：TRAE 为主，兼容 Claude Code / Cursor
    └── usage.md                        # 使用：五种模式、产物、分段生成、校验
```

本地临时目录（`_research/`、`_review/` 等）已加入 `.gitignore`，不随仓库提交。

## 4. 安装

技能安装的本质是把 `prd-writer/` 目录放到客户端会扫描的技能目录下，并保持目录名与 `SKILL.md` 的 `name: prd-writer` 一致。完整步骤、升级卸载与失败排查见 [docs/install.md](docs/install.md)。

### 4.1 TRAE 项目级安装（推荐）

先获取仓库，得到 `prd-skill` 目录：

```bash
git clone https://github.com/zyzynzs1/prd-skill.git
```

在**目标项目根目录**执行（路径使用正斜杠）：

```powershell
# Windows（PowerShell）
New-Item -ItemType Directory -Force -Path ./.trae/skills/prd-writer | Out-Null
Copy-Item -Path ./prd-skill/prd-writer/* -Destination ./.trae/skills/prd-writer -Recurse -Force
```

```bash
# macOS / Linux
mkdir -p .trae/skills/prd-writer
cp -R prd-skill/prd-writer/. .trae/skills/prd-writer/
```

重复执行上述命令只会覆盖同名文件，不会产生 `prd-writer/prd-writer/` 嵌套目录。安装后 `.trae/skills/prd-writer/` 下应直接看到 `SKILL.md`、`templates/`、`references/`、`examples/`、`scripts/`。项目级技能随仓库提交后，团队成员克隆项目即可使用。

### 4.2 TRAE 全局级安装

| 系统 | 全局技能目录 |
|------|--------------|
| Windows | `%userprofile%/.trae-cn/skills/prd-writer/` |
| macOS / Linux | `~/.trae-cn/skills/prd-writer/` |

将 `prd-writer/` 复制到上表对应目录即可。国际版客户端的全局目录以「设置 > 技能与命令」页面实际显示为准；同名技能同时存在时，项目级 `.trae/skills/` 优先。

### 4.3 其他客户端

| 客户端 | 项目级技能目录 | 用户级技能目录 |
|--------|----------------|----------------|
| 通用 `.agents`（TRAE、Cursor、Codex、Gemini CLI 等） | `.agents/skills/prd-writer/` | `~/.agents/skills/prd-writer/` |
| Claude Code | `.claude/skills/prd-writer/` | `~/.claude/skills/prd-writer/` |
| Cursor | `.cursor/skills/prd-writer/` | `~/.cursor/skills/prd-writer/` |

TRAE 使用 `.agents/skills/` 前需在「设置 > 技能与命令 > 导入设置」中开启「启用 .agents 技能目录」。Claude Code 不读取 `.agents/skills/`，可建立符号链接或直接复制。

### 4.4 zip 打包与导入

通过 TRAE 的创建/导入窗口或 TraeWork 上传技能时，压缩包解压后 **`SKILL.md` 必须直接位于根级**，不能出现 `prd-writer/SKILL.md` 这样多套一层。

```powershell
# Windows：在仓库根目录执行，让目录内容位于压缩包根级
Compress-Archive -Path ./prd-writer/* -DestinationPath ./prd-writer.zip -Force
```

```bash
# macOS / Linux：在仓库根目录执行
cd prd-writer && zip -r ../prd-writer.zip SKILL.md templates references examples scripts && cd ..
```

直接压缩整个 `prd-writer` 文件夹，或直接上传 GitHub 下载的仓库归档，都会多套一层导致导入失败。先解压，再按上述命令重新打包。TraeWork 还接受扩展名为 `.skill` 的文件，把 zip 改名即可。

## 5. 快速开始

**第 1 步：安装技能。** 按第 4 节把 `prd-writer/` 放进客户端技能目录。

**第 2 步：在目标代码仓库中打开会话**，用一句话说明要做什么。例如：

> 用 prd-writer 技能给这个仓库补一份 PRD，覆盖整个后台管理系统，版本 V1.0，读者是研发和 UI。

**第 3 步：核对功能盘点并确认骨架**，然后按技能提示继续。产物默认输出到 `docs/prd/`。

示例对话（节选）：

```text
用户：用 prd-writer 技能给这个仓库补一份 PRD，版本 V1.0，读者是研发和 UI。

技能：（阶段 0）读取 README 与构建配置，识别技术栈与模块，确认范围、版本、读者三个问题。
      （阶段 1）扫描路由、页面、接口、数据模型，输出功能盘点表，每条带代码证据与置信度，
              请你增删改功能范围。

用户：订单模块的「批量导出」本期不做，其他可以。

技能：（阶段 2–3）补问代码中拿不到的信息（一次不超过 5 个），提交功能清单、迭代规划、
      功能框架图草图请你确认。
      （阶段 4–6）按迭代起草正文，逐项过质量门禁并运行校验脚本，按交付指南转 Word 后打开。
```

只想先看范围时，可以说：

> 先只梳理这个仓库的功能点，不要写正文。

此时技能只执行功能盘点，输出功能清单、建议迭代划分与待确认清单。

## 6. 工作流与五种模式

技能先判断要做哪一种事，再按对应模式执行；用户未说明时默认按模式 A。

| 模式 | 用户说法示例 | 输入 | 主要输出 | 可跳过的阶段 |
|------|--------------|------|----------|--------------|
| A 完整生成 | 「给这个仓库补个 PRD」 | 代码仓库 | 功能盘点 + 完整 PRD（Markdown 转 Word） | 无 |
| B 增量更新 | 「只更新 1.2 的限制条件，其他不变」 | 已有 PRD + 代码 | 变更小节 + 修订记录 | 阶段 0、阶段 2 中无关问题 |
| C 评审 | 「评审这份 PRD」「看看还缺什么」 | 已有 PRD（可选代码） | 评审报告（问题表 + 结论） | 阶段 3、4 |
| D 仅功能盘点 | 「先梳理功能点，不要写正文」 | 代码仓库 | `功能盘点.md` | 阶段 3–6 |
| E 测试用例 | 「生成迭代 1 的测试用例」 | 已有 PRD 正文 | 测试用例表（嵌入 Excel） | 阶段 0–3 |

多模式可以组合，一次只推进一个模式，完成后再进入下一个。

工作流各阶段的产物：

| 阶段 | 目标 | 产物 |
|------|------|------|
| 0 范围确认 | 圈定文档边界 | 范围摘要（写哪个产品/模块、版本号、目标读者） |
| 1 功能盘点 | 把代码翻译成功能清单 | `功能盘点-{产品/模块}.md`，含代码证据与置信度 |
| 2 访谈补全 | 补代码里拿不到的信息 | 访谈记录（并入 PRD「文档说明」） |
| 3 骨架确认 | 与用户对齐结构 | 确认后的功能清单、迭代规划、功能框架图草图 |
| 4 分迭代起草 | 产出 PRD 正文 | PRD Markdown 草稿 |
| 5 自查与门禁 | 交付前兜底 | 自检通过记录（含校验脚本报告） |
| 6 交付 | 转成交付物 | `.docx` + `.md` |

详细流程与完成判据以 [prd-writer/SKILL.md](prd-writer/SKILL.md) 为准。

## 7. 质量门禁与校验脚本

### 7.1 质量门禁（G1–G9）

| 编号 | 门禁项 | 通过标准 |
|------|--------|----------|
| G1 | 结构完整 | 章节齐全、编号与模板一致，无自创层级 |
| G2 | 功能一致 | 功能清单、功能框架图、正文三处功能数量与命名完全一致 |
| G3 | 字段齐全 | 每个子功能 9 个字段齐全、顺序正确、无空字段 |
| G4 | 编号规范 | 「具体说明」编号符合 N. / N.M / N.M.K / N.M.K.L，缩进与连续性正确 |
| G5 | 证据充分 | 每个功能可追溯到功能盘点；无来源内容在正文对应位置标【待确认】并在 Word 中红色显示（不设附录汇总表） |
| G6 | 交互深度 | 按钮、列表、表单、状态均写明交互后效果、作用范围、生效时机 |
| G7 | 可测性 | 生成测试用例时，叶子条目与限制条件 100% 有覆盖用例 |
| G8 | 交付格式 | Word 中框架图为图片、测试用例为嵌入 Excel、序号为自动多级编号 |
| G9 | 语言与占位 | 无字面量 HTML 实体、无模板占位残留、无口语与营销话术 |

门禁由技能在阶段 5 逐项执行，修复循环不超过 3 轮；仍有未通过项时须在交付说明中如实列出。

### 7.2 校验脚本

`prd-writer/scripts/validate_prd.py` 覆盖 G1–G5、G9 中可机械判断的部分。运行需要 Python 3.8+，只使用标准库。

```bash
# 校验 PRD Markdown
python prd-writer/scripts/validate_prd.py docs/prd/PRD-在线考试系统-V1.0.md

# 校验技能文件本身（frontmatter、行数、引用路径）
python prd-writer/scripts/validate_prd.py --skill prd-writer/SKILL.md

# WARN 也视为失败，适合交付前严格自检
python prd-writer/scripts/validate_prd.py --strict docs/prd/PRD-在线考试系统-V1.0.md

# JSON 输出，便于接入其他工具
python prd-writer/scripts/validate_prd.py --json docs/prd/PRD-在线考试系统-V1.0.md
```

退出码：`0` 表示未发现 ERROR（`--strict` 时还需无 WARN），`1` 表示存在失败项，`2` 表示用法或文件错误。报告按 ERROR、WARN、INFO 分级并给出行号。

需要明确的是：**脚本只做结构与一致性检查，不判断内容质量**。业务正确性、交互描述是否充分、证据是否真实，仍需按 [prd-writer/references/quality-checklist.md](prd-writer/references/quality-checklist.md) 人工核对。

## 8. 示例与产物

`prd-writer/examples/` 下提供两个示例，基于虚构的「在线考试系统」项目：

| 文件 | 说明 |
|------|------|
| [prd-writer/examples/PRD-示例-在线考试系统.md](prd-writer/examples/PRD-示例-在线考试系统.md) | 精简 PRD 示例，可用于运行校验脚本 |
| [prd-writer/examples/功能盘点-示例.md](prd-writer/examples/功能盘点-示例.md) | 功能盘点示例，含代码证据、置信度、待确认清单与建议迭代划分 |

```bash
# 用示例验证校验脚本可正常运行
python prd-writer/scripts/validate_prd.py prd-writer/examples/PRD-示例-在线考试系统.md
```

示例说明与自测方法见 [prd-writer/examples/README.md](prd-writer/examples/README.md)。

默认产物与命名：

| 产物 | 命名 | 建议位置 |
|------|------|----------|
| 功能盘点 | `功能盘点-{产品/模块}.md` | `docs/prd/` |
| PRD 草稿 | `PRD-{产品/模块}-V{x.y}.md` | `docs/prd/` |
| PRD 交付 | `PRD-{产品/模块}-V{x.y}.docx` | `docs/prd/` |
| 测试用例附件 | 由交付环节内嵌，不单独命名 | 嵌入 PRD Word 内 |

Word 交付说明：仓库**不包含**把 Markdown 一键导出为 docx 的脚本。Word 交付按 [prd-writer/references/delivery-guide.md](prd-writer/references/delivery-guide.md) 中记录的流程与工具链执行（例如 pandoc、python-docx、docxtpl、Word / WPS COM），自动多级编号、框架图渲染与嵌入 Excel 均在该指南中给出做法与降级方案；本机缺少工具时按指南的替代步骤操作，不会静默降级。

## 9. 常见问题

**Q1：必须用 TRAE 吗？其他客户端能用吗？**

不必须。技能遵循 Agent Skills 开放标准，可安装到 TRAE、Claude Code、Cursor，也可放到多客户端通用的 `.agents/skills/`。见 [docs/install.md](docs/install.md)。

**Q2：为什么必须先做功能盘点，不能直接写正文？**

功能盘点是 PRD 的证据来源，也是与用户对齐功能范围的抓手。跳过盘点直接写正文容易编造功能。用户明确要求快速出草稿时，技能会在草稿中标注假设。

**Q3：代码里找不到依据的内容怎么处理？**

统一在正文对应位置标注【待确认：待补信息/建议确认人】，禁止编造数据、时间、人名、指标；Word 交付时该处以红色显示，不设附录 A 汇总表、无需读者跳转回查。

**Q4：技能会自动生成 Word 文档吗？**

交付目标是 Word，但仓库没有一键导出脚本。技能按 `prd-writer/references/delivery-guide.md` 的流程完成转换，需要本机具备相应工具（如 pandoc、python-docx、docxtpl、Word / WPS COM）；工具缺失时会说明并给出替代步骤。

**Q5：校验脚本能保证文档质量吗？**

不能。脚本只检查结构、字段、编号、数量一致性与占位符，不判断业务是否正确、交互描述是否充分。内容质量需按 `prd-writer/references/quality-checklist.md` 人工核对。

**Q6：测试用例为什么默认不生成？**

demo 未定型时功能细节可能变化，提前生成会返工。PRD 先保留附件位，用户明确要求后再按迭代生成。

**Q7：生成内容太长被截断怎么办？**

技能会主动按迭代或大功能点分段，段尾标注「回复『继续』生成下一段」。同一会话内回复「继续」；换会话时提供已有文件路径与断点位置，技能从断点续写，不重写已完成部分。

**Q8：已有 PRD 只想改某一节怎么办？**

使用增量更新模式，说明要改的位置与内容。技能只输出变更后的小节并追加修订记录，不重写未涉及的章节；涉及功能点增删时才同步更新功能清单与功能框架图。

**Q9：技能会修改业务代码吗？**

不会。技能只读取代码作为证据，产出为 PRD 相关文档；除用户明确要求写入的文档外，不修改仓库代码。

**Q10：如何在 Windows 上正常使用？**

安装与命令中的路径统一使用正斜杠 `/`；`SKILL.md` 用 UTF-8 无 BOM 保存；校验脚本若输出中文乱码，先在 PowerShell 执行 `chcp 65001`。

**Q11：如何确认版本？**

查看 `prd-writer/SKILL.md` 的 frontmatter 版本、[CHANGELOG.md](CHANGELOG.md) 与本文档的版本说明，当前统一为 `2.0.0`。

## 10. 版本与变更

当前版本 `2.0.0`（2026-10-26），将技能从单份 `SKILL.md` 升级为按 Agent Skills 规范组织的可发布技能：新增五种模式、七阶段工作流、功能盘点与代码证据规则、评审与交付指南、9 条质量门禁、结构校验脚本、示例与发布配套文档，并修正目录结构与格式问题。

早期版本（`1.0.0`–`1.8.1`，2026-09-15 至 2026-10-10）为技能初版与多轮迭代，未单独维护变更记录。

完整变更见 [CHANGELOG.md](CHANGELOG.md)。

## 11. 贡献

欢迎提交 Issue 与 Pull Request。修改时请遵循以下约定：

1. 修改 `prd-writer/` 下的技能内容前，先阅读 `prd-writer/SKILL.md`，保持术语一致：大功能点、子功能、具体说明、限制条件、迭代、功能盘点、质量门禁、待确认。
2. 新增或重命名 `prd-writer/references/` 文件时，同步更新 `SKILL.md` 第 9 节参考文件索引，保证引用为一层深度且路径真实存在。
3. 修改模板或字段规范时，同步检查 `templates/prd-template.md`、`prd-writer/references/field-spec.md` 与校验脚本的字段列表是否一致。
4. 提交前运行校验脚本自检：

   ```bash
   python prd-writer/scripts/validate_prd.py prd-writer/examples/PRD-示例-在线考试系统.md
   python prd-writer/scripts/validate_prd.py --skill prd-writer/SKILL.md
   ```

5. 不提交 `_research/`、`_review/` 等本地临时目录与 `docs/prd/` 下的生成产物；新增能力时同步更新 README、`CHANGELOG.md` 与 `docs/`。
6. 提交的信息与文档使用中文，避免营销话术与感叹号堆砌；不确定的内容标注【待确认】，不编造。

## 12. 许可证

本项目采用 MIT 许可证，版权人 zyzynzs1，年份 2026。详见 [LICENSE](LICENSE)。
