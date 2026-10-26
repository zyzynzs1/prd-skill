# 安装指南

本技能遵循 Agent Skills 开放标准，安装的本质是：把仓库中的 `prd-writer/` 目录放到客户端会扫描的技能目录下，并保证目录名与 `SKILL.md` frontmatter 中的 `name` 一致（均为 `prd-writer`）。

- 技能入口：`prd-writer/SKILL.md`，必须是技能目录下的直接子文件。
- 技能版本：2.0.0。以 `prd-writer/SKILL.md` 的 frontmatter 为准，变更说明见 [CHANGELOG.md](../CHANGELOG.md)。
- 运行依赖：日常使用不需要额外依赖；仅运行校验脚本时需要 Python 3.8+，脚本只使用标准库。
- 技能只读取目标仓库的代码，不会修改业务代码；产出为 PRD 相关文档。

下文 §3–§6 的安装命令均相对于「目标项目根目录」执行；§7 打包与 §9 升级命令在技能仓库（`prd-skill/`）根目录执行，相关小节会单独标注。`prd-skill` 指本仓库克隆后的目录名。

## 1. 安装前准备

获取技能文件（二选一）：

```bash
# 方式一：克隆仓库
git clone https://github.com/zyzynzs1/prd-skill.git

# 方式二：在 GitHub 页面下载 ZIP 并解压，得到 prd-skill-main 目录
```

安装使用的来源目录是 `prd-skill/prd-writer/`。不要把整个仓库根目录当作技能目录，也不要让 `SKILL.md` 多套一层目录。若仓库克隆在其他位置，把下文命令中的 `./prd-skill` 或 `prd-skill` 替换为实际路径。

## 2. 技能目录结构（安装后校验用）

安装完成后，技能目录应包含以下文件；缺少 `templates/`、`references/`、`examples/`、`scripts/` 时技能仍可加载，但起草、审查、交付环节会退回 `SKILL.md` 内的摘要规则，能力受限。

```text
prd-writer/
├── SKILL.md
├── templates/
│   └── prd-template.md
├── references/
│   ├── code-analysis-guide.md
│   ├── delivery-guide.md
│   ├── field-spec.md
│   ├── interview-guide.md
│   ├── quality-checklist.md
│   ├── review-guide.md
│   └── testcase-spec.md
├── examples/
│   ├── README.md
│   ├── PRD-示例-在线考试系统.md
│   └── 功能盘点-示例.md
└── scripts/
    └── validate_prd.py
```

## 3. TRAE 安装（推荐）

### 3.1 项目级安装（推荐）

将技能目录复制到目标项目的 `.trae/skills/prd-writer/`。项目级技能随仓库提交后，团队成员克隆项目即可获得。

Windows（PowerShell，在目标项目根目录执行）：

```powershell
New-Item -ItemType Directory -Force -Path ./.trae/skills/prd-writer | Out-Null
Copy-Item -Path ./prd-skill/prd-writer/* -Destination ./.trae/skills/prd-writer -Recurse -Force
```

macOS / Linux（在目标项目根目录执行）：

```bash
mkdir -p .trae/skills/prd-writer
cp -R prd-skill/prd-writer/. .trae/skills/prd-writer/
```

校验目录层级：

```powershell
# Windows
Get-ChildItem ./.trae/skills/prd-writer | Select-Object -ExpandProperty Name
```

```bash
# macOS / Linux
ls .trae/skills/prd-writer
```

输出中应直接看到 `SKILL.md`、`templates`、`references`、`scripts`。

### 3.2 全局级安装（所有项目可用）

全局级技能对当前用户的所有项目生效，适合个人长期使用。

| 系统 | 全局技能目录 |
|------|--------------|
| Windows | `%userprofile%/.trae-cn/skills/prd-writer/` |
| macOS / Linux | `~/.trae-cn/skills/prd-writer/` |

Windows（PowerShell）：

