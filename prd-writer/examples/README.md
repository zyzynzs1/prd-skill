# 示例目录说明

本目录提供 prd-writer 技能的示例输出，用于：

1. 展示技能在真实仓库上应产出的文档形态与详细程度；
2. 作为 `prd-writer/scripts/validate_prd.py` 的自测 fixture；
3. 供评审、培训、二次开发时对照参考。

示例基于虚构的「在线考试系统」项目，仓库名、提交号、业务数据均为演示用途，不代表真实项目。**示例不是模板**：正式生成 PRD 时必须以 `prd-writer/templates/prd-template.md` 的章节骨架、字段顺序与编号规则为准，不得照搬示例中的具体业务内容。

## 1. 文件清单

| 文件 | 内容 | 对应技能阶段 | 能否用 PRD 校验脚本 |
|------|------|--------------|---------------------|
| `PRD-示例-在线考试系统.md` | 精简 PRD 示例：产品需求背景、通用设计机制、迭代1 的功能详述、附录 A、待确认清单 | 阶段 3–5（骨架确认、起草、自查） | 可以 |
| `功能盘点-示例.md` | 功能盘点示例：功能清单（含代码证据与置信度）、角色与权限、待确认清单、建议迭代划分 | 阶段 1（功能盘点） | 不可以，见第 3 节 |

两个示例互为上下游：`功能盘点-示例.md` 是 `PRD-示例-在线考试系统.md` 的依据。迭代1 范围内的 5 个子功能（课程列表、课程编辑弹窗、课程状态切换、在线作答页、交卷确认）在两个示例中一一对应，可用于核对「功能清单、功能框架图、正文」三方一致性；「成绩统计」为低置信度待定项，未纳入 PRD，符合 `prd-writer/references/code-analysis-guide.md` 的置信度规则。

> 说明：示例的测试用例仅演示 8 列表头、场景类型与追溯写法，**未覆盖**全部「具体说明」叶子条目与「限制条件」，不满足 G7 全覆盖门禁；正式交付必须按 `prd-writer/references/testcase-spec.md` 补齐，不能以示例为覆盖率标准。

## 2. 用 PRD 示例跑校验脚本

在仓库根目录执行：

```bash
# 基本校验（在仓库根目录执行）
python prd-writer/scripts/validate_prd.py prd-writer/examples/PRD-示例-在线考试系统.md

# JSON 输出
python prd-writer/scripts/validate_prd.py --json prd-writer/examples/PRD-示例-在线考试系统.md

# 隐藏 INFO 信息
python prd-writer/scripts/validate_prd.py --quiet prd-writer/examples/PRD-示例-在线考试系统.md
```

当前示例的运行结果：

- ERROR 与 WARN 均为 0，退出码 0，结论为「通过」；
- 输出含 3 条 INFO：待确认条数统计、`yyyy-mm-dd` 格式说明提示（来自「数据格式约定」，不是日期残留）、测试用例表数量；
- 因无 WARN，`--strict` 也能通过；JSON 输出中的 `"passed": true` 表示未发现 ERROR。需要 Python 3.8+，脚本只使用标准库。

## 3. 不要用 PRD 模式校验功能盘点示例

`功能盘点-示例.md` 是阶段 1 的过程产物，不是 PRD，缺少「产品需求背景」「通用设计机制」「功能详细描述」等章节。用 `validate_prd.py` 校验它必然报多个 ERROR（缺少一级章节、缺少修订记录表、缺少功能清单表等），这是预期结果，不是示例或脚本的问题。

功能盘点的质量应按 `prd-writer/references/code-analysis-guide.md` 人工核对：每个子功能是否登记了代码证据（`文件路径:行号` 或符号名）、置信度是否合理、低置信度项是否进入待确认清单、建议迭代划分是否与功能依赖一致。

## 4. 用示例验证校验脚本的报错能力

如需确认校验脚本能识别结构错误，可复制 PRD 示例到临时文件后故意破坏结构，例如删除某个子功能的「限制条件」字段、改乱「具体说明」编号、删掉附录 A。再次运行脚本应报 ERROR 并给出行号；验证完成后删除临时文件，不要提交。

## 5. 相关文件

- 技能入口与完整规则：`prd-writer/SKILL.md`
- PRD 固定模板：`prd-writer/templates/prd-template.md`
- 字段写法与「具体说明」细化标准：`prd-writer/references/field-spec.md`
- 代码分析与功能盘点规范：`prd-writer/references/code-analysis-guide.md`
- 质量检查清单：`prd-writer/references/quality-checklist.md`
- 安装与使用说明：`docs/install.md`、`docs/usage.md`