```powershell
New-Item -ItemType Directory -Force -Path "$env:userprofile/.trae-cn/skills/prd-writer" | Out-Null
Copy-Item -Path ./prd-skill/prd-writer/* -Destination "$env:userprofile/.trae-cn/skills/prd-writer" -Recurse -Force
```

macOS / Linux：

```bash
mkdir -p ~/.trae-cn/skills/prd-writer
cp -R prd-skill/prd-writer/. ~/.trae-cn/skills/prd-writer/
```

说明：

- 中国版 TRAE 的全局目录为 `~/.trae-cn/skills`；国际版客户端若显示不同的全局目录，以「设置 > 技能与命令」页面实际展示的路径为准。
- 同名技能同时存在于项目级与全局级时，项目级 `.trae/skills/` 优先。

### 3.3 IDE 导入（不复制目录时）

1. 在 TRAE 中打开目标项目。
2. 进入「设置 > 技能与命令 > 技能」，点击「创建」。
3. 选择作用域（项目 / 全局），在创建窗口顶部使用上传入口：
   - 上传单个 `prd-writer/SKILL.md`；或
   - 上传一个包含根级 `SKILL.md` 的 `.zip` 压缩包。
4. TRAE 会解析并自动回填名称、描述与指令，确认名称为 `prd-writer` 后保存。

注意：单文件导入只带入 `SKILL.md` 正文，`templates/`、`references/`、`examples/`、`scripts/` 不会随之导入。需要在导入后把其余文件手工放入对应技能目录，否则请改用「复制整个目录」的方式安装。

## 4. Agent 通用安装（`.agents/skills/`）

`.agents/skills/` 是多个客户端共同读取的通用技能目录（TRAE、Cursor、Codex、Gemini CLI、GitHub Copilot、OpenCode 等）。如果团队内同时使用多个 Agent 客户端，优先采用这一方式。

| 作用域 | 路径 |
|--------|------|
| 项目级 | `<目标项目>/.agents/skills/prd-writer/` |
| 用户级 | `~/.agents/skills/prd-writer/`（Windows 为 `%userprofile%/.agents/skills/prd-writer/`） |

Windows（PowerShell，在目标项目根目录执行）：

```powershell
New-Item -ItemType Directory -Force -Path ./.agents/skills/prd-writer | Out-Null
Copy-Item -Path ./prd-skill/prd-writer/* -Destination ./.agents/skills/prd-writer -Recurse -Force
```

macOS / Linux（在目标项目根目录执行）：

```bash
mkdir -p .agents/skills/prd-writer
cp -R prd-skill/prd-writer/. .agents/skills/prd-writer/
```

TRAE 使用该目录前需要开启开关：「设置 > 技能与命令 > 导入设置 > 启用 .agents 技能目录」。

Claude Code 不读取 `.agents/skills/`。如需共用同一份技能，可建立符号链接（Windows 建符号链接需要开发者模式或管理员权限，也可改为直接复制）：

```bash
# macOS / Linux，在目标项目根目录执行
mkdir -p .claude/skills
ln -s ../../.agents/skills/prd-writer .claude/skills/prd-writer
```

## 5. Claude Code 安装

| 作用域 | 路径 |
|--------|------|
| 项目级（随仓库共享） | `.claude/skills/prd-writer/` |
| 个人级（当前用户所有项目） | `~/.claude/skills/prd-writer/` |

Windows（PowerShell，在目标项目根目录执行）：

```powershell
New-Item -ItemType Directory -Force -Path ./.claude/skills/prd-writer | Out-Null
Copy-Item -Path ./prd-skill/prd-writer/* -Destination ./.claude/skills/prd-writer -Recurse -Force
```

macOS / Linux：

```bash
mkdir -p .claude/skills/prd-writer
cp -R prd-skill/prd-writer/. .claude/skills/prd-writer/
```

安装后在会话中描述任务即可由模型自动调用；也可以在消息中直接点名「使用 prd-writer 技能」。

## 6. Cursor 安装

| 作用域 | 路径 |
|--------|------|
| 项目级 | `.cursor/skills/prd-writer/` |
| 用户级 | `~/.cursor/skills/prd-writer/` |

Cursor 同时会读取项目级 `.agents/skills/`、`.claude/skills/`、`.codex/skills/`，以及用户级 `~/.agents/skills/`、`~/.claude/skills/`、`~/.codex/skills/`。因此已按第 4 节安装到 `.agents/skills/` 时，通常无需在 Cursor 中重复安装。

复制目录的命令与第 3.1 节相同，只需把目标路径换成 `.cursor/skills/prd-writer`：

```powershell
# Windows
New-Item -ItemType Directory -Force -Path ./.cursor/skills/prd-writer | Out-Null
Copy-Item -Path ./prd-skill/prd-writer/* -Destination ./.cursor/skills/prd-writer -Recurse -Force
```

```bash
# macOS / Linux
mkdir -p .cursor/skills/prd-writer
cp -R prd-skill/prd-writer/. .cursor/skills/prd-writer/
```

在 Cursor 中通过 `/` 选择技能，或直接用自然语言描述任务。

## 7. zip 打包与导入要求

技能的分发单位是一个目录。打包时最容易出错的地方是压缩包层级：解压后 **`SKILL.md` 必须直接位于压缩包根级**，不能出现 `prd-writer/SKILL.md` 这样多套一层。

Windows（PowerShell，在仓库根目录执行，注意 `*` 让内容位于压缩包根级）：

```powershell
Compress-Archive -Path ./prd-writer/* -DestinationPath ./prd-writer.zip -Force
```

macOS / Linux（在仓库根目录执行）：

```bash
cd prd-writer && zip -r ../prd-writer.zip SKILL.md templates references scripts && cd ..
```

打包后检查压缩包内容：第一层条目应包含 `SKILL.md`、`templates/`、`references/`、`scripts/`。若第一层只有 `prd-writer/`，说明多套了一层，导入会被拒绝或解析失败。

常见错误：直接右键压缩整个 `prd-writer` 文件夹；或直接上传 GitHub 下载的仓库归档 `prd-skill-main.zip`。这两种包的第一层都不是 `SKILL.md`。正确做法是先解压，再进入 `prd-writer` 目录，按上面的命令重新打包其内容。

TRAE 的 Agent 窗口 / Web 端（TraeWork）同样要求 zip 或 `.skill` 文件，且 `SKILL.md` 位于根级、包含 YAML 格式的 `name` 与 `description`。把 zip 的扩展名改为 `.skill` 即可作为 `.skill` 文件上传。

## 8. 如何确认技能已加载

1. 在客户端的技能列表中应出现 `prd-writer`，描述包含「PRD」「产品需求文档」等关键词。
2. 做一次冒烟对话，例如：

   > 用 prd-writer 技能先对这个仓库做功能盘点，只输出功能盘点，不要写正文。

   预期行为：先读取仓库 README 与构建配置，再按路由、页面、接口、数据模型登记功能点，输出带代码证据与置信度的功能盘点表；而不是直接开始写文档。

3. 反向验证（不应触发）：询问「帮我写一段产品宣传文案」，技能不应被加载或不应按 PRD 流程执行。
4. 文件级自检（需要 Python）：在本仓库根目录执行以下命令，退出码 0 表示未发现 ERROR。

   ```bash
   python prd-writer/scripts/validate_prd.py --skill prd-writer/SKILL.md
   ```

   安装到目标项目后，把路径换成实际技能目录，例如 `python .trae/skills/prd-writer/scripts/validate_prd.py --skill .trae/skills/prd-writer/SKILL.md`。

5. 版本确认：查看 `prd-writer/SKILL.md` 的 frontmatter 与仓库的 `CHANGELOG.md`，版本应为 `2.0.0`。

## 9. 升级

技能升级会覆盖技能目录内的全部文件。如果本地修改过 `SKILL.md` 或 `references/`，先备份再升级。

```bash
# 1. 更新仓库
cd prd-skill && git pull
```

```powershell
# 2. Windows：删除旧目录后重新复制（在目标项目根目录执行）
Remove-Item -Recurse -Force ./.trae/skills/prd-writer
Copy-Item -Path ./prd-skill/prd-writer -Destination ./.trae/skills/prd-writer -Recurse -Force
```

```bash
# 2. macOS / Linux：删除旧目录后重新复制（在目标项目根目录执行）
rm -rf .trae/skills/prd-writer
cp -R prd-skill/prd-writer .trae/skills/prd-writer
```

升级完成后新建会话或重启 IDE。若使用 IDE 导入方式安装，请在「设置 > 技能与命令」中删除旧技能后重新导入。

## 10. 卸载

1. 删除技能目录，例如：

   ```powershell
   # Windows
   Remove-Item -Recurse -Force ./.trae/skills/prd-writer
   ```

   ```bash
   # macOS / Linux
   rm -rf .trae/skills/prd-writer
   ```

2. 若通过 IDE 导入或插件市场安装，在「设置 > 技能与命令 > 技能」中删除对应的自定义技能。
3. 新建会话或重启 IDE 使变更生效。

卸载不会影响目标项目的业务代码，也不会删除已经生成的 PRD 文档。

## 11. 常见安装失败排查

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| 技能列表中没有 `prd-writer` | 目录多套了一层，如 `.trae/skills/prd-writer/prd-writer/SKILL.md` | 保证 `SKILL.md` 是 `.trae/skills/prd-writer/` 的直接子文件 |
| 技能出现但名称异常或无法触发 | 目录名与 frontmatter 的 `name` 不一致；`SKILL.md` 首行不是 `---`，或文件带 BOM | 目录统一命名为 `prd-writer`；`---` 必须是文件第一行；用 UTF-8 无 BOM 保存 |
| `.agents/skills/` 方式不生效 | TRAE 未开启「启用 .agents 技能目录」 | 在「设置 > 技能与命令 > 导入设置」中打开开关 |
| 上传 zip 失败或解析出空技能 | 压缩包第一层不是 `SKILL.md`，而是 `prd-writer/` | 按第 7 节重新打包目录内容 |
| 技能能回答但从不读取 `references/` | 附加文件缺失、路径大小写不一致，或只导入了单个 `SKILL.md` | 按第 2 节核对目录结构；大小写保持一致 |
| 同一个技能出现两条 | 项目级与全局级同时安装，或同时存在于 `.trae/skills/` 与 `.agents/skills/` | 保留一处；TRAE 优先使用 `.trae/skills/` |
| 修改了技能内容但不生效 | 客户端缓存或旧会话仍在使用旧版本 | 新建会话；IDE 方式安装的重新导入 |
| 校验脚本报「文件不存在」 | 命令不在仓库根目录执行，或路径写错 | 在仓库根目录执行；路径使用正斜杠 `/`，不要用 Windows 反斜杠 |
| 校验脚本中文输出乱码 | Windows 终端代码页与 UTF-8 不一致 | PowerShell 先执行 `chcp 65001`，或改用 Windows Terminal |
| `python` 命令不可用 | 未安装 Python 或未加入 PATH | 安装 Python 3.8+ 后重试；仅使用技能本身时不依赖 Python |

## 12. 路径速查表

| 客户端 | 项目级技能目录 | 用户级（全局）技能目录 |
|--------|----------------|------------------------|
| TRAE / TraeCode | `.trae/skills/prd-writer/` | Windows：`%userprofile%/.trae-cn/skills/prd-writer/`；macOS / Linux：`~/.trae-cn/skills/prd-writer/` |
| 通用 `.agents` | `.agents/skills/prd-writer/` | `~/.agents/skills/prd-writer/` |
| Claude Code | `.claude/skills/prd-writer/` | `~/.claude/skills/prd-writer/` |
| Cursor | `.cursor/skills/prd-writer/` | `~/.cursor/skills/prd-writer/` |

安装完成后，回到 [README.md](../README.md) 的「快速开始」一节开始使用，或查阅 [使用指南](usage.md)。
